"""
Celery Configuration for SOC Agent
Handles async task processing with Redis broker
"""
from celery import Celery
from celery.schedules import crontab
import os

# Initialize Celery app
app = Celery('soc_agent')

# Configure Celery
app.conf.update(
    # Redis broker for task queue
    broker_url=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    result_backend=os.getenv('REDIS_URL', 'redis://redis:6379/1'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task timeout (seconds)
    task_soft_time_limit=300,  # 5 minutes soft timeout
    task_time_limit=600,        # 10 minutes hard timeout
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from all installed apps
from app.tasks import analysis
app.autodiscover_tasks(['app.tasks'])

@app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working"""
    print(f'Request: {self.request!r}')
