from typing import Generic, Optional, Sequence, TypeVar
from uuid import UUID

from app.repositories.base import BaseRepository

ModelType = TypeVar("ModelType")
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(Generic[ModelType, RepositoryType]):
    def __init__(self, repository: RepositoryType) -> None:
        self.repository = repository

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        return await self.repository.get_by_id(id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        return await self.repository.get_all(skip=skip, limit=limit)

    async def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[list] = None,
    ) -> tuple[Sequence[ModelType], int]:
        return await self.repository.paginate(
            page=page, page_size=page_size, filters=filters
        )

    async def delete(self, id: UUID) -> bool:
        return await self.repository.delete(id)

    async def soft_delete(self, id: UUID) -> Optional[ModelType]:
        return await self.repository.soft_delete(id)

    async def exists(self, **kwargs) -> bool:
        return await self.repository.exists(**kwargs)
