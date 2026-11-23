from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIJobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIJobType(str, Enum):
    EVALUATION = "evaluation"
    EMBEDDING = "embedding"
    INGESTION = "ingestion"
    RETRIEVAL = "retrieval"
    ORCHESTRATION = "orchestration"


class AIJobCreate(BaseModel):
    """Schema for creating a new AI job."""

    job_type: AIJobType
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIJobResponse(BaseModel):
    """Schema for AI job API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_type: AIJobType
    status: AIJobStatus
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int
    progress: float = Field(ge=0.0, le=1.0, default=0.0)
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AIJobProgressUpdate(BaseModel):
    """Payload for streaming job progress updates."""

    progress: float = Field(ge=0.0, le=1.0)
    message: str
    current_node: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIJobCancelRequest(BaseModel):
    reason: Optional[str] = None
