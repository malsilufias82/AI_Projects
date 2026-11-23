from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type

from langgraph.graph import StateGraph

from app.ai.schemas.workflow import WorkflowDefinition, WorkflowExecutionSummary, WorkflowState
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseOrchestrator(ABC):
    """
    Abstract base class for all LangGraph-backed orchestrators.

    Subclasses define the graph topology (nodes + edges) and register
    them against a LangGraph StateGraph. The orchestrator is responsible
    for execution lifecycle management only — no business logic.
    """

    orchestrator_id: str = "base"

    def __init__(self, definition: WorkflowDefinition, config: Optional[Dict[str, Any]] = None) -> None:
        self.definition = definition
        self.config: Dict[str, Any] = config or {}
        self._graph: Optional[StateGraph] = None

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """
        Construct and return the LangGraph StateGraph for this orchestrator.
        Must call add_node() and add_edge() on the graph before returning.
        """
        ...

    @abstractmethod
    async def on_node_start(self, node_id: str, state: WorkflowState) -> None:
        """Hook invoked before each node begins execution."""
        ...

    @abstractmethod
    async def on_node_complete(self, node_id: str, state: WorkflowState, result: Any) -> None:
        """Hook invoked after each node completes successfully."""
        ...

    @abstractmethod
    async def on_node_error(self, node_id: str, state: WorkflowState, error: Exception) -> None:
        """Hook invoked when a node raises an exception."""
        ...

    def get_graph(self) -> StateGraph:
        """Return the compiled graph, building it on first access."""
        if self._graph is None:
            self._graph = self.build_graph()
        return self._graph

    async def execute(self, initial_state: WorkflowState) -> WorkflowExecutionSummary:
        """
        Run the compiled workflow graph from initial_state.
        Returns a summary of the execution outcome.
        """
        graph = self.get_graph()
        compiled = graph.compile()
        logger.info(
            "orchestrator_execution_start",
            orchestrator_id=self.orchestrator_id,
            workflow_id=initial_state.workflow_id,
            job_id=initial_state.job_id,
        )
        try:
            final_state_dict = await compiled.ainvoke(initial_state.model_dump())
            final_state = WorkflowState(**final_state_dict)
            logger.info(
                "orchestrator_execution_complete",
                orchestrator_id=self.orchestrator_id,
                workflow_id=initial_state.workflow_id,
            )
            from uuid import uuid4
            from app.ai.schemas.workflow import WorkflowStatus

            return WorkflowExecutionSummary(
                execution_id=uuid4(),
                workflow_id=final_state.workflow_id,
                job_id=final_state.job_id,
                status=final_state.status,
                completed_nodes=final_state.completed_nodes,
                failed_nodes=final_state.failed_nodes,
                error=final_state.error,
            )
        except Exception as exc:
            logger.error(
                "orchestrator_execution_failed",
                orchestrator_id=self.orchestrator_id,
                error=str(exc),
                exc_info=True,
            )
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.orchestrator_id}>"
