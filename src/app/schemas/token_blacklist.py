from datetime import datetime

from pydantic import BaseModel


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class RefreshToken(BaseModel):
    refresh_token: str | None = None


class TokenBlacklistBase(BaseModel):
    jti: str
    expires_at: datetime


class TokenBlacklistCreate(TokenBlacklistBase):
    is_blacklisted: bool = True


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass


class TokenBlacklistFilter(BaseModel):
    id: int | None = None
    jti: str | None = None
    expires_at: datetime | None = None
    is_blacklisted: bool | None = None
