from math import ceil
from typing import Generic, List, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedResult(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta


def paginate(
    items: Sequence[T],
    total: int,
    page: int,
    page_size: int,
) -> PaginatedResult[T]:
    total_pages = ceil(total / page_size) if page_size > 0 else 0
    return PaginatedResult(
        items=list(items),
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        ),
    )
