from app.core.db import SessionDep
from app.core.exceptions import NotFoundException
from app.dao.tier import TierDAO
from app.schemas.tier import TierFilter


async def validate_tier_by_id(
    tier_id: int,
    session=SessionDep,
):
    tier = await TierDAO.find_one_or_none(
        session=session,
        filters=TierFilter(
            id=tier_id,
        ),
    )
    if not tier:
        raise NotFoundException(
            message="Tier not found",
        )
    return tier


async def validate_tier_by_name(
    tier_name: str,
    session=SessionDep,
):
    tier = await TierDAO.find_one_or_none(
        session=session,
        filters=TierFilter(
            name=tier_name,
        ),
    )
    if not tier:
        raise NotFoundException(
            message="Tier not found",
        )
    return tier
