from typing import Any, Optional

from app.ai.context.models import ContextAssemblyRequest, RetrievalContext
from app.ai.context.window import ContextWindow
from app.ai.providers.vector_db.base import BaseVectorStore
from app.core.logging import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """
    Assembles a RetrievalContext for a given evaluator query.

    Workflow:
    1. Embed the query using the configured embedding provider.
    2. Run semantic search against the vector store.
    3. Fill a ContextWindow respecting the token budget.
    4. Return a structured RetrievalContext.
    """

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        embedding_provider: Optional[Any] = None,
        max_tokens: int = 8192,
    ) -> None:
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.max_tokens = max_tokens

    async def build(self, request: ContextAssemblyRequest) -> RetrievalContext:
        """
        Build and return a RetrievalContext for the given request.
        Falls back to an empty context if providers are not configured.
        """
        if self.embedding_provider is None or self.vector_store is None:
            logger.warning(
                "context_builder_no_providers",
                evaluator_id=request.evaluator_id,
            )
            return RetrievalContext(
                evaluator_id=request.evaluator_id,
                query=request.query,
            )

        embedding_resp = await self.embedding_provider.embed_text(request.query)
        search_results = await self.vector_store.search(
            collection=request.collection,
            query_vector=embedding_resp.vector,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            filters=request.filters,
        )

        window = ContextWindow(max_tokens=request.max_tokens)
        from app.ai.context.models import ChunkReference

        for idx, result in enumerate(search_results):
            chunk = ChunkReference(
                chunk_id=result.id,
                artifact_id=request.artifact_id,
                content=result.text,
                score=result.score,
                index=idx,
                metadata=result.metadata,
            )
            if not window.try_add(chunk):
                break

        logger.info(
            "context_built",
            evaluator_id=request.evaluator_id,
            chunks_added=len(window),
            tokens_used=window.used_tokens,
            truncated=window.is_full and len(search_results) > len(window),
        )

        return RetrievalContext(
            evaluator_id=request.evaluator_id,
            query=request.query,
            chunks=window.get_chunks(),
            total_tokens=window.used_tokens,
            truncated=window.is_full and len(search_results) > len(window),
        )
