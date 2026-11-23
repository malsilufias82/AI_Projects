from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import BaseService


class UserService(BaseService[User, UserRepository]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        repository = UserRepository(session)
        super().__init__(repository)

    async def create_user(self, data: UserCreate) -> User:
        if await self.repository.exists(email=data.email):
            raise ConflictException(
                f"User with email '{data.email}' already exists."
            )
        return await self.repository.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.repository.get_by_email(email)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repository.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedException("User account is inactive.")
        return user

    async def update_user(self, id: UUID, data: UserUpdate) -> User:
        user = await self.repository.get_by_id(id)
        if not user:
            raise NotFoundException(f"User '{id}' not found.")
        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repository.update(id, **update_data)
        if not updated:
            raise NotFoundException(f"User '{id}' not found.")
        return updated

    async def deactivate_user(self, id: UUID) -> User:
        user = await self.repository.get_by_id(id)
        if not user:
            raise NotFoundException(f"User '{id}' not found.")
        updated = await self.repository.update(id, is_active=False)
        if not updated:
            raise NotFoundException(f"User '{id}' not found.")
        return updated
