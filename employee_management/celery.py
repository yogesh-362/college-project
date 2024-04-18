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
        'schedule': crontab(hour=19, minute=40),  # Run daily at 12:00 PM
    },
}
#runserver
# redis-server
# celery -A employee_management worker -l info -P eventlet
# celery -A employee_management beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

