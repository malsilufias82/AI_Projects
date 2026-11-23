from datetime import datetime
from typing import Optional
from pydantic import Field

from app.models.mongo_base import MongoBaseModel


class UserRole(MongoBaseModel):
    """MongoDB User-Role relationship model."""
    
    user_id: str = Field(..., index=True)
    role_id: str = Field(..., index=True)
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_by: Optional[str] = Field(None)

    class Config:
        collection_name = "user_roles"
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "role_id": "507f1f77bcf86cd799439012",
                "assigned_at": "2024-01-01T00:00:00",
                "assigned_by": "507f1f77bcf86cd799439013"
            }
        }
