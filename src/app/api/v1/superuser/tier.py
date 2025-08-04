from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_superuser, validate_tier_by_name
from app.core.config import settings
from app.core.db import SessionDep, TransactionSessionDep
from app.core.exceptions import DuplicateValueException
from app.dao.tier import TierDAO
from app.schemas import DataResponse, ListResponse
from app.schemas.tier import (
    TierCreate,
    TierCreateInternal,
    TierFilter,
    TierRead,
    TierUpdate,
    TierUpdateInternal,
)

router = APIRouter(
    prefix=settings.api.v1.tiers,
)


@router.get(
    "/list",
    response_model=ListResponse[TierRead],
)
async def get_tiers(
    session=SessionDep,
):
    db_tiers = await TierDAO.find_all(
        session=session,
        filters=None,
    )
    return ListResponse(
        data=db_tiers,
        total=len(db_tiers),
    )


@router.get(
    "/{tier_name}",
    response_model=DataResponse[TierRead],
)
async def get_tier(
    session=SessionDep,
    tier: TierRead = Depends(validate_tier_by_name),
):
    return DataResponse(
        data=tier,
    )


@router.post(
    "",
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_201_CREATED,
    response_model=DataResponse[TierRead],
)
async def create_tier(
    tier_create: TierCreate,
    session=TransactionSessionDep,
):
    db_tier = await TierDAO.find_one_or_none(
        session=session,
        filters=TierFilter(
            name=tier_create.name,
        ),
    )
    if db_tier:
        raise DuplicateValueException(
            message="Tier Name not available",
        )

    tier_internal = TierCreateInternal(
        **tier_create.model_dump(),
    )
    created_tier: TierRead = await TierDAO.add(
        session=session,
        values=tier_internal,
    )
    return DataResponse(
        data=created_tier,
    )


@router.put(
    "/{tier_name}",
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_201_CREATED,
)
async def update_tier(
    name: str,
    tier_update: TierUpdate,
    tier: TierRead = Depends(validate_tier_by_name),
    session=TransactionSessionDep,
):
    tier_internal = TierUpdateInternal(
        **tier_update.model_dump(),
    )
    await TierDAO.update(
        session=session,
        filters=TierFilter(
            name=name,
        ),
        values=tier_internal,
    )
    updated_tier = await TierDAO.find_one_or_none(
        session=session,
        filters=TierFilter(
            name=name,
        ),
    )
    return DataResponse(
        data=updated_tier,
    )


@router.delete(
    "/{tier_name}",
    dependencies=[Depends(get_current_superuser)],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tier(
    tier: TierRead = Depends(validate_tier_by_name),
    session=TransactionSessionDep,
):
    await TierDAO.delete(
        session=session,
        filters=TierFilter(
            name=tier.name,
        ),
    )
