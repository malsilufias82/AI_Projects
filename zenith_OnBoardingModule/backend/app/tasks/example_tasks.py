from app.core.logging import get_logger
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="app.tasks.example_tasks.sample_task",
    max_retries=3,
    default_retry_delay=60,
)
def sample_task(self, payload: dict) -> dict:
    """
    Placeholder task demonstrating Celery task structure.
    Replace with actual business logic in feature modules.
    """
    logger.info("Executing sample task", task_id=self.request.id, payload=payload)
    return {"status": "completed", "task_id": self.request.id}


@celery_app.task(
    bind=True,
    name="app.tasks.example_tasks.send_notification",
    max_retries=3,
    default_retry_delay=30,
)
def send_notification(self, user_id: str, message: str) -> dict:
    """
    Notification task placeholder.
    Extend this to integrate email / push / webhook providers.
    """
    logger.info("Sending notification", user_id=user_id, message=message)
    return {"status": "sent", "user_id": user_id}
