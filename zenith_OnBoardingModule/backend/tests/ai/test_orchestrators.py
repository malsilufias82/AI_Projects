import pytest

from app.ai.orchestrators.evaluation_orchestrator import EvaluationOrchestrator
from app.ai.registry.evaluator_registry import EvaluatorRegistry
from app.ai.registry.workflow_registry import WorkflowRegistry
from app.ai.schemas.workflow import WorkflowState, WorkflowStatus
from app.ai.evaluators.architecture.evaluator import ArchitectureEvaluator
from app.ai.evaluators.code_quality.evaluator import CodeQualityEvaluator


def test_evaluation_orchestrator_is_registered():
    assert WorkflowRegistry.get("evaluation") is EvaluationOrchestrator


def test_evaluation_orchestrator_builds_graph():
    orchestrator = EvaluationOrchestrator()
    graph = orchestrator.build_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_evaluation_orchestrator_executes_empty_evaluators():
    EvaluatorRegistry.register("architecture", ArchitectureEvaluator)
    EvaluatorRegistry.register("code_quality", CodeQualityEvaluator)

    orchestrator = EvaluationOrchestrator()
    initial_state = WorkflowState(
        workflow_id="evaluation",
        job_id="test-job-001",
        context={
            "evaluator_ids": ["architecture", "code_quality"],
            "input_data": {"artifact_id": "artifact-test-001"},
        },
    )
    summary = await orchestrator.execute(initial_state)
    assert summary.workflow_id == "evaluation"
    assert summary.job_id == "test-job-001"
    assert summary.status == WorkflowStatus.COMPLETED
    assert "ingestion" in summary.completed_nodes
    assert "evaluation" in summary.completed_nodes
    assert "aggregation" in summary.completed_nodes


@pytest.mark.asyncio
async def test_evaluation_orchestrator_handles_unknown_evaluator():
    orchestrator = EvaluationOrchestrator()
    initial_state = WorkflowState(
        workflow_id="evaluation",
        job_id="test-job-002",
        context={
            "evaluator_ids": ["unknown_evaluator"],
            "input_data": {"artifact_id": "artifact-test-002"},
        },
    )
    summary = await orchestrator.execute(initial_state)
    assert summary.status == WorkflowStatus.COMPLETED
    assert not summary.failed_nodes


@pytest.mark.asyncio
async def test_context_window_respects_token_budget():
    from app.ai.context.window import ContextWindow
    from app.ai.context.models import ChunkReference

    window = ContextWindow(max_tokens=20)
    chunk_small = ChunkReference(
        chunk_id="c1", artifact_id="a1", content="A" * 40, score=0.9, index=0
    )
    chunk_large = ChunkReference(
        chunk_id="c2", artifact_id="a1", content="B" * 200, score=0.8, index=1
    )
    assert window.try_add(chunk_small) is True
    assert window.try_add(chunk_large) is False
    assert len(window) == 1
