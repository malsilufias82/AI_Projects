from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(
                and_(
                    User.email == email,
                    User.is_deleted == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> Sequence[User]:
        result = await self.session.execute(
            select(User)
            .where(
                and_(
                    User.role == role,
                    User.is_active == True,  # noqa: E712
                    User.is_deleted == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> Sequence[User]:
        result = await self.session.execute(
            select(User)
            .where(
                and_(
                    User.is_active == True,  # noqa: E712
                    User.is_deleted == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
