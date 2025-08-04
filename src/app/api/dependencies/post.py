from fastapi import (
    Depends,
)

from app.core.db import SessionDep
from app.core.exceptions import NotFoundException
from app.dao.post import PostDAO
from app.schemas.post import PostFilter
from app.schemas.user import UserRead

from .user import get_current_auth_user


async def validate_post_owner_by_id(
    post_id: int,
    current_user: UserRead = Depends(get_current_auth_user),
    session=SessionDep,
):
    post = await PostDAO.find_one_or_none(
        session=session,
        filters=PostFilter(
            id=post_id,
            user_id=current_user.id,
        ),
    )
    if not post:
        raise NotFoundException(
            message="Post not found",
        )
    return post
