from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .validation import sanitize_path


class RateLimitBase(BaseModel):
    path: Annotated[str, Field(examples=["users"])]
    limit: Annotated[int, Field(examples=[5])]
    period: Annotated[int, Field(examples=[60])]

    @field_validator("path")
    def validate_and_sanitize_path(cls, v: str) -> str:
        return sanitize_path(v)


class RateLimit(RateLimitBase):
    tier_id: int
    name: str
    created_at: datetime
    updated_at: datetime | None = None


class RateLimitRead(RateLimit):
    id: int
    tier_id: int


class RateLimitCreate(RateLimitBase):
    model_config = ConfigDict(extra="forbid")


class RateLimitCreateInternal(RateLimitCreate):
    tier_id: int
    name: str


class RateLimitUpdate(BaseModel):
    path: str | None = Field(default=None)
    limit: int | None = None
    period: int | None = FileNotFoundError

    @field_validator("path")
    def validate_and_sanitize_path(cls, v: str) -> str:
        return sanitize_path(v) if v is not None else None


class RateLimitUpdateInternal(RateLimitUpdate):
    updated_at: datetime | None = None
    name: str | None = None


class RateLimitFilter(BaseModel):
    id: int | None = None
    path: str | None = None
    limit: int | None = None
    period: int | None = None
    name: str | None = None
