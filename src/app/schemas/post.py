from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.networks import AnyHttpUrl

from .validation import (
    MEDIA_URL_FIELD,
    TEXT_FIELD,
    TEXT_FIELD_UPDATE,
    TITLE_FIELD,
    TITLE_FIELD_UPDATE,
    serialize_image_url,
)


class PostBase(BaseModel):
    """Базовая схема поста с основными полями."""

    title: TITLE_FIELD
    text: TEXT_FIELD


class Post(PostBase):
    """Схема поста с расширенными полями."""

    image_url: MEDIA_URL_FIELD
    user_id: int


class PostRead(Post):
    """Схема чтения поста."""

    created_at: datetime
    id: int


class PostCreate(PostBase):
    """Схема создания поста."""

    model_config = ConfigDict(extra="forbid")
    image_url: MEDIA_URL_FIELD


class PostCreateInternal(PostCreate):
    """Схема внутреннего создания поста."""

    user_id: int

    @field_serializer("image_url")
    def change_image_url(
        v: Optional[AnyHttpUrl],
    ) -> str:
        return serialize_image_url(v)


class PostUpdate(BaseModel):
    """Схема обновления поста."""

    model_config = ConfigDict(extra="forbid")

    title: TITLE_FIELD_UPDATE
    text: TEXT_FIELD_UPDATE
    image_url: MEDIA_URL_FIELD

    @field_serializer("image_url")
    def change_image_url(
        v: Optional[AnyHttpUrl],
    ) -> str:
        return serialize_image_url(v)


class PostUpdateInternal(PostUpdate):
    """Схема внутреннего обновления поста."""

    is_deleted: Optional[bool] = None
    updated_at: Optional[datetime] = None


class PostFilter(BaseModel):
    """Схема фильтрации постов."""

    id: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    user_id: Optional[int] = None
    is_deleted: Optional[bool] = None
