from typing import Dict, List, Optional, Type

from app.core.logging import get_logger

logger = get_logger(__name__)


class EvaluatorRegistry:
    """
    Central registry for all evaluator classes.
    Supports dynamic registration and discovery.
    """

    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls, evaluator_id: str, evaluator_class: Type) -> None:
        """Register an evaluator class under a unique ID."""
        if evaluator_id in cls._registry:
            logger.warning("evaluator_already_registered", evaluator_id=evaluator_id)
        cls._registry[evaluator_id] = evaluator_class
        logger.info("evaluator_registered", evaluator_id=evaluator_id)

    @classmethod
    def get(cls, evaluator_id: str) -> Optional[Type]:
        """Retrieve an evaluator class by ID."""
        return cls._registry.get(evaluator_id)

    @classmethod
    def get_or_raise(cls, evaluator_id: str) -> Type:
        """Retrieve an evaluator class or raise KeyError."""
        evaluator = cls._registry.get(evaluator_id)
        if evaluator is None:
            raise KeyError(f"Evaluator '{evaluator_id}' is not registered.")
        return evaluator

    @classmethod
    def list_registered(cls) -> List[str]:
        """Return all registered evaluator IDs."""
        return list(cls._registry.keys())

    @classmethod
    def unregister(cls, evaluator_id: str) -> None:
        """Remove an evaluator from the registry."""
        cls._registry.pop(evaluator_id, None)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered evaluators (primarily for testing)."""
        cls._registry.clear()


def register_evaluator(evaluator_id: str):
    """Class decorator for automatic evaluator registration."""

    def decorator(cls: Type) -> Type:
        EvaluatorRegistry.register(evaluator_id, cls)
        return cls

    return decorator
