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
    hash_password,
    validate_token_type,
)
from app.core.config import settings
from app.core.db import SessionDep, TransactionSessionDep
from app.core.exceptions import (
    BadRequestException,
    DuplicateValueException,
    NotFoundException,
    TooManyRequestsException,
    UnauthorizedException,
)
from app.core.utils import redis_sms
from app.core.utils.send_sms import send_verification_sms
from app.dao.token_blacklist import TokenBlacklistDAO
from app.dao.user import UserDAO
from app.schemas.response import DataResponse
from app.schemas.token_blacklist import RefreshToken, TokenInfo
from app.schemas.user import (
    LoginViaPhone,
    UserCreate,
    UserCreateInternal,
    UserFilter,
    UserUpdateInternal,
    VerifyPhoneNumber,
)

REFRESH_TOKEN_KEY = "refresh_token"
router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[dict],
)
async def register_user(
    register_data: UserCreate,
    session=TransactionSessionDep,
):
    # Проверяем, существует ли партнер, до отправки SMS
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=register_data.phone_number,
    )
    print(db_user)
    # Если партнер уже существует и верифицирован/активен, возвращаем ошибку
    if db_user and (db_user.is_verified or db_user.is_active):
        raise DuplicateValueException(
            message="User already exists",
        )

    # Отправляем SMS только если нужно регистрировать партнера
    success, _ = await send_verification_sms(register_data.phone_number)
    if not success:
        raise TooManyRequestsException(
            message="Too many requests",
        )

    # Хешируем пароль один раз
    hashed_password = hash_password(register_data.password).decode("utf-8")

    # Подготавливаем общие данные для создания партнера
    user_create_data = UserCreateInternal(
        **register_data.model_dump(
            exclude={"password"},
            exclude_unset=True,
            exclude_none=True,
        ),
        hashed_password=hashed_password,
        is_active=False,
        is_verified=False,
    )

    # Если партнер существует, но не верифицирован и не активен - удаляем его
    if db_user:
        await UserDAO.delete(
            session=session,
            filters=UserFilter(id=db_user.id),
        )

    # Создаем нового партнера
    await UserDAO.add(
        session=session,
        values=user_create_data,
    )

    return DataResponse(
        data={
            "phone_number": register_data.phone_number,
        },
    )


@router.post(
    "/verify",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[TokenInfo],
)
async def verify_user(
    verify_data: VerifyPhoneNumber,
    session=TransactionSessionDep,
):
    success, _ = await redis_sms.verify_sms_code(
        phone=verify_data.phone_number,
        code=verify_data.code,
    )
    if not success:
        raise BadRequestException(
            message="Invalid code",
        )
    # Проверяем, существует ли пользователь
    db_user = await UserDAO.get_user_by_phone(
        session=session,
        phone_number=verify_data.phone_number,
    )
    if not db_user:
        raise NotFoundException(
            message="User not found",
        )
    await UserDAO.update(
        session=session,
        filters=UserFilter(
            id=db_user.id,
            phone_number=verify_data.phone_number,
        ),
        values=UserUpdateInternal(
            is_active=True,
            is_verified=True,
        ),
    )
    # Создаем токены
    access_token = await create_access_token(db_user)
    refresh_token = await create_refresh_token(db_user)
    return DataResponse(
        data=TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
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
