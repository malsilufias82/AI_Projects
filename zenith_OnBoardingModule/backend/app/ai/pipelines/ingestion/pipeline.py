from typing import Any, Dict

from app.ai.pipelines.base import BasePipeline
from app.core.logging import get_logger

logger = get_logger(__name__)


class IngestionPipeline(BasePipeline):
    """
    Ingestion pipeline interface.

    Responsibilities:
    - Receive uploaded artifacts (file paths, S3 keys, URLs).
    - Extract basic metadata (mime type, size, encoding).
    - Trigger downstream chunking/embedding pipelines.
    """

    pipeline_id: str = "ingestion"

    async def validate(self, payload: Dict[str, Any]) -> bool:
        if "artifact_id" not in payload:
            raise ValueError("IngestionPipeline requires 'artifact_id'.")
        if "source" not in payload:
            raise ValueError("IngestionPipeline requires 'source' (path, url, or s3_key).")
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from the artifact and return a structured ingestion record.
        Downstream: triggers chunking pipeline with the extracted content.
        """
        artifact_id = payload["artifact_id"]
        source = payload["source"]
        logger.info("ingestion_pipeline_execute", artifact_id=artifact_id, source=source)
        return {
            "artifact_id": artifact_id,
            "source": source,
            "metadata": {},
            "raw_content": None,
        }

    async def on_success(self, output: Dict[str, Any]) -> None:
        logger.info("ingestion_pipeline_success", artifact_id=output.get("artifact_id"))

    async def on_failure(self, error: Exception, payload: Dict[str, Any]) -> None:
        logger.error("ingestion_pipeline_failure", artifact_id=payload.get("artifact_id"), error=str(error))
