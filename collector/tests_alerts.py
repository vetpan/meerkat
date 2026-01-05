from django.test import TestCase, override_settings
from django.core import mail
from shared.models import Target, Scan, Alert
from collector.tasks import send_alert_task
from django.utils import timezone

class AlertTestCase(TestCase):
    def setUp(self):
        self.target = Target.objects.create(name="Test Target", url="http://example.com")
        self.scan = Scan.objects.create(
            target=self.target,
            status='success',
            content_hash='abc',
            screenshot_path='/tmp/test.png',
            scanned_at=timezone.now(),
            analysis_json={
                'type': 'critical',
                'title': 'Test Change',
                'summary': 'Something changed',
                'changes': [
                    {'category': 'Price', 'change_description': 'Price up', 'impact_score': 8}
                ]
            }
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_alert(self):
        send_alert_task(self.scan.id)
        
        # Check email sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Test Change', mail.outbox[0].subject)
        
        # Check Alert created
        self.assertTrue(Alert.objects.filter(scan=self.scan).exists())
        self.assertEqual(Alert.objects.get(scan=self.scan).status, 'sent')
        
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_duplicate_alert_prevention(self):
        # Create existing alert
        Alert.objects.create(scan=self.scan, recipient='test', status='sent')
        
        send_alert_task(self.scan.id)
        
        # Should not send another
        self.assertEqual(len(mail.outbox), 0)
