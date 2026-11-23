from typing import Any, Dict, List

from app.ai.evaluators.base import BaseEvaluator
from app.ai.registry.evaluator_registry import register_evaluator
from app.ai.schemas.results import EvaluatorResult, Finding


@register_evaluator("delivery")
class DeliveryEvaluator(BaseEvaluator):
    """
    Placeholder evaluator for delivery & deployment quality assessment.
    Evaluates: CI/CD pipelines, Docker setup, deployment scripts, environment config.
    """

    evaluator_id: str = "delivery"
    evaluator_type: str = "delivery"

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "artifact_id" not in input_data:
            raise ValueError("DeliveryEvaluator requires 'artifact_id' in input_data.")
        return True

    async def prepare_context(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"artifact_id": input_data.get("artifact_id"), "retrieved_chunks": []}

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {"placeholder": True, "evaluator": self.evaluator_id}

    async def post_process(self, raw_result: Dict[str, Any]) -> List[Finding]:
        return []

    async def generate_summary(self, result: EvaluatorResult) -> str:
        return f"Delivery evaluation placeholder — {len(result.findings)} finding(s)."
