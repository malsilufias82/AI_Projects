from typing import Any, Dict, List, Optional

from celery import Task

from app.ai.config import ai_settings
from app.workers.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseAITask(Task):
    """Base Celery task class with shared AI task lifecycle hooks."""

    abstract = True

    def on_failure(self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        logger.error("ai_task_failed", task_id=task_id, error=str(exc), task_name=self.name)

    def on_retry(self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        logger.warning("ai_task_retrying", task_id=task_id, error=str(exc), task_name=self.name)

    def on_success(self, retval: Any, task_id: str, args: Any, kwargs: Any) -> None:
        logger.info("ai_task_succeeded", task_id=task_id, task_name=self.name)


@celery_app.task(
    bind=True,
    base=BaseAITask,
    name="ai.evaluation.run_evaluation",
    queue=ai_settings.AI_EVALUATION_QUEUE,
    max_retries=ai_settings.AI_JOB_MAX_RETRIES,
    default_retry_delay=ai_settings.AI_JOB_RETRY_DELAY_SECONDS,
)
def run_evaluation_task(self: Task, job_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task: execute the full evaluation workflow for a given job.
    Dispatches to the EvaluationOrchestrator via the WorkflowService.
    """
    logger.info("run_evaluation_task_started", job_id=job_id)
    return {"job_id": job_id, "status": "queued", "placeholder": True}


@celery_app.task(
    bind=True,
    base=BaseAITask,
    name="ai.evaluation.run_single_evaluator",
    queue=ai_settings.AI_EVALUATION_QUEUE,
    max_retries=ai_settings.AI_JOB_MAX_RETRIES,
    default_retry_delay=ai_settings.AI_JOB_RETRY_DELAY_SECONDS,
)
def run_single_evaluator_task(
    self: Task,
    job_id: str,
    evaluator_id: str,
    input_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Celery task: run a single evaluator for parallel fan-out evaluation.
    """
    logger.info("run_single_evaluator_task_started", job_id=job_id, evaluator_id=evaluator_id)
    return {"job_id": job_id, "evaluator_id": evaluator_id, "placeholder": True}


@celery_app.task(
    bind=True,
    base=BaseAITask,
    name="ai.evaluation.aggregate_results",
    queue=ai_settings.AI_ORCHESTRATION_QUEUE,
    max_retries=2,
)
def aggregate_results_task(
    self: Task,
    job_id: str,
    workflow_execution_id: str,
    evaluator_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Celery task: aggregate evaluator results into a unified report.
    """
    logger.info("aggregate_results_task_started", job_id=job_id, result_count=len(evaluator_results))
    return {"job_id": job_id, "workflow_execution_id": workflow_execution_id, "placeholder": True}
