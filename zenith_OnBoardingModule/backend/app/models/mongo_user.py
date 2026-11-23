import enum
from typing import Optional
from pydantic import Field, EmailStr

from app.models.mongo_base import MongoBaseModel, SoftDeleteMixin, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(MongoBaseModel, TimestampMixin, SoftDeleteMixin):
    """MongoDB User model."""
    
    email: EmailStr = Field(..., unique=True, index=True)
    hashed_password: Optional[str] = Field(None)
    password_set: bool = Field(default=False)
    first_name: Optional[str] = Field(None, max_length=255)
    last_name: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)
    is_team_lead: bool = Field(default=False)

    class Config:
        collection_name = "users"
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "hashed_password": "hashed_password_here",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "role": "user"
            }
        }
