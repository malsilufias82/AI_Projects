from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class FindingSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    """A single evaluator finding."""

    title: str
    description: str
    severity: FindingSeverity
    location: Optional[str] = None
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseEvaluationResult(BaseModel):
    """Minimum result contract every evaluator must satisfy."""

    evaluator_id: str
    evaluator_type: str
    status: EvaluationStatus
    score: Optional[float] = Field(None, ge=0.0, le=1.0)
    findings: List[Finding] = Field(default_factory=list)
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[int] = None
    references: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None


class EvaluatorResult(BaseEvaluationResult):
    """Full evaluator result including raw LLM output."""

    raw_output: Optional[Dict[str, Any]] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None


class AggregatedEvaluationResult(BaseModel):
    """Unified result combining all evaluator outputs for a single job."""

    job_id: UUID
    workflow_execution_id: UUID
    overall_status: EvaluationStatus
    overall_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    evaluator_results: List[EvaluatorResult] = Field(default_factory=list)
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    execution_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    completed_at: Optional[datetime] = None
