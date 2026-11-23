from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Type

from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for all LLM provider implementations.
    Concrete providers must implement all abstract methods.
    """

    provider_id: str = "base"

    def __init__(self, model: str, temperature: float = 0.0, max_tokens: int = 4096, **kwargs: Any) -> None:
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.extra = kwargs

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a text completion from a list of messages."""
        ...

    @abstractmethod
    async def generate_structured(
        self,
        messages: List[LLMMessage],
        response_schema: Type[BaseModel],
        **kwargs: Any,
    ) -> BaseModel:
        """Generate a structured (JSON-mode) response conforming to response_schema."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: List[LLMMessage],
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream tokens as they are generated."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and operational."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.model}>"
