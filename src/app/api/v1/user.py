import uuid as uuid_pkg
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_current_active_auth_user,
    get_current_auth_user,
)
from app.core.config import settings
from app.core.db import TransactionSessionDep
from app.core.exceptions import (
    BadRequestException,
    DuplicateValueException,
    TooManyRequestsException,
)
from app.core.utils import redis_sms
from app.core.utils.send_sms import send_verification_sms
from app.dao.user import UserDAO
from app.schemas import DataResponse
from app.schemas.user import (
    PhoneNumber,
    UserFilter,
    UserRead,
    UserUpdate,
    UserUpdateInternal,
    VerifyPhoneNumber,
)

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=DataResponse[UserRead],
)
async def get_me(
    current_user: UserRead = Depends(get_current_auth_user),
):
    return DataResponse(
        data=current_user,
    )


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=DataResponse[UserRead],
)
async def update_me(
    update_data: UserUpdate,
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    current_user_id = (
        current_user.get("id") if isinstance(current_user, dict) else current_user.id
    )
    update_internal = UserUpdateInternal(
        **update_data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        ),
    )
    await UserDAO.update(
        session=session,
        filters=UserFilter(
            id=current_user_id,
        ),
        values=update_internal,
    )
    updated_user = await UserDAO.find_one_or_none_by_id(
        session=session,
        data_id=current_user_id,
    )
    return DataResponse(
        data=updated_user,
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_me(
    current_user: UserRead = Depends(get_current_auth_user),
    session=TransactionSessionDep,
):
    current_user_id = (
        current_user.get("id") if isinstance(current_user, dict) else current_user.id
    )

    db_user = await UserDAO.find_one_or_none_by_id(
        session=session,
        data_id=current_user_id,
    )
    deleted_phone_number = f"{db_user.phone_number}_{uuid_pkg.uuid4()!s}"
    await UserDAO.update(
        session=session,
        filters=UserFilter(
            id=current_user_id,
        ),
        values=UserUpdateInternal(
            phone_number=deleted_phone_number,
            is_active=False,
            is_verified=False,
            is_deleted=True,
            deleted_at=datetime.now(UTC),
        ),
    )


@router.patch(
    "/me/phone-number",
    response_model=DataResponse[dict],
)
async def change_phone_number(
    update_data: PhoneNumber,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    new_phone_number = update_data.phone_number
    db_user = await UserDAO.find_one_or_none_by_id(
        session=session,
        data_id=current_user.id,
    )
    if new_phone_number == db_user.phone_number:
        raise DuplicateValueException(
            message="New phone number is the same as the current one",
        )
    db_user = await UserDAO.find_one_or_none(
        session=session,
        filters=UserFilter(phone_number=new_phone_number),
    )
    if db_user:
        raise DuplicateValueException(
            message="User with this phone number already exists",
        )
    if await redis_sms.is_blocked(update_data.phone_number):
        raise TooManyRequestsException(
            message="Too many requests",
        )
    success, _ = await send_verification_sms(new_phone_number)
    if not success:
        raise TooManyRequestsException(
            message="Too many requests",
        )
    return DataResponse(
        data={
            "phone_number": new_phone_number,
        },
    )


@router.post(
    "/me/phone-number/verify",
    response_model=DataResponse[dict],
)
async def verify_phone_number(
    verify_data: VerifyPhoneNumber,
    current_user: UserRead = Depends(get_current_active_auth_user),
    session=TransactionSessionDep,
):
    success, _ = await redis_sms.verify_sms_code(
        phone=verify_data.phone_number,
        code=verify_data.code,
    )
    if not success:
        raise BadRequestException(
            message="Invalid verification code",
        )
    await UserDAO.update(
        session=session,
        filters=UserFilter(
            id=current_user.id,
        ),
        values=UserUpdateInternal(
            phone_number=verify_data.phone_number,
        ),
    )
    return DataResponse(
        data={
            "phone_number": verify_data.phone_number,
        },
    )
