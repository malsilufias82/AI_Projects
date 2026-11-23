from app.ai.config import ai_settings
from app.workers.celery_app import celery_app

celery_app.conf.update(
    task_routes={
        "ai.evaluation.*": {"queue": ai_settings.AI_EVALUATION_QUEUE},
        "ai.embedding.*": {"queue": ai_settings.AI_EMBEDDING_QUEUE},
        "ai.ingestion.*": {"queue": ai_settings.AI_INGESTION_QUEUE},
        "ai.orchestration.*": {"queue": ai_settings.AI_ORCHESTRATION_QUEUE},
    },
    task_queues_from_routes=True,
)

celery_app.autodiscover_tasks(
    [
        "app.ai.tasks.evaluation_tasks",
        "app.ai.tasks.embedding_tasks",
        "app.ai.tasks.ingestion_tasks",
    ]
)
