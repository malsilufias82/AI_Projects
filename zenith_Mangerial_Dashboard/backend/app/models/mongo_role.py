from typing import Optional
from pydantic import Field

from app.models.mongo_base import MongoBaseModel, SoftDeleteMixin, TimestampMixin


class Role(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB Role model for permission groups."""
    
    name: str = Field(..., unique=True, index=True, max_length=100)
    display_name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    permissions: list[str] = Field(default_factory=list)  # List of permission IDs
    is_system: bool = Field(default=False)  # System roles cannot be deleted
    is_default: bool = Field(default=False)  # Default role for new users

    class Config:
        collection_name = "roles"
        json_schema_extra = {
            "example": {
                "name": "admin",
                "display_name": "Administrator",
                "description": "Full system access",
                "permissions": ["permission_id_1", "permission_id_2"],
                "is_system": True,
                "is_default": False
            }
        }
