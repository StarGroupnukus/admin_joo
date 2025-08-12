from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.departments import Department
from app.schemas.department import DepartmentFilter, DepartmentRead, DepartmentReadWithCount
from sqlalchemy import select, text

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

    @classmethod
    async def get_departments_with_count(
        cls, 
        session: AsyncSession, 
        role_id: int | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[DepartmentRead]:
        base_query = """
            SELECT d.id, d.name, d.role_id, COUNT(p.id) AS count
            FROM departments d
            LEFT JOIN persons p ON d.id = p.department_id
            {where_clause}
            GROUP BY d.id, d.name, d.role_id
            ORDER BY d.id
            LIMIT :page_size OFFSET :offset
        """
        where_clause = "WHERE d.role_id = :role_id" if role_id is not None else ""
        query = text(base_query.format(where_clause=where_clause))
        params = {
            "role_id": role_id,
            "page_size": page_size,
            "offset": (page - 1) * page_size,
        }
        result = await session.execute(query, params)
        records = result.mappings().all()
        return [DepartmentReadWithCount(**record) for record in records]
