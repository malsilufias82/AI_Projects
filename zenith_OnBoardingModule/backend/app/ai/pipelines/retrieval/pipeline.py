from typing import Any, Dict, List

from app.ai.pipelines.base import BasePipeline
from app.core.logging import get_logger

logger = get_logger(__name__)


class RetrievalPipeline(BasePipeline):
    """
    Retrieval pipeline interface.

    Responsibilities:
    - Embed a query using the configured embedding provider.
    - Perform vector similarity search against the target collection.
    - Return ranked, filtered results for context assembly.
    """

    pipeline_id: str = "retrieval"

    async def validate(self, payload: Dict[str, Any]) -> bool:
        if "query" not in payload:
            raise ValueError("RetrievalPipeline requires 'query'.")
        if "collection" not in payload:
            raise ValueError("RetrievalPipeline requires 'collection'.")
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Embed the query and retrieve top-k semantically similar chunks.
        Embedding provider and vector store injected via config or DI.
        """
        query = payload["query"]
        collection = payload["collection"]
        top_k = payload.get("top_k", self.config.get("top_k", 10))
        logger.info("retrieval_pipeline_execute", collection=collection, top_k=top_k)
        return {
            "query": query,
            "collection": collection,
            "results": [],
            "result_count": 0,
        }

    async def on_success(self, output: Dict[str, Any]) -> None:
        logger.info(
            "retrieval_pipeline_success",
            collection=output.get("collection"),
            result_count=output.get("result_count", 0),
        )

    async def on_failure(self, error: Exception, payload: Dict[str, Any]) -> None:
        logger.error("retrieval_pipeline_failure", query=payload.get("query"), error=str(error))
