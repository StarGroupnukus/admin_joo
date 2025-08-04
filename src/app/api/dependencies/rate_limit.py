import logging

from fastapi import Depends, Request

from app.api.dependencies.user import get_optional_user
from app.core.config import settings
from app.core.db import SessionDep
from app.core.exceptions import (
    NotFoundException,
    RateLimitException,
)
from app.core.utils.rate_limit import is_rate_limited
from app.dao.rate_limit import RateLimitDAO
from app.dao.tier import TierDAO
from app.models.user import User
from app.schemas.rate_limit import RateLimitFilter
from app.schemas.tier import TierRead
from app.schemas.validation import sanitize_path

from .tier import validate_tier_by_name

logger = logging.getLogger(__name__)


async def rate_limiter(
    request: Request,
    session=SessionDep,
    user: User | None = Depends(get_optional_user),
) -> None:
    path = sanitize_path(request.url.path)
    if user:
        user_id = user.id
        tier = await TierDAO.find_one_or_none_by_id(
            session=session,
            data_id=user.tier_id,
        )
        if tier:
            rate_limit = await RateLimitDAO.find_one_or_none(
                session=session,
                filters=RateLimitFilter(
                    tier_id=tier["id"],
                    path=path,
                ),
            )
            if rate_limit:
                limit, period = rate_limit["limit"], rate_limit["period"]
            else:
                logger.warning(
                    f"User {user_id} with tier '{tier['name']}' has no specific rate limit for path '{path}'. \
                        Applying default rate limit."
                )
                limit, period = (
                    settings.rate_limit.DEFAULT_LIMIT,
                    settings.rate_limit.DEFAULT_PERIOD,
                )
        else:
            logger.warning(
                f"User {user_id} has no assigned tier. Applying default rate limit."
            )
            limit, period = (
                settings.rate_limit.DEFAULT_LIMIT,
                settings.rate_limit.DEFAULT_PERIOD,
            )
    else:
        user_id = request.client.host
        limit, period = (
            settings.rate_limit.DEFAULT_LIMIT,
            settings.rate_limit.DEFAULT_PERIOD,
        )

    is_limited = await is_rate_limited(
        user_id=user_id,
        path=path,
        limit=limit,
        period=period,
    )
    if is_limited:
        raise RateLimitException(
            message="Rate limit exceeded",
        )


async def validate_rate_limit_by_tier_name(
    rate_limit_id: int,
    tier: TierRead = Depends(validate_tier_by_name),
    session=SessionDep,
):
    db_rate_limit = await RateLimitDAO.find_one_or_none(
        session=session,
        filters=RateLimitFilter(
            tier_id=tier.id,
            id=rate_limit_id,
        ),
    )
    if not db_rate_limit:
        raise NotFoundException(
            message="Rate limit not found",
        )
    return db_rate_limit
