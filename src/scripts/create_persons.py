import asyncio
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SOURCE_DIR
from app.core.db import db_helper
from app.dao.person import PersonDAO
from app.schemas.person import PersonCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_persons(session: AsyncSession) -> None:
    try:
        PERSONS_JSON_PATH = f"{SOURCE_DIR}/data/persons.json"
        with open(PERSONS_JSON_PATH, encoding="utf-8") as file:
            people = json.load(file)
        people_count = await PersonDAO.count(session=session)
        if people_count > 0:
            logger.info("People already exist.")
            return
        for person in people:
            await PersonDAO.add(
                session=session,
                values=PersonCreate(
                    first_name=person["first_name"],
                    last_name=person["last_name"],
                    image_url=person["image"],
                    department_id=person["department_id"],
                    role_id=person["role_id"],
                ),
            )

        await session.commit()

    except Exception as e:
        logger.error("Error creating persons: %s", e)
        await session.rollback()
        raise e


async def main():
    async with db_helper.session_factory() as session:
        await create_persons(session)


if __name__ == "__main__":
    asyncio.run(main())
