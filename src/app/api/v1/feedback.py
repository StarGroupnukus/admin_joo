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
import httpx
from app.schemas.response import ListResponse
from fastapi import Form

router = APIRouter(
    prefix=settings.api.v1.feedback,
    tags=["feedback"],
)
SMARTCAPTCHA_SECRET = settings.crypt.CAPTCHA_SECRET


async def verify_captcha(token: str) -> bool:
    url = "https://smartcaptcha.yandexcloud.net/validate"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url, data={"secret": SMARTCAPTCHA_SECRET, "token": token}
        )
        data = resp.json()
        return data.get("status") == "ok"


@router.post("add_branch")
async def add_branch(
    branch: BranchCreate,
    session=TransactionSessionDep,
   # current_user: UserRead = Depends(get_current_auth_user),
):
    branch = await BranchDAO.add(session=session, values=branch)
    return DataResponse(
        data=BranchRead(id=branch.id, name=branch.name,
        rating_1_count=branch.rating_1_count,
        rating_2_count=branch.rating_2_count,
        rating_3_count=branch.rating_3_count,
        rating_4_count=branch.rating_4_count,
        rating_5_count=branch.rating_5_count,
        rating=5),
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


@router.post("/feedbackadd_feedback")
async def add_feedback(
    branch_id: int = Form(...),
    rating: int = Form(ge=1, le=5),
    smart_token: str = Form(...),
    session=TransactionSessionDep,
):
    # if not await verify_captcha(smart_token):
    #     raise HTTPException(status_code=400, detail="Captcha failed")

    feedback = Feedback(branch_id=branch_id, rating=rating)
    branch = await BranchDAO.add_feedback(session=session, feedback=feedback)
    return DataResponse(
        data=branch,
    )
