from dotenv import load_dotenv
import os
from celery.schedules import crontab

load_dotenv()

CELERY_CONFIG = {
    'broker_url': os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'),
    'result_backend': os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'timezone': 'Africa/Nairobi',
    'enable_utc': True,
    'imports': ('app.tasks.update_feed',),
}


CELERY_CONFIG.update({
    'beat_schedule': {
        'check-feeds-every-hour': {
            'task': 'app.tasks.update_feed.update_rss_feeds',
            'schedule': crontab(minute=0, hour='*'),  # toutes les 10 minutes
        },
    },
    'beat_scheduler': 'celery.beat:PersistentScheduler',
})
