from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, Sequence
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowNodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowState(BaseModel):
    """
    LangGraph-compatible workflow state model.
    Tracks execution progress across graph nodes.
    """

    workflow_id: str
    job_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_node: Optional[str] = None
    completed_nodes: List[str] = Field(default_factory=list)
    failed_nodes: List[str] = Field(default_factory=list)
    node_results: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    retry_count: int = 0


class WorkflowNodeConfig(BaseModel):
    """Configuration for a single graph node."""

    node_id: str
    node_type: str
    retry_limit: int = 3
    timeout_seconds: int = 300
    dependencies: List[str] = Field(default_factory=list)
    parallel_group: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    """Full workflow blueprint used to construct a LangGraph StateGraph."""

    workflow_id: str
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNodeConfig] = Field(default_factory=list)
    entry_point: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionSummary(BaseModel):
    """Lightweight execution summary returned to callers."""

    execution_id: UUID
    workflow_id: str
    job_id: str
    status: WorkflowStatus
    completed_nodes: List[str] = Field(default_factory=list)
    failed_nodes: List[str] = Field(default_factory=list)
    error: Optional[str] = None
