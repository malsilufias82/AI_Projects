import enum
from typing import Optional, List
from pydantic import Field, BaseModel

from app.models.mongo_base import MongoBaseModel, SoftDeleteMixin, TimestampMixin


class ClientStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class ContactPerson(BaseModel):
    """Contact person details for a client."""
    
    name: str = Field(..., max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100, description="e.g., Project Manager, Technical Lead")


class Client(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB Client model."""
    
    name: str = Field(..., max_length=255)
    contact_persons: List[ContactPerson] = Field(default_factory=list)
    address: Optional[str] = Field(None, max_length=500)
    status: ClientStatus = Field(default=ClientStatus.ACTIVE)
    description: Optional[str] = Field(None, max_length=1000)

    class Config:
        collection_name = "clients"
        json_schema_extra = {
            "example": {
                "name": "Acme Corporation",
                "contact_persons": [
                    {
                        "name": "John Smith",
                        "email": "john@acme.com",
                        "phone": "+1-555-0123",
                        "role": "Project Manager"
                    },
                    {
                        "name": "Jane Doe",
                        "email": "jane@acme.com",
                        "phone": "+1-555-0124",
                        "role": "Technical Lead"
                    }
                ],
                "address": "123 Business Ave, Suite 100",
                "status": "active",
                "description": "Technology solutions provider"
            }
        }
