import enum
from typing import Optional
from pydantic import Field

from app.models.mongo_base import MongoBaseModel, SoftDeleteMixin, TimestampMixin


class PermissionAction(str, enum.Enum):
    VIEW = "view"
    MODIFY = "modify"
    ADD = "add"
    DELETE = "delete"


class Permission(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB Permission model."""
    
    page: str = Field(..., index=True)
    display_name: str = Field(...)
    category: str = Field(..., index=True)
    icon: str = Field(...)
    route: str = Field(...)
    order: int = Field(...)
    enabled: bool = Field(default=True)
    action: PermissionAction = Field(...)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        collection_name = "permissions"
        json_schema_extra = {
            "example": {
                "page": "home",
                "display_name": "Home",
                "category": "main",
                "icon": "home",
                "route": "/",
                "order": 1,
                "enabled": True,
                "action": "view",
                "description": "Can view home page"
            }
        }
