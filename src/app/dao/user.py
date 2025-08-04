from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.models.user import User
from app.schemas.user import (
    UserFilter,
    UserRead,
)


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def get_user_by_phone(
        cls,
        session: AsyncSession,
        phone_number: str,
    ) -> UserRead | None:
        user = await cls.find_one_or_none(
            session=session,
            filters=UserFilter(
                phone_number=phone_number,
            ),
        )
        return user if user else None
