from typing import Any, Dict, List

from celery import Task

from app.ai.config import ai_settings
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    bind=True,
    name="ai.embedding.embed_artifact",
    queue=ai_settings.AI_EMBEDDING_QUEUE,
    max_retries=ai_settings.AI_JOB_MAX_RETRIES,
    default_retry_delay=ai_settings.AI_JOB_RETRY_DELAY_SECONDS,
)
def embed_artifact_task(self: Task, artifact_id: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Celery task: generate and persist embeddings for all chunks of an artifact.
    """
    logger.info("embed_artifact_task_started", artifact_id=artifact_id, chunk_count=len(chunks))
    return {"artifact_id": artifact_id, "embedded_count": 0, "placeholder": True}


@celery_app.task(
    bind=True,
    name="ai.embedding.embed_batch",
    queue=ai_settings.AI_EMBEDDING_QUEUE,
    max_retries=ai_settings.AI_JOB_MAX_RETRIES,
    default_retry_delay=ai_settings.AI_JOB_RETRY_DELAY_SECONDS,
)
def embed_batch_task(
    self: Task,
    artifact_id: str,
    batch: List[Dict[str, Any]],
    collection: str,
) -> Dict[str, Any]:
    """
    Celery task: embed a single batch of chunks and upsert into the vector store.
    Used by chord/chord-group patterns for parallel batch embedding.
    """
    logger.info("embed_batch_task_started", artifact_id=artifact_id, batch_size=len(batch), collection=collection)
    return {"artifact_id": artifact_id, "batch_size": len(batch), "collection": collection, "placeholder": True}
