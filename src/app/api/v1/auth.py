from fastapi import APIRouter, Depends, status
from jwt import InvalidTokenError

from app.api.dependencies.user import get_current_auth_user
from app.core.auth import (
    REFRESH_TOKEN_TYPE,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_refresh_token_payload,
    get_user_by_token_sub,
    validate_token_type,
)
from app.core.config import settings
from app.core.db import SessionDep, TransactionSessionDep
from app.core.exceptions import (
    UnauthorizedException,
)
from app.dao.token_blacklist import TokenBlacklistDAO
from app.dao.user import UserDAO
from app.schemas.response import DataResponse
from app.schemas.token_blacklist import RefreshToken, TokenInfo
from app.schemas.user import (
    LoginViaPhone,
)

REFRESH_TOKEN_KEY = "refresh_token"
router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


@router.post(
    "/login",
    response_model=DataResponse[TokenInfo],
)
async def login_user(
    login_data: LoginViaPhone,
    session=SessionDep,
):
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=login_data.phone_number,
    )
    if not db_user:
        raise UnauthorizedException(
            message="User not found",
        )
    if db_user and (not db_user.is_active or not db_user.is_verified):
        raise UnauthorizedException(
            message="User is inactive",
        )
    db_user = await authenticate_user(
        phone_number=login_data.phone_number,
        password=login_data.password,
        session=session,
    )
    if not db_user:
        raise UnauthorizedException(
            message="Invalid credentials",
        )
    access_token = await create_access_token(db_user)
    refresh_token = await create_refresh_token(db_user)

    return DataResponse(
        data=TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
        ),
    )


@router.post(
    "/logout",
    dependencies=[Depends(get_current_auth_user)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout_user(
    refresh_token_data: RefreshToken,
    session=TransactionSessionDep,
):
    try:
        token = refresh_token_data.refresh_token
        if not token:
            raise UnauthorizedException(
                message="Refresh token is missing",
            )
        await TokenBlacklistDAO.add_to_blacklist(
            session=session,
            token=token,
        )

    except InvalidTokenError:
        raise UnauthorizedException(
            message="Invalid token",
        )


@router.post(
    "/refresh",
    response_model=DataResponse[TokenInfo],
    status_code=status.HTTP_201_CREATED,
)
async def refresh_access_token(
    refresh_token_data: RefreshToken,
    session=SessionDep,
):
    token = refresh_token_data.refresh_token
    if not token:
        raise UnauthorizedException(
            message="Refresh token is missing",
        )
    payload = await get_refresh_token_payload(
        session=session,
        refresh_token=token,
    )
    validate_token_type(payload, REFRESH_TOKEN_TYPE)
    db_user = await get_user_by_token_sub(
        session=session,
        payload=payload,
    )
    new_access_token = await create_access_token(db_user)
    return DataResponse(
        data=TokenInfo(
            access_token=new_access_token,
            token_type="Bearer",
        ),
    )
