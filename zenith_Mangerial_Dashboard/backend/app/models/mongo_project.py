import enum
from typing import Optional, List
from pydantic import Field, BaseModel

from app.models.mongo_base import MongoBaseModel, SoftDeleteMixin, TimestampMixin


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"


class ProjectPOC(BaseModel):
    """Point of Contact details for a project."""
    
    name: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100, description="e.g., Business Owner, Technical Sponsor")


class Project(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB Project model."""

    name: str = Field(..., max_length=255)
    client_id: str = Field(..., description="Reference to client document ID")
    pocs: List[ProjectPOC] = Field(default_factory=list, description="Points of Contact for this project")
    description: Optional[str] = Field(None, max_length=1000)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    start_date: Optional[str] = Field(None)
    end_date: Optional[str] = Field(None)
    team_lead: Optional[str] = Field(None, max_length=255, description="Team lead name or user ID")
    pillar: Optional[str] = Field(None, max_length=255)

    class Config:
        collection_name = "projects"
        json_schema_extra = {
            "example": {
                "name": "E-commerce Platform",
                "client_id": "507f1f77bcf86cd799439011",
                "pocs": [
                    {
                        "name": "John Smith",
                        "email": "john@acme.com",
                        "phone": "+1-555-0123",
                        "role": "Business Owner"
                    },
                    {
                        "name": "Jane Doe",
                        "email": "jane@acme.com",
                        "phone": "+1-555-0124",
                        "role": "Technical Sponsor"
                    }
                ],
                "description": "Building a modern e-commerce platform",
                "status": "active",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "team_lead": "John Doe",
                "pillar": "Engineering"
            }
        }
