import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Настройка расписания для Celery Beat
app.conf.beat_schedule = {
    'delete-expired-bookings': {
        'task': 'applications.services.tasks.delete_expired_bookings',
        'schedule': crontab(hour=0, minute=0),  # Запускать каждый день в полночь
    },
}
