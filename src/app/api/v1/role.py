from fastapi import APIRouter
from app.core.db import TransactionSessionDep
from app.core.exceptions import NotFoundException
from app.dao.role import RoleDAO
from app.schemas.response import ListResponse
from app.schemas.role import RoleCreate, RoleRead
from app.core.config import settings
from app.schemas import DataResponse
from fastapi import status

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