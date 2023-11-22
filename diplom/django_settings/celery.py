from __future__ import absolute_import, unicode_literals
from celery import Celery
from celery.schedules import crontab

app = Celery('django_settings')

# Указываем адрес брокера сообщений (в данном случае используем Redis)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Настраиваем периодическую отправку задачи раз в сутки
app.conf.beat_schedule = {
    'send_weekly_product_list': {
        'task': 'django_app/view.py',  # Путь к вашей задаче
        'schedule': crontab(minute=0, hour=0),  # Каждый день в полночь
    },
}

app.autodiscover_tasks()
