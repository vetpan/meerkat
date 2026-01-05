"""
Celery Configuration voor Meerkat

Waarom Celery:
- Background tasks kunnen uren duren (screenshots, AI analyse)
- Django requests mogen max 30 sec, daarna timeout
- Celery draait apart, Django blijft responsive

Waarom Redis:
- Super snel message broker
- In-memory, geen disk I/O
- Perfect voor task queues
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set Django settings module
# Waarom: Celery moet weten welke Django settings te gebruiken
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
# Waarom 'meerkat': Dit is de naam van onze Celery instance
app = Celery('meerkat')

# Load config from Django settings
# Waarom namespace: Alle Celery settings beginnen met CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
# Waarom: Django apps kunnen tasks.py files hebben met @shared_task
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task om te testen of Celery werkt"""
    print(f'Request: {self.request!r}')


# Periodic tasks schedule
# Waarom: We willen NIET elke minuut alle targets scannen
# In plaats daarvan: Elke minuut check welke targets DUE zijn
# app.conf.beat_schedule = {
#     'check-targets-for-scanning': {
#         'task': 'collector.tasks.check_and_scan_targets',
#         'schedule': 60.0,  # Elke minuut
#     },
# }
