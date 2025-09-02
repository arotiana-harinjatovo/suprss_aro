from celery import Celery
from app.celery_config import CELERY_CONFIG

celery_app = Celery("worker")
celery_app.config_from_object(CELERY_CONFIG)
celery_app.autodiscover_tasks(['app.tasks'])
