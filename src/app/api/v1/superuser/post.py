from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies.user import get_current_superuser
from app.core.config import settings
from app.core.db import SessionDep
from app.core.exceptions import NotFoundException
from app.dao.post import PostDAO
from app.schemas import PaginatedListResponse, get_pagination
from app.schemas.post import PostFilter, PostRead

router = APIRouter(
    prefix=settings.api.v1.posts,
)


@router.get(
    "/{user_id}/list",
    response_model=PaginatedListResponse[PostRead],
)
async def get_user_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    session=SessionDep,
):
    db_posts_count = await PostDAO.count(
        session=session,
        filters=PostFilter(
            user_id=user_id,
        ),
    )
    db_posts = await PostDAO.paginate(
        session=session,
        filters=PostFilter(
            user_id=user_id,
        ),
        page=page,
        page_size=page_size,
        order_by="id",
        order_direction="desc",
    )
    return PaginatedListResponse(
        data=db_posts,
        pagination=get_pagination(
            total_count=db_posts_count,
            page=page,
            page_size=page_size,
        ),
    )


@router.delete(
    "/{user_id}/{post_id}/",
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user_post(
    user_id: int,
    post_id: int,
    session=SessionDep,
):
    db_post = await PostDAO.find_one_or_none(
        session=session,
        filters=PostFilter(
            user_id=user_id,
            id=post_id,
        ),
    )
    if db_post is None:
        raise NotFoundException(
            message="Post not found",
        )
    await PostDAO.delete(
        session=session,
        filters=PostFilter(
            id=post_id,
        ),
    )
