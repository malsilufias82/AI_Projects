from abc import ABC, abstractmethod
from typing import Any, List


class EmbeddingResponse(object):
    """Lightweight wrapper around a single embedding vector."""

    def __init__(self, vector: List[float], model: str, tokens: int = 0) -> None:
        self.vector = vector
        self.model = model
        self.tokens = tokens


class BaseEmbeddingProvider(ABC):
    """
    Abstract base class for all embedding provider implementations.
    """

    provider_id: str = "base"

    def __init__(self, model: str, dimension: int, batch_size: int = 100, **kwargs: Any) -> None:
        self.model = model
        self.dimension = dimension
        self.batch_size = batch_size
        self.extra = kwargs

    @abstractmethod
    async def embed_text(self, text: str, **kwargs: Any) -> EmbeddingResponse:
        """Generate an embedding for a single text string."""
        ...

    @abstractmethod
    async def embed_batch(self, texts: List[str], **kwargs: Any) -> List[EmbeddingResponse]:
        """
        Generate embeddings for a list of texts.
        Implementations should honour self.batch_size when splitting requests.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the provider is reachable and operational."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.model} dim={self.dimension}>"
