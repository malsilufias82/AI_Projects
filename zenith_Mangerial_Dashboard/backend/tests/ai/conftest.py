from typing import Any, AsyncIterator, Dict, List, Optional, Type
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.providers.embeddings.base import BaseEmbeddingProvider, EmbeddingResponse
from app.ai.providers.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.ai.providers.vector_db.base import BaseVectorStore, SearchResult, VectorDocument
from app.ai.registry.evaluator_registry import EvaluatorRegistry
from app.ai.registry.provider_registry import ProviderRegistry


@pytest.fixture(autouse=True)
def reset_registries():
    """Ensure registries are clean before every AI test."""
    EvaluatorRegistry.clear()
    ProviderRegistry.clear()
    yield
    EvaluatorRegistry.clear()
    ProviderRegistry.clear()


class MockLLMProvider(BaseLLMProvider):
    """In-memory LLM provider for testing."""

    provider_id = "mock"

    def __init__(self, response_content: str = "mock response") -> None:
        super().__init__(model="mock-model")
        self.response_content = response_content
        self.call_count = 0

    async def generate(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        self.call_count += 1
        return LLMResponse(
            content=self.response_content,
            model=self.model,
            prompt_tokens=10,
            completion_tokens=20,
        )

    async def generate_structured(
        self, messages: List[LLMMessage], response_schema: Type, **kwargs: Any
    ):
        self.call_count += 1
        return response_schema.model_validate({})

    async def stream(self, messages: List[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        for word in self.response_content.split():
            yield word + " "

    async def health_check(self) -> bool:
        return True


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """In-memory embedding provider for testing."""

    provider_id = "mock"

    def __init__(self, dimension: int = 4) -> None:
        super().__init__(model="mock-embed", dimension=dimension)

    async def embed_text(self, text: str, **kwargs: Any) -> EmbeddingResponse:
        return EmbeddingResponse(vector=[0.1] * self.dimension, model=self.model, tokens=len(text))

    async def embed_batch(self, texts: List[str], **kwargs: Any) -> List[EmbeddingResponse]:
        return [await self.embed_text(t) for t in texts]

    async def health_check(self) -> bool:
        return True


class MockVectorStore(BaseVectorStore):
    """In-memory vector store for testing."""

    provider_id = "mock"

    def __init__(self) -> None:
        super().__init__(collection_prefix="test")
        self._store: Dict[str, List[VectorDocument]] = {}

    async def create_collection(self, name: str, dimension: int, **kwargs: Any) -> None:
        self._store.setdefault(self._collection_name(name), [])

    async def collection_exists(self, name: str) -> bool:
        return self._collection_name(name) in self._store

    async def insert(self, collection: str, documents: List[VectorDocument], **kwargs: Any) -> None:
        self._store.setdefault(self._collection_name(collection), []).extend(documents)

    async def search(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        docs = self._store.get(self._collection_name(collection), [])
        return [
            SearchResult(id=doc.id, text=doc.text, score=0.9, metadata=doc.metadata)
            for doc in docs[:top_k]
        ]

    async def delete(self, collection: str, document_ids: List[str], **kwargs: Any) -> None:
        col = self._collection_name(collection)
        self._store[col] = [d for d in self._store.get(col, []) if d.id not in document_ids]

    async def health_check(self) -> bool:
        return True


@pytest.fixture
def mock_llm():
    return MockLLMProvider()


@pytest.fixture
def mock_embedding():
    return MockEmbeddingProvider()


@pytest.fixture
def mock_vector_store():
    return MockVectorStore()
