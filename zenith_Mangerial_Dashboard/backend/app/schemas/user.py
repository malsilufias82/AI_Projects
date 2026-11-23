from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field, field_validator

from app.models.mongo_base import SoftDeleteMixin
from app.models.mongo_user import UserRole
from app.schemas.base import BaseSchema


class UserBase(BaseSchema, SoftDeleteMixin):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    role: UserRole = UserRole.USER
    phone_number: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = "Active"
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    team_lead_id: Optional[str] = None
    role_description: Optional[str] = None
    work_location: Optional[str] = None
    employment_type: Optional[str] = None
    client: Optional[str] = None
    project: Optional[str] = None
    vlinker: Optional[str] = None
    dev_qa: Optional[str] = None
    onboarding: Optional[str] = None


class UserCreate(BaseSchema):
    email: EmailStr
    password: Optional[str] = None
    send_account_info: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = "Active"
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    team_lead_id: Optional[str] = None
    role: UserRole = UserRole.USER
    role_description: Optional[str] = None
    work_location: Optional[str] = None
    employment_type: Optional[str] = None
    client: Optional[str] = None
    project: Optional[str] = None
    vlinker: Optional[str] = None
    dev_qa: Optional[str] = None
    onboarding: Optional[str] = None


class UserUpdate(BaseSchema):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    phone_number: Optional[str] = None
    employee_id: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    team_lead_id: Optional[str] = None
    role_description: Optional[str] = None
    work_location: Optional[str] = None
    employment_type: Optional[str] = None
    client: Optional[str] = None
    project: Optional[str] = None
    vlinker: Optional[str] = None
    dev_qa: Optional[str] = None
    onboarding: Optional[str] = None


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
