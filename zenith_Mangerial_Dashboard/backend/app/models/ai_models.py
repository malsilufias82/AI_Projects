import enum
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


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


class AIJob(UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Represents a single AI processing job."""

    __tablename__ = "ai_jobs"

    job_type: Mapped[str] = mapped_column(
        Enum(AIJobType, name="ai_job_type_enum"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum(AIJobStatus, name="ai_job_status_enum"),
        nullable=False,
        default=AIJobStatus.PENDING,
        index=True,
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)

    workflow_executions: Mapped[list["AIWorkflowExecution"]] = relationship(
        "AIWorkflowExecution", back_populates="job", lazy="select"
    )

    __table_args__ = (
        Index("ix_ai_jobs_status_type", "status", "job_type"),
    )


class AIWorkflowExecution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks a single LangGraph workflow execution for an AI job."""

    __tablename__ = "ai_workflow_executions"

    job_id: Mapped[str] = mapped_column(
        ForeignKey("ai_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workflow_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        Enum(WorkflowStatus, name="workflow_status_enum"),
        nullable=False,
        default=WorkflowStatus.PENDING,
        index=True,
    )
    state_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    completed_nodes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    failed_nodes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    job: Mapped["AIJob"] = relationship("AIJob", back_populates="workflow_executions")
    evaluator_executions: Mapped[list["EvaluatorExecution"]] = relationship(
        "EvaluatorExecution", back_populates="workflow_execution", lazy="select"
    )


class EvaluatorExecution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Records a single evaluator run within a workflow execution."""

    __tablename__ = "evaluator_executions"

    workflow_execution_id: Mapped[str] = mapped_column(
        ForeignKey("ai_workflow_executions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evaluator_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    evaluator_type: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    findings: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    workflow_execution: Mapped["AIWorkflowExecution"] = relationship(
        "AIWorkflowExecution", back_populates="evaluator_executions"
    )


class PromptVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores versioned prompt templates for audit and reproducibility."""

    __tablename__ = "prompt_versions"

    template_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_prompt_versions_template_version", "template_id", "version", unique=True),
    )


class EmbeddingMetadata(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks embedding generation metadata for each artifact chunk."""

    __tablename__ = "embedding_metadata"

    artifact_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    chunk_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    collection: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    embedding_model: Mapped[str] = mapped_column(String(128), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    chunk_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_embedding_metadata_artifact_chunk", "artifact_id", "chunk_id", unique=True),
    )
