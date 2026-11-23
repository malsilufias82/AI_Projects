from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas.job import AIJobCreate, AIJobProgressUpdate, AIJobResponse, AIJobStatus, AIJobType
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AIJobService:
    """
    Service layer for AI job lifecycle management.

    Responsibilities:
    - Create and persist AIJob records.
    - Update job status and progress.
    - Dispatch jobs to the appropriate Celery queue.
    - Support cancellation and retry.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_job(self, payload: AIJobCreate) -> AIJobResponse:
        """Persist a new AIJob and return its response schema."""
        logger.info("ai_job_create", job_type=payload.job_type)
        raise NotImplementedError("AIJobService.create_job is not yet implemented.")

    async def get_job(self, job_id: UUID) -> AIJobResponse:
        """Fetch a job by ID or raise NotFoundError."""
        raise NotImplementedError("AIJobService.get_job is not yet implemented.")

    async def list_jobs(
        self,
        status: Optional[AIJobStatus] = None,
        job_type: Optional[AIJobType] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[AIJobResponse]:
        """Return a filtered, paginated list of AI jobs."""
        raise NotImplementedError("AIJobService.list_jobs is not yet implemented.")

    async def update_status(
        self,
        job_id: UUID,
        status: AIJobStatus,
        error_message: Optional[str] = None,
    ) -> None:
        """Transition a job to a new status."""
        logger.info("ai_job_status_update", job_id=str(job_id), status=status)
        raise NotImplementedError("AIJobService.update_status is not yet implemented.")

    async def update_progress(self, job_id: UUID, update: AIJobProgressUpdate) -> None:
        """Record a progress update for an in-flight job."""
        logger.debug("ai_job_progress_update", job_id=str(job_id), progress=update.progress)
        raise NotImplementedError("AIJobService.update_progress is not yet implemented.")

    async def set_result(self, job_id: UUID, result: Dict[str, Any]) -> None:
        """Persist the final result payload for a completed job."""
        raise NotImplementedError("AIJobService.set_result is not yet implemented.")

    async def cancel_job(self, job_id: UUID, reason: Optional[str] = None) -> None:
        """Cancel a pending or queued job."""
        logger.info("ai_job_cancel", job_id=str(job_id), reason=reason)
        raise NotImplementedError("AIJobService.cancel_job is not yet implemented.")

    async def dispatch(self, job_id: UUID) -> None:
        """
        Dispatch a job to its Celery queue based on job_type.
        Transitions status from PENDING → QUEUED.
        """
        logger.info("ai_job_dispatch", job_id=str(job_id))
        raise NotImplementedError("AIJobService.dispatch is not yet implemented.")
