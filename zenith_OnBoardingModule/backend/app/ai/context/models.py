from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChunkReference(BaseModel):
    """A reference to a specific chunk used in context assembly."""

    chunk_id: str
    artifact_id: str
    content: str
    score: float = 0.0
    index: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievalContext(BaseModel):
    """Context assembled from retrieved chunks for a single evaluator."""

    evaluator_id: str
    query: str
    chunks: List[ChunkReference] = Field(default_factory=list)
    total_tokens: int = 0
    truncated: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextAssemblyRequest(BaseModel):
    """Request model for the ContextBuilder."""

    evaluator_id: str
    query: str
    artifact_id: str
    collection: str
    top_k: int = 10
    max_tokens: int = 8192
    score_threshold: float = 0.7
    filters: Optional[Dict[str, Any]] = None
