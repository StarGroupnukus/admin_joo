from fastapi import APIRouter, Query

from app.core.config import settings
from app.core.db import SessionDep
from app.core.exceptions import NotFoundException
from app.dao.user import UserDAO
from app.schemas import DataResponse, PaginatedListResponse, get_pagination
from app.schemas.user import UserFilter, UserRead

router = APIRouter(
    prefix=settings.api.v1.users,
)


@router.get(
    "/list",
    # dependencies=[Depends(get_current_superuser)],
    response_model=PaginatedListResponse[UserRead],
)
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=SessionDep,
):
    db_users_count = await UserDAO.count(
        session=session,
        filters=UserFilter(),
    )
    db_users = await UserDAO.paginate(
        session=session,
        filters=UserFilter(),
        page=page,
        page_size=page_size,
        order_by="id",
        order_direction="desc",
    )

    return PaginatedListResponse(
        data=db_users,
        pagination=get_pagination(
            total_count=db_users_count,
            page=page,
            page_size=page_size,
        ),
    )


@router.get(
    "/{user_id}",
    response_model=DataResponse[UserRead],
    # dependencies=[Depends(get_current_superuser)],
)
async def get_user(
    user_id: int,
    session=SessionDep,
):
    db_user: UserRead | None = await UserDAO.find_one_or_none_by_id(
        session=session,
        data_id=user_id,
    )
    if db_user is None:
        raise NotFoundException(
            message="User not found",
        )

    return DataResponse(
        data=db_user,
    )
