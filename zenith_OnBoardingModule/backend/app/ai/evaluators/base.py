import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.ai.schemas.results import (
    BaseEvaluationResult,
    EvaluationStatus,
    EvaluatorResult,
    Finding,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseEvaluator(ABC):
    """
    Abstract base class for all evaluators.

    Lifecycle:
        1. validate_input(input_data)
        2. prepare_context(input_data)
        3. execute(input_data, context)
        4. post_process(raw_result)
        5. generate_summary(result)
    """

    evaluator_id: str = "base"
    evaluator_type: str = "base"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate the input payload before evaluation begins.
        Should raise ValueError with a descriptive message on failure.
        """
        ...

    @abstractmethod
    async def prepare_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assemble retrieval context, metadata, and any pre-processing results.
        Returns a context dict passed directly to execute().
        """
        ...

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core evaluation step. Should call the LLM provider and return raw output.
        DO NOT implement business logic here — keep it pluggable.
        """
        ...

    @abstractmethod
    async def post_process(self, raw_result: Dict[str, Any]) -> List[Finding]:
        """
        Transform raw LLM output into a structured list of Findings.
        """
        ...

    @abstractmethod
    async def generate_summary(self, result: EvaluatorResult) -> str:
        """
        Produce a human-readable summary string from the full evaluator result.
        """
        ...

    async def run(self, input_data: Dict[str, Any]) -> EvaluatorResult:
        """
        Orchestrated evaluation run following the full evaluator lifecycle.
        Handles timing and top-level error capture.
        """
        start = time.monotonic()
        try:
            await self.validate_input(input_data)
            context = await self.prepare_context(input_data)
            raw = await self.execute(input_data, context)
            findings = await self.post_process(raw)
            result = EvaluatorResult(
                evaluator_id=self.evaluator_id,
                evaluator_type=self.evaluator_type,
                status=EvaluationStatus.COMPLETED,
                findings=findings,
                raw_output=raw,
                execution_time_ms=int((time.monotonic() - start) * 1000),
            )
            result.summary = await self.generate_summary(result)
            return result
        except Exception as exc:
            logger.error(
                "evaluator_run_failed",
                evaluator_id=self.evaluator_id,
                error=str(exc),
                exc_info=True,
            )
            return EvaluatorResult(
                evaluator_id=self.evaluator_id,
                evaluator_type=self.evaluator_type,
                status=EvaluationStatus.FAILED,
                error_message=str(exc),
                execution_time_ms=int((time.monotonic() - start) * 1000),
            )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.evaluator_id}>"
