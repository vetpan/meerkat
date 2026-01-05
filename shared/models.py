"""
Meerkat Intelligence - Database Models

Target: Websites die we monitoren (competitors)
Scan: Individuele scan resultaten met screenshots en analyses
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Target(models.Model):
    """
    Een target is een website die we monitoren op commerciële wijzigingen.
    
    Bijvoorbeeld: Ziggo, Odido, KPN internetpagina's
    """
    
    # Later toevoegen voor multi-user support (nullable voor MVP)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Basis informatie
    name = models.CharField(
        max_length=200,
        help_text="Naam van de concurrent (bijv. 'Ziggo')"
    )
    url = models.URLField(
        max_length=500,
        help_text="URL om te monitoren (bijv. 'https://ziggo.nl/internet')"
    )
    
    # Scan configuratie
    INTERVAL_CHOICES = [
        (5, '5 minuten'),
        (15, '15 minuten'),
        (30, '30 minuten'),
        (60, '1 uur'),
    ]
    interval = models.IntegerField(
        choices=INTERVAL_CHOICES,
        default=15,
        help_text="Hoe vaak scannen we deze target?"
    )
    
    STATUS_CHOICES = [
        ('active', 'Actief'),
        ('paused', 'Gepauzeerd'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Is deze target actief?"
    )
    
    # Scan state
    last_hash = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        help_text="MD5 hash van laatste scan (voor change detection)"
    )
    last_scan_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Wanneer was de laatste scan?"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Target'
        verbose_name_plural = 'Targets'
    
    def __str__(self):
        return f"{self.name} ({self.url})"
    
    def should_scan(self):
        """
        Moet deze target nu gescand worden?
        True als: actief EN (nog nooit gescand OF interval verstreken)
        """
        if self.status != 'active':
            return False
        
        if not self.last_scan_at:
            return True  # Nog nooit gescand
        
        # Check of interval verstreken is
        time_since_scan = timezone.now() - self.last_scan_at
        interval_seconds = self.interval * 60
        
        return time_since_scan.total_seconds() >= interval_seconds
    
    def next_scan_at(self):
        """Wanneer is de volgende scan gepland?"""
        if not self.last_scan_at:
            return timezone.now()
        
        from datetime import timedelta
        return self.last_scan_at + timedelta(minutes=self.interval)


class Scan(models.Model):
    """
    Een scan representeert één check van een target.
    
    Bevat: screenshot, hash, Gemini analyse, status
    """
    
    target = models.ForeignKey(
        Target,
        on_delete=models.CASCADE,
        related_name='scans',
        help_text="Welke target is gescand?"
    )
    
    # Screenshot
    screenshot_path = models.CharField(
        max_length=500,
        help_text="Pad naar screenshot bestand (bijv. '/storage/screenshots/abc123.png')"
    )
    
    # Content hash voor change detection
    content_hash = models.CharField(
        max_length=32,
        help_text="MD5 hash van pagina content (tekst + image URLs)"
    )
    
    # Gemini AI analyse (als JSON)
    analysis_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Gestructureerde analyse van Gemini (type, title, summary, etc.)"
    )
    
    # Status tracking
    STATUS_CHOICES = [
        ('pending', 'Bezig'),
        ('success', 'Succesvol'),
        ('failed', 'Mislukt'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Status van deze scan"
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error bericht als scan is mislukt"
    )
    
    # Metadata
    scanned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Wanneer is deze scan uitgevoerd?"
    )
    
    class Meta:
        ordering = ['-scanned_at']
        verbose_name = 'Scan'
        verbose_name_plural = 'Scans'
        indexes = [
            models.Index(fields=['-scanned_at']),
            models.Index(fields=['target', '-scanned_at']),
        ]
    
    def __str__(self):
        return f"Scan #{self.id} - {self.target.name} ({self.status})"
    
    def is_change_detected(self):
        """
        Was deze scan een wijziging?
        True als de hash anders is dan de vorige scan
        """
        previous_scan = Scan.objects.filter(
            target=self.target,
            scanned_at__lt=self.scanned_at,
            status='success'
        ).first()
        
        if not previous_scan:
            return True  # Eerste scan = altijd wijziging
        
        return self.content_hash != previous_scan.content_hash
    
    @property
    def analysis_type(self):
        """Shortcut naar analyse type (critical/stable)"""
        if self.analysis_json:
            return self.analysis_json.get('type', 'unknown')
        return None
    
    @property
    def analysis_title(self):
        """Shortcut naar analyse titel"""
        if self.analysis_json:
            return self.analysis_json.get('title', 'Geen titel')
        return 'Geen analyse beschikbaar'


class Alert(models.Model):
    """
    Houdt bij welke alerts verstuurd zijn.
    We willen niet dubbel emailen over dezelfde scan.
    """
    scan = models.OneToOneField(Scan, on_delete=models.CASCADE, related_name='alert')
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient = models.EmailField()
    
    STATUS_CHOICES = [
        ('sent', 'Verzonden'),
        ('failed', 'Mislukt'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'

    def __str__(self):
        return f"Alert voor {self.scan} aan {self.recipient}"

