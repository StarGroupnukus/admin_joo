from fastapi import APIRouter, Depends, HTTPException
from app.core.db import SessionDep, TransactionSessionDep
from app.dao.branch import BranchDAO
from app.schemas.branch import (
    Feedback,
    BranchRead,
)
from app.core.config import settings
from app.schemas import DataResponse, PaginatedListResponse, get_pagination
from fastapi import status, Query

from app.schemas.response import ListResponse

router = APIRouter(
    prefix=settings.api.v1.feedback,
    tags=["feedback"],
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