from typing import Any, Dict, List, Optional

from app.ai.providers.vector_db.base import BaseVectorStore, SearchResult, VectorDocument
from app.ai.registry.provider_registry import ProviderType, register_provider
from app.core.logging import get_logger

logger = get_logger(__name__)


@register_provider(ProviderType.VECTOR_DB, "chroma")
class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB vector store placeholder (development / local use).
    Uses the chromadb HTTP client to connect to a running Chroma server.
    """

    provider_id: str = "chroma"

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8001,
        collection_prefix: str = "zenith",
        **kwargs: Any,
    ) -> None:
        super().__init__(collection_prefix=collection_prefix, **kwargs)
        self.host = host
        self.port = port
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None:
            import chromadb

            self._client = chromadb.HttpClient(host=self.host, port=self.port)
        return self._client

    async def create_collection(self, name: str, dimension: int, **kwargs: Any) -> None:
        """Create a ChromaDB collection if it does not exist."""
        client = self._get_client()
        full_name = self._collection_name(name)
        client.get_or_create_collection(name=full_name, metadata={"dimension": dimension, **kwargs})
        logger.info("chroma_collection_created", name=full_name)

    async def collection_exists(self, name: str) -> bool:
        """Check whether a ChromaDB collection exists."""
        client = self._get_client()
        full_name = self._collection_name(name)
        collections = client.list_collections()
        return any(c.name == full_name for c in collections)

    async def insert(self, collection: str, documents: List[VectorDocument], **kwargs: Any) -> None:
        """Insert documents into a ChromaDB collection."""
        client = self._get_client()
        col = client.get_collection(self._collection_name(collection))
        col.add(
            ids=[doc.id for doc in documents],
            embeddings=[doc.vector for doc in documents],
            documents=[doc.text for doc in documents],
            metadatas=[doc.metadata for doc in documents],
        )
        logger.debug("chroma_documents_inserted", collection=collection, count=len(documents))

    async def search(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 10,
        score_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> List[SearchResult]:
        """Run a similarity search against a ChromaDB collection."""
        client = self._get_client()
        col = client.get_collection(self._collection_name(collection))
        query_kwargs: Dict[str, Any] = {"query_embeddings": [query_vector], "n_results": top_k}
        if filters:
            query_kwargs["where"] = filters
        results = col.query(**query_kwargs)
        search_results: List[SearchResult] = []
        if not results["ids"]:
            return search_results
        for idx, doc_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][idx] if results.get("distances") else 0.0
            score = 1.0 - distance
            if score >= score_threshold:
                search_results.append(
                    SearchResult(
                        id=doc_id,
                        text=results["documents"][0][idx] if results.get("documents") else "",
                        score=score,
                        metadata=results["metadatas"][0][idx] if results.get("metadatas") else {},
                    )
                )
        return search_results

    async def delete(self, collection: str, document_ids: List[str], **kwargs: Any) -> None:
        """Delete documents by ID from a ChromaDB collection."""
        client = self._get_client()
        col = client.get_collection(self._collection_name(collection))
        col.delete(ids=document_ids)
        logger.debug("chroma_documents_deleted", collection=collection, count=len(document_ids))

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            client.heartbeat()
            return True
        except Exception as exc:
            logger.warning("chroma_health_check_failed", error=str(exc))
            return False
