from typing import Optional, List
from pydantic import BaseModel, Field


class ContactPersonCreate(BaseModel):
    """Contact person details for creating a client."""
    
    name: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)


class ContactPersonResponse(BaseModel):
    """Contact person details for response."""
    
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class ClientCreate(BaseModel):
    """Client creation request."""
    
    name: str = Field(..., max_length=255)
    contact_persons: List[ContactPersonCreate] = Field(default_factory=list)
    address: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="active")
    description: Optional[str] = Field(None, max_length=1000)


class ClientUpdate(BaseModel):
    """Client update request."""
    
    name: Optional[str] = Field(None, max_length=255)
    contact_persons: Optional[List[ContactPersonCreate]] = None
    address: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)


class ClientResponse(BaseModel):
    """Client response."""
    
    id: str
    name: str
    contact_persons: List[ContactPersonResponse] = Field(default_factory=list)
    address: Optional[str] = None
    status: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
