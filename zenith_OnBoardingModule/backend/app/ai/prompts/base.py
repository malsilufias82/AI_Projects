from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class PromptTemplate(ABC):
    """
    Abstract base class for all prompt templates.
    Supports variable substitution and versioning.
    """

    template_id: str = "base"
    version: str = "1.0.0"
    description: str = ""

    @abstractmethod
    def render(self, variables: Dict[str, Any]) -> str:
        """
        Render the template with the provided variables.
        Must return a fully-formed prompt string.
        """
        ...

    def validate_variables(self, variables: Dict[str, Any]) -> bool:
        """
        Validate that all required variables are present.
        Override in subclasses to add required-variable checks.
        """
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.template_id} version={self.version}>"


class StringPromptTemplate(PromptTemplate):
    """
    Simple string-interpolation-based prompt template.
    Uses Python str.format_map() for variable substitution.
    """

    template_id: str = "string"

    def __init__(self, template: str, template_id: str = "string", version: str = "1.0.0") -> None:
        self.template = template
        self.template_id = template_id
        self.version = version

    def render(self, variables: Dict[str, Any]) -> str:
        return self.template.format_map(variables)
