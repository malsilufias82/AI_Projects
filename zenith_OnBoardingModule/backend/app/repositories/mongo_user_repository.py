from typing import Optional, Sequence

from app.models.mongo_user import User, UserRole
from app.repositories.mongo_base import MongoBaseRepository


class MongoUserRepository(MongoBaseRepository):
    """MongoDB repository for User operations."""

    def __init__(self) -> None:
        super().__init__("users")

    async def get_by_email(self, email: str) -> Optional[dict]:
        """Get a user by email address."""
        return await self.find_one({"email": email})

    async def get_by_role(
        self, role: UserRole, skip: int = 0, limit: int = 100
    ) -> Sequence[dict]:
        """Get users by role."""
        return await self.find_many(
            {"role": role.value, "is_active": True},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> Sequence[dict]:
        """Get all active users."""
        return await self.find_many(
            {"is_active": True},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )

    async def create(self, **kwargs) -> dict:
        """Create a new user."""
        return await super().create(kwargs)

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Get a user by ID."""
        return await super().get_by_id(id)

    async def update(self, id: str, **kwargs) -> Optional[dict]:
        """Update a user by ID."""
        return await super().update(id, kwargs)

    async def delete(self, id: str) -> bool:
        """Delete a user by ID."""
        return await super().delete(id)

    async def soft_delete(self, id: str) -> Optional[dict]:
        """Soft delete a user by ID."""
        return await super().soft_delete(id)

    async def exists(self, email: str) -> bool:
        """Check if a user with the given email exists."""
        return await super().exists({"email": email})
