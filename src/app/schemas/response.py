from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

SchemaType = TypeVar("SchemaType")


class DataResponse(BaseModel, Generic[SchemaType]):
    data: SchemaType


class ListResponse(BaseModel, Generic[SchemaType]):
    data: list[SchemaType]
    total: int


class Pagination(BaseModel):
    page: Optional[int] = None
    items_per_page: Optional[int] = None
    total: Optional[int] = None
    total_pages: Optional[int] = None


class PaginatedListResponse(BaseModel, Generic[SchemaType]):
    data: list[SchemaType]
    pagination: Pagination


def get_pagination(
    total_count: int,
    page: int,
    page_size: int,
) -> Pagination:
    """
    Создает объект пагинации на основе общего количества элементов, текущей страницы и размера страницы.

    Args:
        total_count: Общее количество элементов
        page: Текущая страница
        page_size: Размер страницы

    Returns:
        Pagination: Объект с информацией о пагинации
    """

    return Pagination(
        page=page,
        items_per_page=page_size,
        total=total_count or 0,
        total_pages=total_count // page_size
        + (1 if total_count % page_size > 0 else 0),
    )
