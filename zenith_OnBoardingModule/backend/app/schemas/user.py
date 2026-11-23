from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from app.models.mongo_user import UserRole
from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: UserRole = UserRole.USER


class UserCreate(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_id(cls, v):
        """Convert MongoDB _id to id field."""
        if isinstance(v, dict) and '_id' in v:
            return str(v['_id'])
        return str(v) if v is not None else None


class UserInDB(UserResponse):
    hashed_password: str
