from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')

app = Celery('employee_management')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.update(result_expires=10, result_backend='django-db')
# Define a periodic task
app.conf.beat_schedule = {
    'daily_task': {
        'task': 'account.tasks.send_email_before_end_date',
        'schedule': crontab(hour=11, minute=24),  # Run daily at 07:44 PM
    },
}
