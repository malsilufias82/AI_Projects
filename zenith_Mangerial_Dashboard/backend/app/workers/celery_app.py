from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "zenith",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.example_tasks", "app.tasks.sheet_tasks", "app.tasks.email_tasks"],
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.example_tasks.*": {"queue": "default"},
        "app.tasks.sheet_tasks.*": {"queue": "sheets"},
        "app.tasks.email_tasks.*": {"queue": "emails"},
    },
)
