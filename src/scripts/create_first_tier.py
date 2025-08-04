import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import db_helper
from app.models.tier import Tier

logger = logging.getLogger(__name__)


async def create_first_tier(session: AsyncSession) -> None:
    try:
        tier_name = settings.first_tier.NAME

        query = select(Tier).where(Tier.name == tier_name)
        result = await session.execute(query)
        tier = result.scalar_one_or_none()

        if tier is None:
            session.add(Tier(name=tier_name))
            await session.commit()
            logger.info(f"Tier '{tier_name}' created successfully.")

        else:
            logger.info(f"Tier '{tier_name}' already exists.")

    except Exception as e:
        logger.error(f"Error creating tier: {e}")
        await session.rollback()
        raise e


async def main():
    async with db_helper.session_factory() as session:
        await create_first_tier(session)


if __name__ == "__main__":
    asyncio.run(main())
