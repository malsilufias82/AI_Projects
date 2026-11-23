from typing import Optional

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.services.email_service import send_account_setup_email
from app.models.mongo_user import User
from app.repositories.mongo_user_repository import MongoUserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class MongoUserService(BaseService):
    """MongoDB-based user service."""

    def __init__(self) -> None:
        self.repository = MongoUserRepository()

    async def create_user(self, data: UserCreate) -> dict:
        """Create a new user."""
        if await self.repository.exists(email=data.email):
            raise ConflictException(
                f"User with email '{data.email}' already exists."
            )
        user_dict = data.model_dump(exclude_unset=True, exclude={"password", "send_account_info"})
        if data.password:
            user_dict["hashed_password"] = hash_password(data.password)
        else:
            user_dict["hashed_password"] = None

        created = await self.repository.create(**user_dict)

        if getattr(data, "send_account_info", False):
            user_id = str(created["_id"])
            recipient_name = f"{data.first_name or ''} {data.last_name or ''}".strip() or data.email.split("@")[0]
            reset_url = f"{settings.FRONTEND_URL}/set-password?token={user_id}"
            send_account_setup_email(to=data.email, recipient_name=recipient_name, setup_url=reset_url)
        return created

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get a user by email."""
        return await self.repository.get_by_email(email)

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Get a user by ID."""
        return await self.repository.get_by_id(id)

    async def authenticate(self, email: str, password: str) -> dict:
        """Authenticate a user with email and password."""
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user["hashed_password"]):
            raise UnauthorizedException("Invalid email or password.")
        if not user.get("is_active", True):
            raise UnauthorizedException("User account is inactive.")
        return user

    async def update_user(self, id: str, data: UserUpdate) -> dict:
        """Update a user."""
        user = await self.repository.get_by_id(id)
        if not user:
            raise NotFoundException(f"User '{id}' not found.")
        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repository.update(id, **update_data)
        if not updated:
            raise NotFoundException(f"User '{id}' not found.")
        return updated

    async def deactivate_user(self, id: str) -> dict:
        """Deactivate a user."""
        user = await self.repository.get_by_id(id)
        if not user:
            raise NotFoundException(f"User '{id}' not found.")
        updated = await self.repository.update(id, is_active=False)
        if not updated:
            raise NotFoundException(f"User '{id}' not found.")
        return updated

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list:
        """Get all users."""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def delete_user(self, id: str) -> bool:
        """Delete a user."""
        user = await self.repository.get_by_id(id)
        if not user:
            raise NotFoundException(f"User '{id}' not found.")
        return await self.repository.delete(id)
