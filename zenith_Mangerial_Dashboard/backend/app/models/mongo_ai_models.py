import enum
from typing import Any, Optional
from pydantic import Field

from app.models.mongo_base import MongoBaseModel, TimestampMixin, SoftDeleteMixin


class AIJobStatus(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIJobType(str, enum.Enum):
    EVALUATION = "evaluation"
    EMBEDDING = "embedding"
    INGESTION = "ingestion"
    RETRIEVAL = "retrieval"
    ORCHESTRATION = "orchestration"


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIJob(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB AIJob model."""
    
    job_type: AIJobType = Field(..., index=True)
    status: AIJobStatus = Field(default=AIJobStatus.PENDING, index=True)
    priority: int = Field(default=5)
    payload: dict[str, Any] = Field(default_factory=dict)
    result: Optional[dict[str, Any]] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    progress: float = Field(default=0.0)
    celery_task_id: Optional[str] = Field(default=None, index=True)

    class Config:
        collection_name = "ai_jobs"
        json_schema_extra = {
            "example": {
                "job_type": "evaluation",
                "status": "pending",
                "priority": 5,
                "payload": {"project_id": "123"},
                "result": None,
                "error_message": None,
                "retry_count": 0,
                "progress": 0.0,
                "celery_task_id": None
            }
        }


class AIWorkflowExecution(MongoBaseModel, TimestampMixin):
    """MongoDB AIWorkflowExecution model."""
    
    job_id: str = Field(..., index=True)
    workflow_id: str = Field(..., index=True)
    status: WorkflowStatus = Field(default=WorkflowStatus.PENDING, index=True)
    state_snapshot: Optional[dict[str, Any]] = Field(default=None)
    completed_nodes: list = Field(default_factory=list)
    failed_nodes: list = Field(default_factory=list)
    error: Optional[str] = Field(default=None)

    class Config:
        collection_name = "ai_workflow_executions"
        json_schema_extra = {
            "example": {
                "job_id": "job_id_here",
                "workflow_id": "workflow_id_here",
                "status": "pending",
                "state_snapshot": None,
                "completed_nodes": [],
                "failed_nodes": [],
                "error": None
            }
        }


class EvaluatorExecution(MongoBaseModel, TimestampMixin):
    """MongoDB EvaluatorExecution model."""
    
    workflow_execution_id: str = Field(..., index=True)
    evaluator_id: str = Field(..., index=True)
    evaluator_type: str = Field(...)
    status: str = Field(default="pending")
    score: Optional[float] = Field(default=None)
    findings: list = Field(default_factory=list)
    summary: Optional[str] = Field(default=None)
    raw_output: Optional[dict[str, Any]] = Field(default=None)
    execution_time_ms: Optional[int] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    prompt_tokens: Optional[int] = Field(default=None)
    completion_tokens: Optional[int] = Field(default=None)

    class Config:
        collection_name = "evaluator_executions"
        json_schema_extra = {
            "example": {
                "workflow_execution_id": "workflow_exec_id",
                "evaluator_id": "evaluator_id",
                "evaluator_type": "code_quality",
                "status": "pending",
                "score": None,
                "findings": [],
                "summary": None,
                "raw_output": None,
                "execution_time_ms": None,
                "error_message": None,
                "prompt_tokens": None,
                "completion_tokens": None
            }
        }


class PromptVersion(MongoBaseModel, TimestampMixin):
    """MongoDB PromptVersion model."""
    
    template_id: str = Field(..., index=True)
    version: str = Field(...)
    template: str = Field(...)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    extra_metadata: Optional[dict[str, Any]] = Field(default=None)

    class Config:
        collection_name = "prompt_versions"
        indexes = [
            {"keys": [("template_id", 1), ("version", 1)], "unique": True}
        ]
        json_schema_extra = {
            "example": {
                "template_id": "template_123",
                "version": "v1.0",
                "template": "Your prompt here",
                "description": "Initial version",
                "is_active": True,
                "extra_metadata": {}
            }
        }


class EmbeddingMetadata(MongoBaseModel, TimestampMixin):
    """MongoDB EmbeddingMetadata model."""
    
    artifact_id: str = Field(..., index=True)
    chunk_id: str = Field(..., index=True)
    collection: str = Field(..., index=True)
    embedding_model: str = Field(...)
    embedding_provider: str = Field(...)
    dimension: int = Field(...)
    token_count: Optional[int] = Field(default=None)
    content_hash: Optional[str] = Field(default=None, max_length=64)
    chunk_metadata: Optional[dict[str, Any]] = Field(default=None)

    class Config:
        collection_name = "embedding_metadata"
        indexes = [
            {"keys": [("artifact_id", 1), ("chunk_id", 1)], "unique": True}
        ]
        json_schema_extra = {
            "example": {
                "artifact_id": "artifact_123",
                "chunk_id": "chunk_456",
                "collection": "documents",
                "embedding_model": "text-embedding-ada-002",
                "embedding_provider": "openai",
                "dimension": 1536,
                "token_count": 100,
                "content_hash": "abc123",
                "chunk_metadata": {}
            }
        }
