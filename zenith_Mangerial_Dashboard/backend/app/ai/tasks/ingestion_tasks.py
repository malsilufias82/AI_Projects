from typing import Any, Dict

from celery import Task

from app.ai.config import ai_settings
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="ai.ingestion.ingest_artifact",
    queue=ai_settings.AI_INGESTION_QUEUE,
    max_retries=ai_settings.AI_JOB_MAX_RETRIES,
    default_retry_delay=ai_settings.AI_JOB_RETRY_DELAY_SECONDS,
)
def ingest_artifact_task(self: Task, artifact_id: str, source: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task: ingest an artifact from source, extract content, and
    trigger the chunking → embedding pipeline chain.
    """
    logger.info("ingest_artifact_task_started", artifact_id=artifact_id, source=source)
    return {"artifact_id": artifact_id, "source": source, "status": "ingested", "placeholder": True}


@celery_app.task(
    bind=True,
    name="ai.ingestion.chunk_artifact",
    queue=ai_settings.AI_INGESTION_QUEUE,
    max_retries=ai_settings.AI_JOB_MAX_RETRIES,
    default_retry_delay=ai_settings.AI_JOB_RETRY_DELAY_SECONDS,
)
def chunk_artifact_task(self: Task, artifact_id: str, raw_content: str, strategy: str = "semantic") -> Dict[str, Any]:
    """
    Celery task: apply the configured chunking strategy to raw artifact content.
    Output is forwarded to the embedding task via a Celery chain.
    """
    logger.info("chunk_artifact_task_started", artifact_id=artifact_id, strategy=strategy)
    return {"artifact_id": artifact_id, "chunks": [], "chunk_count": 0, "placeholder": True}
