import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.utils import hash_password
from app.core.config import settings
from app.core.db import db_helper
from app.dao import UserDAO
from app.schemas.user import UserCreateInternal, UserFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_user(session: AsyncSession) -> None:
    try:
        email = settings.first_superuser.EMAIL
        username = settings.first_superuser.USERNAME
        phone_number = settings.first_superuser.PHONE_NUMBER
        hashed_password = hash_password(settings.first_superuser.PASSWORD).decode(
            "utf-8"
        )
        db_user = await UserDAO.find_one_or_none(
            session=session,
            filters=UserFilter(
                username=username,
                phone_number=phone_number,
            ),
        )
        if db_user:
            logger.info(f"Admin user {username} already exists.")
            return
        values = UserCreateInternal(
            email=email,
            username=username,
            phone_number=phone_number,
            hashed_password=hashed_password,
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )

        await UserDAO.add(
            session=session,
            values=values,
        )
        await session.commit()
        logger.info(f"Admin user {username} created successfully.")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        await session.rollback()
        raise e


async def main():
    async with db_helper.session_factory() as session:
        await create_first_user(session)


if __name__ == "__main__":
    asyncio.run(main())
