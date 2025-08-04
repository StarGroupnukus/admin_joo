from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """Базовая схема пользователя с основными полями."""

    name: str
    email: Optional[str] = None
    phone_number: str


class UserSchema(UserBase):
    image_url: str
    is_superuser: bool = False
    is_verified: bool = False
    is_active: bool = False
    tier_id: Optional[int] = None


class UserRead(UserSchema):
    id: int
    model_config = ConfigDict(
        from_attributes=True,
    )


class UserCreate(UserBase):
    """Схема создания пользователя."""

    password: str

    model_config = ConfigDict(extra="forbid")


class UserCreateInternal(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    """Схема обновления данных пользователя."""

    name: str | None = None
    model_config = ConfigDict(extra="forbid")


class UserUpdateInternal(UserUpdate):
    email: str | None = None
    image_url: str | None = None
    phone_number: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    is_deleted: bool | None = None
    deleted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tier_id: int | None = None


class UserFilter(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    tier_id: Optional[int] = None


class PhoneNumber(BaseModel):
    phone_number: str


class VerifyPhoneNumber(PhoneNumber):
    code: str

    model_config = ConfigDict(extra="forbid")


class LoginViaPhone(PhoneNumber):
    password: str
