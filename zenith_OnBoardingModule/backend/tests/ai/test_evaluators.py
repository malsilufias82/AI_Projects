import pytest

from app.ai.evaluators.architecture.evaluator import ArchitectureEvaluator
from app.ai.evaluators.code_quality.evaluator import CodeQualityEvaluator
from app.ai.evaluators.security.evaluator import SecurityEvaluator
from app.ai.registry.evaluator_registry import EvaluatorRegistry, register_evaluator
from app.ai.schemas.results import EvaluationStatus


@pytest.mark.asyncio
async def test_architecture_evaluator_validate_input_valid():
    evaluator = ArchitectureEvaluator()
    result = await evaluator.validate_input({"artifact_id": "test-123"})
    assert result is True


@pytest.mark.asyncio
async def test_architecture_evaluator_validate_input_missing_artifact_id():
    evaluator = ArchitectureEvaluator()
    with pytest.raises(ValueError, match="artifact_id"):
        await evaluator.validate_input({})


@pytest.mark.asyncio
async def test_architecture_evaluator_run_returns_result():
    evaluator = ArchitectureEvaluator()
    result = await evaluator.run({"artifact_id": "test-123"})
    assert result.evaluator_id == "architecture"
    assert result.status == EvaluationStatus.COMPLETED
    assert result.execution_time_ms is not None


@pytest.mark.asyncio
async def test_code_quality_evaluator_run_returns_result():
    evaluator = CodeQualityEvaluator()
    result = await evaluator.run({"artifact_id": "test-456"})
    assert result.evaluator_id == "code_quality"
    assert result.status == EvaluationStatus.COMPLETED


@pytest.mark.asyncio
async def test_security_evaluator_run_returns_result():
    evaluator = SecurityEvaluator()
    result = await evaluator.run({"artifact_id": "test-789"})
    assert result.evaluator_id == "security"
    assert result.status == EvaluationStatus.COMPLETED


@pytest.mark.asyncio
async def test_evaluator_run_captures_failure():
    class BrokenEvaluator(ArchitectureEvaluator):
        async def execute(self, input_data, context):
            raise RuntimeError("simulated failure")

    evaluator = BrokenEvaluator()
    result = await evaluator.run({"artifact_id": "fail-test"})
    assert result.status == EvaluationStatus.FAILED
    assert "simulated failure" in (result.error_message or "")


def test_evaluator_registry_register_and_get():
    @register_evaluator("test_eval")
    class TestEvaluator(ArchitectureEvaluator):
        evaluator_id = "test_eval"

    klass = EvaluatorRegistry.get("test_eval")
    assert klass is TestEvaluator


def test_evaluator_registry_get_missing_returns_none():
    assert EvaluatorRegistry.get("does_not_exist") is None


def test_evaluator_registry_get_or_raise_missing():
    with pytest.raises(KeyError):
        EvaluatorRegistry.get_or_raise("does_not_exist")
