from celery import Celery

from app.config import CELERY_BROKER_URL

celery_app = Celery(
    "day10_ecommerce",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BROKER_URL,
)

celery_app.conf.update(task_track_started=True)
