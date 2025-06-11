from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings')

app = Celery('Admin')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()


app.conf.beat_schedule = {
    'refresh-every-60-minutes': {
        'task': 'Product.tasks.refresh_products_cache', 
        'schedule': crontab(minute='*/10'),
    },
    'delete-unpaid-completed-orders': {
        'task': 'Product.tasks.delete_unpaid_completed_orders',
        'schedule': crontab(minute='*/1'),
    },
}

app.conf.timezone = 'Asia/Tashkent'  
