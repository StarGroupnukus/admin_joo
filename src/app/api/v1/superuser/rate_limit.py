from fastapi import APIRouter, Depends, status

from app.api.dependencies import (
    get_current_superuser,
    validate_rate_limit_by_tier_name,
    validate_tier_by_name,
)
from app.core.config import settings
from app.core.db import SessionDep, TransactionSessionDep
from app.core.exceptions import DuplicateValueException
from app.dao.rate_limit import RateLimitDAO
from app.schemas import DataResponse, ListResponse
from app.schemas.rate_limit import (
    RateLimitCreate,
    RateLimitCreateInternal,
    RateLimitFilter,
    RateLimitRead,
    RateLimitUpdate,
    RateLimitUpdateInternal,
)
from app.schemas.tier import TierRead

router = APIRouter(
    prefix=settings.api.v1.rate_limits,
)


@router.get(
    "/list",
    response_model=ListResponse[RateLimitRead],
)
async def get_rate_limits(
    session=SessionDep,
):
    db_rate_limits = await RateLimitDAO.find_all(
        session=session,
        filters=None,
    )
    return ListResponse(
        data=db_rate_limits,
        total=len(db_rate_limits),
    )


@router.get(
    "/{tier_name}/{rate_limit_id}",
    response_model=DataResponse[RateLimitRead],
)
async def get_rate_limit_by_id(
    rate_limit: RateLimitRead = Depends(validate_rate_limit_by_tier_name),
    session=SessionDep,
):
    return DataResponse(
        data=rate_limit,
    )


@router.post(
    "/{tier_name}/",
    response_model=DataResponse[RateLimitRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)],
)
async def create_rate_limit(
    rate_limit_create: RateLimitCreate,
    tier: TierRead = Depends(validate_tier_by_name),
    session=TransactionSessionDep,
):
    rate_limit_create_data = RateLimitCreate(
        **rate_limit_create.model_dump(),
    )
    rate_limit_name = f"{rate_limit_create_data.path}:{rate_limit_create_data.limit}:{rate_limit_create_data.period}"
    rate_limit_create_internal = RateLimitCreateInternal(
        **rate_limit_create_data.model_dump(),
        tier_id=tier.id,
        name=rate_limit_name,
    )
    db_rate_limit = await RateLimitDAO.find_one_or_none(
        session=session,
        filters=RateLimitFilter(
            name=rate_limit_name,
        ),
    )
    if db_rate_limit:
        raise DuplicateValueException(
            message="Rate limit with this name already exists",
        )
    rate_limit = await RateLimitDAO.add(
        session=session,
        values=rate_limit_create_internal,
    )
    return DataResponse(
        data=rate_limit,
    )


@router.put(
    "/{tier_name}/{rate_limit_id}",
    response_model=DataResponse[RateLimitRead],
    dependencies=[Depends(get_current_superuser)],
)
async def update_rate_limit(
    rate_limit_update: RateLimitUpdate,
    rate_limit: RateLimitRead = Depends(validate_rate_limit_by_tier_name),
    session=TransactionSessionDep,
):
    rate_limit_update_data = RateLimitUpdate(
        **rate_limit_update.model_dump(),
    )
    rate_limit_name = (
        f"{rate_limit_update_data.path}:{rate_limit_update_data.limit}:{rate_limit_update_data.period}",
    )
    rate_limit_update_internal = RateLimitUpdateInternal(
        **rate_limit_update_data.model_dump(),
        tier_id=rate_limit.tier_id,
        name=rate_limit_name,
    )
    await RateLimitDAO.update(
        session=session,
        filters=RateLimitFilter(
            id=rate_limit.id,
        ),
        values=rate_limit_update_internal,
    )
    updated_rate_limit = await RateLimitDAO.find_one_or_none(
        session=session,
        filters=RateLimitFilter(
            id=rate_limit.id,
        ),
    )
    return DataResponse(
        data=updated_rate_limit,
    )


@router.delete(
    "/{tier_name}/{rate_limit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_superuser)],
)
async def delete_rate_limit(
    rate_limit: RateLimitRead = Depends(validate_rate_limit_by_tier_name),
    session=TransactionSessionDep,
):
    await RateLimitDAO.delete(
        session=session,
        filters=RateLimitFilter(
            id=rate_limit.id,
        ),
    )
