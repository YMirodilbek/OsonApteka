from celery.schedules import crontab
from datetime import timedelta
from celery import Celery
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings')

app = Celery('Admin')


app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()


app.conf.beat_schedule = {
    'refresh-every-60-minutes': {
        'task': 'Product.tasks.refresh_products_cache', 
        'schedule': crontab(minute='*/50'),
    },
    'delete-unpaid-completed-orders': {
        'task': 'Product.tasks.delete_unpaid_completed_orders',
        'schedule': crontab(minute='*/1'),
    },
    
    'delete-ProductPrice-amount-0-price-0':{
        'task':'Product.tasks.delete_ProductPrice',
        'schedule':crontab(hour=3, minute=0),
    }
}

app.conf.timezone = 'Asia/Tashkent'  
