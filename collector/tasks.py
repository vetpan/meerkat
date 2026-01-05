"""
Celery Tasks voor Background Scanning

Waarom tasks:
- Scans kunnen 30+ seconden duren
- Django HTTP requests moeten binnen 30 sec timeout
- Celery draait apart, kan uren duren

Task flow:
1. Beat scheduler (elke minuut): "Welke targets zijn DUE?"
2. Voor elke DUE target: Start scan_target task
3. scan_target task: Voert full_scan uit
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from shared.models import Target
from collector.scanner.full_scan import perform_full_scan
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from shared.models import Target, Scan, Alert
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def scan_target_task(self, target_id):
    """
    Background task om een target te scannen
    
    Waarom bind=True: We krijgen 'self' voor retry logic
    Waarom max_retries=3: Max 3 pogingen bij failure
    
    Args:
        target_id: ID van target om te scannen
        
    Returns:
        dict met result info
    """
    try:
        result = perform_full_scan(target_id)
        
        # Update last_scan_at
        target = Target.objects.get(id=target_id)
        target.last_scan_at = timezone.now()
        target.save()
        
        if result.get('analysis') and result['analysis'].get('changes'):
            # Check for critical changes
            changes = result['analysis']['changes']
            max_impact = max((c.get('impact_score', 0) for c in changes), default=0)
            
            if max_impact >= 7:
                 # Het is kritiek!
                 scan_id = Scan.objects.filter(target_id=target_id).latest('scanned_at').id
                 send_alert_task.delay(scan_id)

        return {
            'success': True,
            'target_id': target_id,
            'result': result
        }
        
    except Exception as exc:
        # Retry bij failure
        # countdown: Wacht 60 sec voor retry
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_and_scan_targets():
    """
    Check welke targets DUE zijn voor scan
    
    Waarom deze task:
    - Draait elke minuut (via beat schedule)
    - Checkt of target moet gescanned worden
    - Start scan_target_task voor DUE targets
    
    Logic:
    - Target is DUE als: last_scan_at + interval < now
    - Of als: nog nooit gescanned (last_scan_at = None)
    """
    now = timezone.now()
    targets = Target.objects.filter(status='active')
    
    scanned_count = 0
    
    for target in targets:
        # Check of target DUE is
        if target.last_scan_at is None:
            # Nog nooit gescanned -> Scan!
            scan_target_task.delay(target.id)
            scanned_count += 1
            
        else:
            # Check of interval is verstreken
            next_scan_time = target.last_scan_at + timedelta(minutes=target.interval)
            
            if now >= next_scan_time:
                # Tijd voor volgende scan!
                scan_target_task.delay(target.id)
                scanned_count += 1
    
    return {
        'checked': targets.count(),
        'scanned': scanned_count,
        'timestamp': now.isoformat()
    }


@shared_task
def send_alert_task(scan_id):
    """
    Verstuurt email alert voor een kritieke scan.
    """
    try:
        scan = Scan.objects.get(id=scan_id)
        target = scan.target
        
        # Check of al verstuurd
        if hasattr(scan, 'alert'):
            logger.info(f"Alert already sent for scan {scan_id}")
            return
            
        subject = f"🚨 Wijziging: {target.name} ({scan.analysis_title})"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['user@example.com'] # TODO: Make configurable per user
        
        # Render templates
        context = {'scan': scan, 'target': target}
        html_message = render_to_string('emails/alert_email.html', context)
        plain_message = render_to_string('emails/alert_email.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        
        # Track alert
        Alert.objects.create(
            scan=scan,
            recipient=recipient_list[0],
            status='sent'
        )
        logger.info(f"Alert sent for scan {scan_id}")
        
    except Exception as exc:
        logger.error(f"Failed to send alert for scan {scan_id}: {exc}")
        # Track failure if possible, or retry
        if 'scan' in locals():
             Alert.objects.create(
                scan=scan,
                recipient='unknown',
                status='failed'
            )
