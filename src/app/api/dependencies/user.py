import logging

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.helpers import ACCESS_TOKEN_TYPE
from app.core.auth.validation import (
    get_current_token_payload,
    get_current_token_payload_for_optional_user,
    get_user_by_token_sub,
    validate_token_type,
)
from app.core.db import db_helper
from app.core.exceptions.http_exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from app.schemas.user import UserRead

logger = logging.getLogger(__name__)


class UserGetterFromToken:
    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        payload: dict = Depends(get_current_token_payload),
        session: AsyncSession = Depends(db_helper.session_getter),
    ):
        validate_token_type(payload, self.token_type)
        user = await get_user_by_token_sub(session, payload)
        if not user:
            raise UnauthorizedException(
                message="Inactive user",
            )
        return user


get_current_auth_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)


async def get_current_active_auth_user(
    user: UserRead = Depends(get_current_auth_user),
):
    if user.is_active:
        return user
    raise UnauthorizedException(
        message="Inactive user",
    )


async def get_current_superuser(
    user: UserRead = Depends(get_current_auth_user),
):
    if user.is_superuser:
        return user
    raise ForbiddenException(
        message="User is not superuser",
    )


async def get_optional_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> dict | None:
    try:
        validate_token_type(payload, ACCESS_TOKEN_TYPE)
        user = await get_user_by_token_sub(
            session=session,
            payload=payload,
        )
        if not user:
            return None
        return user
    except HTTPException as http_exc:
        if http_exc.status_code != status.HTTP_401_UNAUTHORIZED:
            logger.exception(
                f"Unexpected HTTPException in get_optional_user: {http_exc.detail}"
            )
        return None
    except Exception as exc:
        logger.exception(
            f"Unexpected error in get_optional_user: {exc}",
        )
        return None


async def get_optional_active_auth_user(
    payload: dict = Depends(get_current_token_payload_for_optional_user),
    session: AsyncSession = Depends(db_helper.session_getter),
) -> dict | None:
    try:
        if not payload:
            return None
        validate_token_type(payload, ACCESS_TOKEN_TYPE)
        user = await get_user_by_token_sub(
            session=session,
            payload=payload,
        )
        if not user:
            return None
        return user
    except HTTPException as http_exc:
        if http_exc.status_code != status.HTTP_401_UNAUTHORIZED:
            logger.exception(
                f"Unexpected HTTPException in get_optional_user: {http_exc.detail}",
            )
        return None
    except Exception as exc:
        logger.exception(
            f"Unexpected error in get_optional_user: {exc}",
        )
        return None
