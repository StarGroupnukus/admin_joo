from fastapi import APIRouter, Depends, status

from app.api.dependencies.user import get_current_auth_user
from app.core.config import settings
from app.core.db import TransactionSessionDep
from app.core.exceptions import NotFoundException
from app.dao.role import RoleDAO
from app.schemas import DataResponse
from app.schemas.response import ListResponse
from app.schemas.role import RoleCreate, RoleRead
from app.schemas.user import UserRead

router = APIRouter(
    prefix=settings.api.v1.roles,
    tags=["Roles"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[RoleRead],
)
async def create_role(
    role: RoleCreate,
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    role = await RoleDAO.add(session=session, values=role)
    return DataResponse(
        data=role,
    )

@router.get(
    "/get_all",
    response_model=ListResponse[RoleRead],
)
async def get_roles(
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    roles = await RoleDAO.find_all(
        session=session,
        filters=None,
    )
    if roles is None:
        raise NotFoundException(
            message="Roles not found",
        )
    return ListResponse(
        data=roles,
        total=len(roles),
    )