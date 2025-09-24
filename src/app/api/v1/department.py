from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.user import get_current_auth_user
from app.core.config import settings
from app.core.db import TransactionSessionDep
from app.dao.department import DepartmentDAO
from app.schemas import DataResponse, PaginatedListResponse, get_pagination
from app.schemas.department import (
    DepartmentCreate,
    DepartmentFilter,
    DepartmentRead,
    DepartmentReadWithCount,
)
from app.schemas.user import UserRead

router = APIRouter(
    prefix=settings.api.v1.departments,
    tags=["Departments"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[DepartmentRead],
)
async def create_department(
    department: DepartmentCreate,
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    department = await DepartmentDAO.add(session=session, values=department)
    return DataResponse(
        data=department,
    )


@router.put(
    '/update/{department_id}',
    status_code=status.HTTP_200_OK,
    response_model=DataResponse[str],
)
async def update_department(
    department_id: int,
    department: DepartmentFilter,
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    count = await DepartmentDAO.update(session=session, filters=DepartmentFilter(id=department_id), values=department)
    return DataResponse(
        data=f"Updated {count} rows",
    )

@router.get(
    '/get_all',
    response_model=PaginatedListResponse[DepartmentReadWithCount],
)
async def get_departments(
    role_id: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    db_departments_count = await DepartmentDAO.count(
        session=session,
        filters=DepartmentFilter(
            role_id=role_id,
        ),
    )
    db_departments = await DepartmentDAO.get_departments_with_count(
        session=session,
        role_id=role_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedListResponse(
        data=db_departments,
        pagination=get_pagination(
            total_count=db_departments_count,
            page=page,
            page_size=page_size,
        ),
    )

