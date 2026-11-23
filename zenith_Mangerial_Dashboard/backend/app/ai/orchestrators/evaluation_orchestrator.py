from typing import Any, Dict, List, Optional

from langgraph.graph import END, StateGraph

from app.ai.orchestrators.base import BaseOrchestrator
from app.ai.registry.evaluator_registry import EvaluatorRegistry
from app.ai.registry.workflow_registry import register_workflow
from app.ai.schemas.workflow import WorkflowDefinition, WorkflowState, WorkflowStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


def _make_ingestion_node(orchestrator: "EvaluationOrchestrator"):
    async def ingestion_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ws = WorkflowState(**state)
        await orchestrator.on_node_start("ingestion", ws)
        logger.info("eval_orchestrator_ingestion_node", job_id=ws.job_id)
        ws.completed_nodes.append("ingestion")
        ws.current_node = "retrieval"
        await orchestrator.on_node_complete("ingestion", ws, {})
        return ws.model_dump()

    return ingestion_node


def _make_retrieval_node(orchestrator: "EvaluationOrchestrator"):
    async def retrieval_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ws = WorkflowState(**state)
        await orchestrator.on_node_start("retrieval", ws)
        logger.info("eval_orchestrator_retrieval_node", job_id=ws.job_id)
        ws.completed_nodes.append("retrieval")
        ws.current_node = "evaluation"
        await orchestrator.on_node_complete("retrieval", ws, {})
        return ws.model_dump()

    return retrieval_node


def _make_evaluation_node(orchestrator: "EvaluationOrchestrator"):
    async def evaluation_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ws = WorkflowState(**state)
        await orchestrator.on_node_start("evaluation", ws)
        logger.info("eval_orchestrator_evaluation_node", job_id=ws.job_id)
        evaluator_ids: List[str] = ws.context.get("evaluator_ids", [])
        results = []
        for eid in evaluator_ids:
            klass = EvaluatorRegistry.get(eid)
            if klass is None:
                logger.warning("evaluator_not_found", evaluator_id=eid)
                continue
            evaluator = klass()
            result = await evaluator.run(ws.context.get("input_data", {}))
            results.append(result.model_dump())
        ws.node_results["evaluation"] = results
        ws.completed_nodes.append("evaluation")
        ws.current_node = "aggregation"
        await orchestrator.on_node_complete("evaluation", ws, results)
        return ws.model_dump()

    return evaluation_node


def _make_aggregation_node(orchestrator: "EvaluationOrchestrator"):
    async def aggregation_node(state: Dict[str, Any]) -> Dict[str, Any]:
        ws = WorkflowState(**state)
        await orchestrator.on_node_start("aggregation", ws)
        logger.info("eval_orchestrator_aggregation_node", job_id=ws.job_id)
        ws.completed_nodes.append("aggregation")
        ws.current_node = None
        ws.status = WorkflowStatus.COMPLETED
        await orchestrator.on_node_complete("aggregation", ws, {})
        return ws.model_dump()

    return aggregation_node


@register_workflow("evaluation")
class EvaluationOrchestrator(BaseOrchestrator):
    """
    LangGraph-backed evaluation workflow orchestrator.

    Graph topology:
        ingestion → retrieval → evaluation → aggregation → END

    Evaluation nodes run registered evaluators in sequence.
    Future: replace with parallel fan-out via Send API.
    """

    orchestrator_id: str = "evaluation"

    def __init__(self, definition: Optional[WorkflowDefinition] = None, config: Optional[Dict[str, Any]] = None) -> None:
        if definition is None:
            definition = WorkflowDefinition(
                workflow_id="evaluation",
                name="Evaluation Workflow",
                description="Multi-evaluator project assessment workflow.",
            )
        super().__init__(definition=definition, config=config)

    def build_graph(self) -> StateGraph:
        """Construct the evaluation StateGraph with four sequential nodes."""
        graph = StateGraph(dict)
        graph.add_node("ingestion", _make_ingestion_node(self))
        graph.add_node("retrieval", _make_retrieval_node(self))
        graph.add_node("evaluation", _make_evaluation_node(self))
        graph.add_node("aggregation", _make_aggregation_node(self))

        graph.set_entry_point("ingestion")
        graph.add_edge("ingestion", "retrieval")
        graph.add_edge("retrieval", "evaluation")
        graph.add_edge("evaluation", "aggregation")
        graph.add_edge("aggregation", END)
        return graph

    async def on_node_start(self, node_id: str, state: WorkflowState) -> None:
        logger.debug("node_start", orchestrator_id=self.orchestrator_id, node=node_id, job_id=state.job_id)

    async def on_node_complete(self, node_id: str, state: WorkflowState, result: Any) -> None:
        logger.debug("node_complete", orchestrator_id=self.orchestrator_id, node=node_id, job_id=state.job_id)

    async def on_node_error(self, node_id: str, state: WorkflowState, error: Exception) -> None:
        logger.error("node_error", orchestrator_id=self.orchestrator_id, node=node_id, error=str(error))
