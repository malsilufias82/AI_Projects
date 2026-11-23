from typing import Dict, List, Optional, Type

from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowRegistry:
    """
    Central registry for workflow classes.
    Supports dynamic registration of LangGraph-backed workflows.
    """

    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, workflow_id: str, workflow_class: Type) -> None:
        cls._registry[workflow_id] = workflow_class
        logger.info("workflow_registered", workflow_id=workflow_id)

    @classmethod
    def get(cls, workflow_id: str) -> Optional[Type]:
        return cls._registry.get(workflow_id)

    @classmethod
    def get_or_raise(cls, workflow_id: str) -> Type:
        workflow = cls._registry.get(workflow_id)
        if workflow is None:
            raise KeyError(f"Workflow '{workflow_id}' is not registered.")
        return workflow

    @classmethod
    def list_registered(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()


def register_workflow(workflow_id: str):
    """Class decorator for automatic workflow registration."""

    def decorator(cls: Type) -> Type:
        WorkflowRegistry.register(workflow_id, cls)
        return cls

    return decorator
