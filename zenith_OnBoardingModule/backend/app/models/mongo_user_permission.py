from datetime import datetime
from typing import Optional
from pydantic import Field

from app.models.mongo_base import MongoBaseModel


class UserPermission(MongoBaseModel):
    """MongoDB User-Permission relationship model."""
    
    user_id: str = Field(..., index=True)
    permission_id: str = Field(..., index=True)
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    granted_by: Optional[str] = Field(None)

    class Config:
        collection_name = "user_permissions"
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "permission_id": "507f1f77bcf86cd799439012",
                "granted_at": "2024-01-01T00:00:00",
                "granted_by": "507f1f77bcf86cd799439013"
            }
        }
