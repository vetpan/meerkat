"""
Test Celery Setup

Run: python manage.py test_celery
"""

from django.core.management.base import BaseCommand
from collector.tasks import scan_target_task, check_and_scan_targets


class Command(BaseCommand):
    help = 'Test Celery setup'

    def handle(self, *args, **options):
        self.stdout.write('Testing Celery...\n')
        
        # Test 1: Check scheduler task
        self.stdout.write('1. Testing check_and_scan_targets...')
        result = check_and_scan_targets.delay()
        self.stdout.write(self.style.SUCCESS(f'   Task ID: {result.id}'))
        
        # Wait for result
        try:
            task_result = result.get(timeout=10)
            self.stdout.write(self.style.SUCCESS(f'   Result: {task_result}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Celery is working!'))
