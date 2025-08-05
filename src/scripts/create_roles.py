import asyncio
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import db_helper
from app.dao.role import RoleDAO
from app.schemas.role import RoleCreateInternal
from app.core.config import SOURCE_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_roles(session: AsyncSession) -> None:
    try:
        ROLES_JSON_PATH = f"{SOURCE_DIR}/data/roles.json"
        with open(ROLES_JSON_PATH, encoding="utf-8") as file:
            roles = json.load(file)
        roles_count = await RoleDAO.count(session=session)
        if roles_count > 0:
            logger.info("Roles already exist.")
            return
        for role in roles:
            await RoleDAO.add(
                session=session,
                values=RoleCreateInternal(
                    id=role["id"],
                    name=role["name"],
                ),
            )

        await session.commit()

    except Exception as e:
        logger.error("Error creating roles: %s", e)
        await session.rollback()
        raise e


async def main():
    async with db_helper.session_factory() as session:
        await create_roles(session)


if __name__ == "__main__":
    asyncio.run(main())
