from typing import Any, Dict, List
from uuid import UUID

from app.ai.pipelines.base import BasePipeline
from app.ai.schemas.results import (
    AggregatedEvaluationResult,
    EvaluationStatus,
    EvaluatorResult,
    FindingSeverity,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class AggregationPipeline(BasePipeline):
    """
    Aggregation pipeline interface.

    Responsibilities:
    - Collect results from all evaluators for a workflow execution.
    - Compute an overall score and status.
    - Produce a unified AggregatedEvaluationResult.
    """

    pipeline_id: str = "aggregation"

    async def validate(self, payload: Dict[str, Any]) -> bool:
        if "job_id" not in payload:
            raise ValueError("AggregationPipeline requires 'job_id'.")
        if "workflow_execution_id" not in payload:
            raise ValueError("AggregationPipeline requires 'workflow_execution_id'.")
        if "evaluator_results" not in payload:
            raise ValueError("AggregationPipeline requires 'evaluator_results'.")
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge evaluator results into a single AggregatedEvaluationResult.
        Scoring strategy injected via config.
        """
        results: List[EvaluatorResult] = payload["evaluator_results"]
        completed = [r for r in results if r.status == EvaluationStatus.COMPLETED]
        failed = [r for r in results if r.status == EvaluationStatus.FAILED]

        scores = [r.score for r in completed if r.score is not None]
        overall_score = sum(scores) / len(scores) if scores else None
        overall_status = (
            EvaluationStatus.FAILED
            if failed and not completed
            else EvaluationStatus.COMPLETED
        )

        all_findings = [f for r in results for f in r.findings]
        critical = sum(1 for f in all_findings if f.severity == FindingSeverity.CRITICAL)
        high = sum(1 for f in all_findings if f.severity == FindingSeverity.HIGH)

        aggregated = AggregatedEvaluationResult(
            job_id=UUID(payload["job_id"]),
            workflow_execution_id=UUID(payload["workflow_execution_id"]),
            overall_status=overall_status,
            overall_score=overall_score,
            evaluator_results=results,
            total_findings=len(all_findings),
            critical_findings=critical,
            high_findings=high,
        )
        return aggregated.model_dump()

    async def on_success(self, output: Dict[str, Any]) -> None:
        logger.info(
            "aggregation_pipeline_success",
            overall_status=output.get("overall_status"),
            overall_score=output.get("overall_score"),
            total_findings=output.get("total_findings", 0),
        )

    async def on_failure(self, error: Exception, payload: Dict[str, Any]) -> None:
        logger.error("aggregation_pipeline_failure", job_id=payload.get("job_id"), error=str(error))
