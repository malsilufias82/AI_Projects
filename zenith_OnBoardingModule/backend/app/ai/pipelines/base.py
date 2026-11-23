import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class PipelineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BasePipeline(ABC):
    """
    Abstract base class for all AI processing pipelines.
    Each pipeline represents a discrete, reusable processing stage.
    """

    pipeline_id: str = "base"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self.status: PipelineStatus = PipelineStatus.IDLE
        self._last_execution_ms: Optional[int] = None

    @abstractmethod
    async def validate(self, payload: Dict[str, Any]) -> bool:
        """Validate the input payload before pipeline execution."""
        ...

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run the core pipeline logic and return output."""
        ...

    @abstractmethod
    async def on_success(self, output: Dict[str, Any]) -> None:
        """Hook called after a successful execution."""
        ...

    @abstractmethod
    async def on_failure(self, error: Exception, payload: Dict[str, Any]) -> None:
        """Hook called when execution raises an exception."""
        ...

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrated pipeline run with lifecycle hooks and timing."""
        start = time.monotonic()
        self.status = PipelineStatus.RUNNING
        try:
            await self.validate(payload)
            output = await self.execute(payload)
            self._last_execution_ms = int((time.monotonic() - start) * 1000)
            self.status = PipelineStatus.COMPLETED
            await self.on_success(output)
            logger.info(
                "pipeline_completed",
                pipeline_id=self.pipeline_id,
                execution_ms=self._last_execution_ms,
            )
            return output
        except Exception as exc:
            self.status = PipelineStatus.FAILED
            self._last_execution_ms = int((time.monotonic() - start) * 1000)
            logger.error("pipeline_failed", pipeline_id=self.pipeline_id, error=str(exc), exc_info=True)
            await self.on_failure(exc, payload)
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.pipeline_id} status={self.status}>"
