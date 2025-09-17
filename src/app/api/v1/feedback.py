from fastapi import APIRouter, Depends, HTTPException
from app.core.db import SessionDep, TransactionSessionDep
from app.dao.branch import BranchDAO
from app.schemas.branch import (
    BranchCreate,
    Feedback,
    BranchRead,
    BranchFilter,
)
from app.core.config import settings
from app.schemas import DataResponse, PaginatedListResponse, get_pagination
from fastapi import status, Query
from app.api.dependencies.user import get_current_auth_user
from app.schemas.user import UserRead

from app.schemas.response import ListResponse

router = APIRouter(
    prefix=settings.api.v1.feedback,
    tags=["feedback"],
)


@router.post("add_branch")
async def add_branch(
    branch: BranchCreate,
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    branch = await BranchDAO.add(session=session, values=branch)
    return DataResponse(
        data=branch,
    )

@router.delete("delete_branch", status_code=status.HTTP_200_OK)
async def delete_branch(
    branch_id: int,
    session=TransactionSessionDep,
    current_user: UserRead = Depends(get_current_auth_user),
):
    await BranchDAO.delete(session=session, filters=BranchFilter(id=branch_id))
    return DataResponse(
        data=None,
    )

@router.get(
    "get_all",
    status_code=status.HTTP_200_OK,
    response_model=ListResponse[BranchRead],
)
async def get_all_feedback(
    session=SessionDep,
):
    branches = await BranchDAO.get_all(session=session)
    return ListResponse(
        data=branches,
        total=len(branches),
    )

@router.post(
    "add_feedback",
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[BranchRead],
)
async def add_feedback(
    feedback: Feedback,
    session=TransactionSessionDep,
):
    branch = await BranchDAO.add_feedback(session=session, feedback=feedback)
    return DataResponse(
        data=branch,
    )
