from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.utils import decode_jwt
from app.dao import BaseDAO
from app.models.token_blacklist import TokenBlacklist
from app.schemas.token_blacklist import (
    TokenBlacklistCreate,
    TokenBlacklistFilter,
)


class TokenBlacklistDAO(BaseDAO):
    model = TokenBlacklist

    @classmethod
    async def add_to_blacklist(
        cls,
        token: str,
        session: AsyncSession,
    ) -> None:
        payload = decode_jwt(token)
        expires_at = datetime.fromtimestamp(
            payload.get("exp"),
            tz=UTC,
        )
        await cls.add(
            session=session,
            values=TokenBlacklistCreate(
                **{
                    "jti": payload.get("jti"),
                    "expires_at": expires_at,
                    "is_blacklisted": True,
                }
            ),
        )

    @classmethod
    async def get_token_by_jti(
        cls,
        session: AsyncSession,
        jti: str,
    ):
        token = await cls.find_one_or_none(
            session=session,
            filters=TokenBlacklistFilter(
                jti=jti,
            ),
        )
        return token

    @classmethod
    async def is_token_blacklisted(
        cls,
        session: AsyncSession,
        jti: str,
    ) -> bool:
        """Проверяет, находится ли токен в черном списке"""
        token = await cls.get_token_by_jti(
            session=session,
            jti=jti,
        )
        return token.is_blacklisted if token else False
