import asyncio
import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import SOURCE_DIR
from app.core.db import db_helper
from app.dao.department import DepartmentDAO
from app.schemas.department import DepartmentCreate, DepartmentFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_departments(session: AsyncSession) -> None:
    try:
        DEPARTMENTS_JSON_PATH = f"{SOURCE_DIR}/data/departments.json"
        with open(DEPARTMENTS_JSON_PATH, encoding="utf-8") as file:
            departments = json.load(file)
        departments_count = await DepartmentDAO.count(
            session=session,
            filters=DepartmentFilter(),
        )
        if departments_count > 0:
            logger.info("Departments already exist.")
            return
        for department in departments:
            await DepartmentDAO.add(
                session=session,
                values=DepartmentCreate(
                    name=department["name"],
                    role_id=department["role_id"],
                ),
            )

        await session.commit()

    except Exception as e:
        logger.error("Error creating departments: %s", e)
        await session.rollback()
        raise e


async def main():
    async with db_helper.session_factory() as session:
        await create_departments(session)


if __name__ == "__main__":
    asyncio.run(main())
