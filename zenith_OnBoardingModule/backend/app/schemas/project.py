from typing import Optional, List
from pydantic import BaseModel, Field


class ProjectPOCCreate(BaseModel):
    """Point of Contact details for creating a project."""
    
    name: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)


class ProjectPOCResponse(BaseModel):
    """Point of Contact details for response."""
    
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class ProjectCreate(BaseModel):
    """Project creation request."""
    
    name: str = Field(..., max_length=255)
    client_id: str = Field(..., description="Reference to client document ID")
    pocs: List[ProjectPOCCreate] = Field(default_factory=list)
    description: Optional[str] = Field(None, max_length=1000)
    status: str = Field(default="active")
    start_date: Optional[str] = Field(None)
    end_date: Optional[str] = Field(None)
    team_lead: Optional[str] = Field(None, max_length=255)
    pillar: Optional[str] = Field(None, max_length=255)


class ProjectUpdate(BaseModel):
    """Project update request."""
    
    name: Optional[str] = Field(None, max_length=255)
    client_id: Optional[str] = None
    pocs: Optional[List[ProjectPOCCreate]] = None
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_lead: Optional[str] = Field(None, max_length=255)
    pillar: Optional[str] = Field(None, max_length=255)


class ProjectResponse(BaseModel):
    """Project response."""
    
    id: str
    name: str
    client_id: str
    pocs: List[ProjectPOCResponse] = Field(default_factory=list)
    description: Optional[str] = None
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    team_lead: Optional[str] = None
    pillar: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
