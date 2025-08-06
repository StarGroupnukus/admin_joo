from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.models.departments import Department


class DepartmentDAO(BaseDAO):
    model = Department

    @classmethod
    async def get_role_id(cls, session: AsyncSession, department_id: int) -> int | None:
        query = select(cls.model.role_id).filter(cls.model.id == department_id)
        result = await session.execute(query)
        record = result.scalar_one_or_none()
        if record:
            return record
        return None
