from typing import Dict, List, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)


class PromptRegistry:
    """
    Central registry for prompt templates.
    Keys are namespaced as '{evaluator_id}.{prompt_name}'.
    """

    _registry: Dict[str, str] = {}

    @classmethod
    def register(cls, key: str, template: str) -> None:
        """Register a prompt template under a namespaced key."""
        cls._registry[key] = template
        logger.debug("prompt_registered", key=key)

    @classmethod
    def get(cls, key: str) -> Optional[str]:
        """Retrieve a prompt template by key."""
        return cls._registry.get(key)

    @classmethod
    def get_or_raise(cls, key: str) -> str:
        """Retrieve a prompt template or raise KeyError."""
        template = cls._registry.get(key)
        if template is None:
            raise KeyError(f"Prompt template '{key}' is not registered.")
        return template

    @classmethod
    def list_registered(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()
