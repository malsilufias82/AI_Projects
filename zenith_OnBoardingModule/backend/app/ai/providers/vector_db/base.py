from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VectorDocument:
    """A document to insert into the vector store."""

    id: str
    vector: List[float]
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A single result from a vector similarity search."""

    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseVectorStore(ABC):
    """
    Abstract base class for all vector database provider implementations.
    """

    provider_id: str = "base"

    def __init__(self, collection_prefix: str = "zenith", **kwargs: Any) -> None:
        self.collection_prefix = collection_prefix
        self.extra = kwargs

    def _collection_name(self, name: str) -> str:
        """Build a prefixed collection name."""
        return f"{self.collection_prefix}_{name}"

    @abstractmethod
    async def create_collection(self, name: str, dimension: int, **kwargs: Any) -> None:
        """Create a new vector collection if it does not already exist."""
        ...

    @abstractmethod
    async def collection_exists(self, name: str) -> bool:
        """Return True if the named collection exists."""
        ...

    @abstractmethod
    async def insert(self, collection: str, documents: List[VectorDocument], **kwargs: Any) -> None:
        """Insert a batch of documents into a collection."""
        ...

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        """Perform a similarity search and return the top-k results."""
        ...

    @abstractmethod
    async def delete(self, collection: str, document_ids: List[str], **kwargs: Any) -> None:
        """Delete documents by ID from a collection."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the vector store is reachable."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} prefix={self.collection_prefix}>"
