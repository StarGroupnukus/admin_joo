from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import (
    get_current_active_auth_user,
    rate_limiter,
    validate_post_owner_by_id,
)
from app.core.config import settings
from app.core.db import TransactionSessionDep
from app.core.exceptions import NotFoundException
from app.dao.post import PostDAO
from app.schemas import (
    DataResponse,
    PaginatedListResponse,
    get_pagination,
)
from app.schemas.post import (
    PostCreate,
    PostCreateInternal,
    PostFilter,
    PostRead,
    PostUpdate,
    PostUpdateInternal,
)
from app.schemas.user import UserRead

router = APIRouter(
    prefix=settings.api.v1.posts,
    tags=["Posts"],
)


@router.get(
    "/list",
    response_model=PaginatedListResponse[PostRead],
)
async def get_my_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    db_posts_count = await PostDAO.count(
        session=session,
        filters=PostFilter(
            user_id=current_user.id,
        ),
    )
    db_posts = await PostDAO.paginate(
        session=session,
        filters=PostFilter(
            user_id=current_user.id,
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter)],
    response_model=DataResponse[PostRead],
)
async def create_post(
    create_post: PostCreate,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    post_values = PostCreateInternal(
        **create_post.model_dump(),
        user_id=current_user.id,
    )
    created_post = await PostDAO.add(
        session=session,
        values=post_values,
    )
    print(created_post)
    return DataResponse(
        data=created_post,
    )


@router.put(
    "/{post_id}",
    response_model=DataResponse[PostRead],
)
async def update_post(
    update_post: PostUpdate,
    post: PostRead = Depends(validate_post_owner_by_id),
    session=TransactionSessionDep,
):
    if post is None:
        raise NotFoundException(
            message="Post not found",
        )

    update_internal = PostUpdateInternal(
        **update_post.model_dump(
            exclude_none=True,
            exclude_unset=True,
        ),
        updated_at=datetime.now(UTC),
    )

    await PostDAO.update(
        session=session,
        values=update_internal,
        filters=PostFilter(
            id=post.id,
        ),
    )
    updated_post = await PostDAO.find_one_or_none(
        session=session,
        filters=PostFilter(
            id=post.id,
        ),
    )
    return DataResponse(
        data=updated_post,
    )


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_post(
    post: PostRead = Depends(validate_post_owner_by_id),
    session=TransactionSessionDep,
):
    post = await PostDAO.find_one_or_none_by_id(
        session=session,
        data_id=post.id,
    )
    if post is None:
        raise NotFoundException(
            message="Post not found",
        )

    await PostDAO.delete(
        session=session,
        filters=PostFilter(
            id=post.id,
        ),
    )
