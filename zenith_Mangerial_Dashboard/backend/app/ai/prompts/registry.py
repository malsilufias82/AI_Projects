from typing import Dict, List, Optional

from app.ai.prompts.base import PromptTemplate
from app.core.logging import get_logger

logger = get_logger(__name__)


class PromptTemplateRegistry:
    """
    Runtime registry mapping template IDs to PromptTemplate instances.
    Loaded at startup; supports dynamic re-registration for hot-reload.
    """

    _registry: Dict[str, PromptTemplate] = {}

    @classmethod
    def register(cls, template: PromptTemplate) -> None:
        cls._registry[template.template_id] = template
        logger.debug("prompt_template_registered", template_id=template.template_id, version=template.version)

    @classmethod
    def get(cls, template_id: str) -> Optional[PromptTemplate]:
        return cls._registry.get(template_id)

    @classmethod
    def get_or_raise(cls, template_id: str) -> PromptTemplate:
        tmpl = cls._registry.get(template_id)
        if tmpl is None:
            raise KeyError(f"Prompt template '{template_id}' is not registered.")
        return tmpl

    @classmethod
    def render(cls, template_id: str, variables: Dict) -> str:
        """Convenience: fetch template and render in one call."""
        return cls.get_or_raise(template_id).render(variables)

    @classmethod
    def list_registered(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()
