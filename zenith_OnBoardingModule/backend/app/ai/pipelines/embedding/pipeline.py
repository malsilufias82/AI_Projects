from typing import Any, Dict

from app.ai.pipelines.base import BasePipeline
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingPipeline(BasePipeline):
    """
    Embedding pipeline interface.

    Responsibilities:
    - Receive chunks from the chunking pipeline.
    - Generate vector embeddings via the configured provider.
    - Persist embeddings to the vector store.
    """

    pipeline_id: str = "embedding"

    async def validate(self, payload: Dict[str, Any]) -> bool:
        if "artifact_id" not in payload:
            raise ValueError("EmbeddingPipeline requires 'artifact_id'.")
        if "chunks" not in payload:
            raise ValueError("EmbeddingPipeline requires 'chunks'.")
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embeddings for each chunk and persist to the vector store.
        Embedding provider and vector store injected via config or DI.
        """
        artifact_id = payload["artifact_id"]
        chunks = payload["chunks"]
        logger.info("embedding_pipeline_execute", artifact_id=artifact_id, chunk_count=len(chunks))
        return {
            "artifact_id": artifact_id,
            "embedded_count": 0,
            "collection": self.config.get("collection", artifact_id),
        }

    async def on_success(self, output: Dict[str, Any]) -> None:
        logger.info(
            "embedding_pipeline_success",
            artifact_id=output.get("artifact_id"),
            embedded_count=output.get("embedded_count", 0),
        )

    async def on_failure(self, error: Exception, payload: Dict[str, Any]) -> None:
        logger.error("embedding_pipeline_failure", artifact_id=payload.get("artifact_id"), error=str(error))
