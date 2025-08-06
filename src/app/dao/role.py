from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import BaseDAO
from app.models.roles import Role
from app.schemas.role import RoleFilter, RoleRead


class RoleDAO(BaseDAO):
    model = Role

    @classmethod
    async def get_role_by_name(
        cls,
        session: AsyncSession,
        name: str,
    ) -> RoleRead | None:
        role = await cls.find_one_or_none(
            session=session,
            filters=RoleFilter(
                name=name,
            ),
        )
        return role if role else None
    
    