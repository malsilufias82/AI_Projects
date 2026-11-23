from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.ai.pipelines.base import BasePipeline
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Chunk:
    """Represents a single text chunk with metadata."""

    chunk_id: str
    artifact_id: str
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChunkingPipeline(BasePipeline):
    """
    Chunking pipeline interface.

    Responsibilities:
    - Split raw artifact content into semantically meaningful chunks.
    - Attach chunk metadata (position, source reference, strategy used).
    - Pass chunks to the embedding pipeline.
    """

    pipeline_id: str = "chunking"

    async def validate(self, payload: Dict[str, Any]) -> bool:
        if "artifact_id" not in payload:
            raise ValueError("ChunkingPipeline requires 'artifact_id'.")
        if "raw_content" not in payload:
            raise ValueError("ChunkingPipeline requires 'raw_content'.")
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Split content into chunks.
        Actual strategy (semantic, fixed-size, recursive) injected via config.
        """
        artifact_id = payload["artifact_id"]
        logger.info("chunking_pipeline_execute", artifact_id=artifact_id)
        return {
            "artifact_id": artifact_id,
            "chunks": [],
            "chunk_count": 0,
            "strategy": self.config.get("strategy", "semantic"),
        }

    async def on_success(self, output: Dict[str, Any]) -> None:
        logger.info(
            "chunking_pipeline_success",
            artifact_id=output.get("artifact_id"),
            chunk_count=output.get("chunk_count", 0),
        )

    async def on_failure(self, error: Exception, payload: Dict[str, Any]) -> None:
        logger.error("chunking_pipeline_failure", artifact_id=payload.get("artifact_id"), error=str(error))
