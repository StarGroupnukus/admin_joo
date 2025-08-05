from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.models.persons import Person
from app.schemas.person import PersonFullRead
from app.schemas.role import RoleRead
from app.schemas.department import DepartmentRead
from sqlalchemy import text


class PersonDAO(BaseDAO):
    model = Person
    

    @classmethod
    async def get_person_by_id(cls, session: AsyncSession, person_id: int) -> PersonFullRead | None:
        query = text("""
            SELECT 
                p.id AS id,
                p.first_name AS first_name,
                p.last_name AS last_name,
                p.image_url AS image_url,
                d.id AS department_id,
                d.name AS department_name,
                r.id AS role_id,
                r.name AS role_name
            FROM persons p
            JOIN departments d ON p.department_id = d.id
            JOIN roles r ON p.role_id = r.id
            WHERE p.id = :person_id
        """)
        result = await session.execute(query, {"person_id": person_id})
        record = result.mappings().first()

        if record:
            return PersonFullRead(
                id=record["id"],
                first_name=record["first_name"],
                last_name=record["last_name"],
                image_url=record["image_url"],
                department=DepartmentRead(id=record["department_id"], role_id=record["role_id"], name=record["department_name"]),
                role=RoleRead(id=record["role_id"], name=record["role_name"]),
            )
        return None
