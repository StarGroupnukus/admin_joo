from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_auth_user,
)
from app.core.config import settings
from app.schemas import DataResponse
from app.schemas.user import (
    UserRead,
)

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=DataResponse[UserRead],
)
async def get_me(
    current_user: UserRead = Depends(get_current_auth_user),
):
    return DataResponse(
        data=current_user,
    )
