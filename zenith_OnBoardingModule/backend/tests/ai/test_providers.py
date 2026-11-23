import pytest

from app.ai.providers.vector_db.base import VectorDocument
from tests.ai.conftest import MockEmbeddingProvider, MockLLMProvider, MockVectorStore
from app.ai.providers.llm.base import LLMMessage


@pytest.mark.asyncio
async def test_mock_llm_generate(mock_llm: MockLLMProvider):
    messages = [LLMMessage(role="user", content="Hello")]
    response = await mock_llm.generate(messages)
    assert response.content == "mock response"
    assert response.model == "mock-model"
    assert mock_llm.call_count == 1


@pytest.mark.asyncio
async def test_mock_llm_stream(mock_llm: MockLLMProvider):
    messages = [LLMMessage(role="user", content="Hello")]
    tokens = []
    async for token in mock_llm.stream(messages):
        tokens.append(token)
    assert len(tokens) > 0
    assert "".join(tokens).strip() == "mock response"


@pytest.mark.asyncio
async def test_mock_llm_health_check(mock_llm: MockLLMProvider):
    assert await mock_llm.health_check() is True


@pytest.mark.asyncio
async def test_mock_embedding_embed_text(mock_embedding: MockEmbeddingProvider):
    response = await mock_embedding.embed_text("test input")
    assert len(response.vector) == mock_embedding.dimension
    assert response.model == "mock-embed"


@pytest.mark.asyncio
async def test_mock_embedding_embed_batch(mock_embedding: MockEmbeddingProvider):
    texts = ["first", "second", "third"]
    responses = await mock_embedding.embed_batch(texts)
    assert len(responses) == 3
    for r in responses:
        assert len(r.vector) == mock_embedding.dimension


@pytest.mark.asyncio
async def test_mock_vector_store_create_and_exists(mock_vector_store: MockVectorStore):
    await mock_vector_store.create_collection("my_collection", dimension=4)
    assert await mock_vector_store.collection_exists("my_collection") is True


@pytest.mark.asyncio
async def test_mock_vector_store_insert_and_search(mock_vector_store: MockVectorStore):
    await mock_vector_store.create_collection("artifacts", dimension=4)
    docs = [
        VectorDocument(id="doc1", vector=[0.1, 0.2, 0.3, 0.4], text="Hello world", metadata={}),
        VectorDocument(id="doc2", vector=[0.5, 0.6, 0.7, 0.8], text="Foo bar", metadata={}),
    ]
    await mock_vector_store.insert("artifacts", docs)
    results = await mock_vector_store.search("artifacts", query_vector=[0.1, 0.2, 0.3, 0.4])
    assert len(results) == 2
    assert results[0].id == "doc1"


@pytest.mark.asyncio
async def test_mock_vector_store_delete(mock_vector_store: MockVectorStore):
    await mock_vector_store.create_collection("del_test", dimension=4)
    docs = [VectorDocument(id="d1", vector=[0.1] * 4, text="Delete me", metadata={})]
    await mock_vector_store.insert("del_test", docs)
    await mock_vector_store.delete("del_test", ["d1"])
    results = await mock_vector_store.search("del_test", query_vector=[0.1] * 4)
    assert all(r.id != "d1" for r in results)
