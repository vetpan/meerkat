"""
Management command om een target te scannen

Usage:
    python manage.py scan_target <target_id>
    python manage.py scan_target --all
"""

from django.core.management.base import BaseCommand
from shared.models import Target
from collector.scanner.full_scan import perform_full_scan


class Command(BaseCommand):
    help = 'Scan een target voor wijzigingen (Scout + Capture + Gemini)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'target_id',
            nargs='?',
            type=int,
            help='ID van target om te scannen'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Scan alle active targets'
        )
    
    def handle(self, *args, **options):
        if options['all']:
            targets = Target.objects.filter(status='active')
            self.stdout.write(f"🔍 Scanning {targets.count()} active targets...\n")
            for target in targets:
                self.scan_target(target.id)
        elif options['target_id']:
            self.scan_target(options['target_id'])
        else:
            self.stdout.write(
                self.style.ERROR('❌ Geef een target_id of gebruik --all')
            )
    
    def scan_target(self, target_id):
        """Scan een enkele target"""
        result = perform_full_scan(target_id)
        
        # Output is al geprint door perform_full_scan
        # Hier hoeven we niks extra te doen
