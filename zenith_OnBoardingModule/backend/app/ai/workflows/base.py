from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.ai.schemas.workflow import WorkflowDefinition, WorkflowExecutionSummary, WorkflowState
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseWorkflow(ABC):
    """
    High-level workflow abstraction sitting above the orchestrator layer.
    Responsible for:
    - building the initial WorkflowState from a job payload
    - delegating execution to the appropriate orchestrator
    - handling pre/post-execution hooks
    """

    workflow_id: str = "base"

    def __init__(self, definition: WorkflowDefinition, config: Optional[Dict[str, Any]] = None) -> None:
        self.definition = definition
        self.config: Dict[str, Any] = config or {}

    @abstractmethod
    async def build_initial_state(self, job_id: str, payload: Dict[str, Any]) -> WorkflowState:
        """Construct the initial WorkflowState from the job payload."""
        ...

    @abstractmethod
    async def before_execute(self, state: WorkflowState) -> None:
        """Hook invoked before orchestrator execution begins."""
        ...

    @abstractmethod
    async def after_execute(self, summary: WorkflowExecutionSummary) -> None:
        """Hook invoked after orchestrator execution completes."""
        ...

    @abstractmethod
    async def get_orchestrator(self) -> Any:
        """Return the configured orchestrator instance for this workflow."""
        ...

    async def run(self, job_id: str, payload: Dict[str, Any]) -> WorkflowExecutionSummary:
        """Orchestrated workflow run."""
        state = await self.build_initial_state(job_id, payload)
        await self.before_execute(state)
        orchestrator = await self.get_orchestrator()
        summary = await orchestrator.execute(state)
        await self.after_execute(summary)
        return summary

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.workflow_id}>"
