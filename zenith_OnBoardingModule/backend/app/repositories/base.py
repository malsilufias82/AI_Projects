from datetime import datetime, timezone
from typing import Any, Generic, Optional, Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(
                and_(
                    self.model.id == id,
                    self.model.is_deleted == False,  # noqa: E712
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[list] = None,
    ) -> Sequence[ModelType]:
        stmt = select(self.model).where(
            self.model.is_deleted == False  # noqa: E712
        )
        if filters:
            stmt = stmt.where(and_(*filters))
        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, filters: Optional[list] = None) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.is_deleted == False)  # noqa: E712
        )
        if filters:
            stmt = stmt.where(and_(*filters))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update(self, id: UUID, **kwargs: Any) -> Optional[ModelType]:
        await self.session.execute(
            update(self.model)
            .where(
                and_(
                    self.model.id == id,
                    self.model.is_deleted == False,  # noqa: E712
                )
            )
            .values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

    async def soft_delete(self, id: UUID) -> Optional[ModelType]:
        return await self.update(
            id,
            is_deleted=True,
            deleted_at=datetime.now(timezone.utc),
        )

    async def exists(self, **kwargs: Any) -> bool:
        conditions = [getattr(self.model, k) == v for k, v in kwargs.items()]
        stmt = (
            select(func.count())
            .select_from(self.model)
            .where(and_(*conditions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[list] = None,
    ) -> tuple[Sequence[ModelType], int]:
        skip = (page - 1) * page_size
        items = await self.get_all(skip=skip, limit=page_size, filters=filters)
        total = await self.count(filters=filters)
        return items, total
