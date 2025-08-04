import logging
from datetime import UTC, datetime

from app.app_lifespan import redis_client

# from app.core.utils.redis_client import client
from app.schemas.rate_limit import sanitize_path

logger = logging.getLogger(__name__)

# uncomment if you use another redis for rate limit
# pool: ConnectionPool | None = None
# client: Redis | None = None


async def is_rate_limited(
    user_id: int,
    path: str,
    limit: int,
    period: int,
) -> bool:
    if redis_client.client is None:
        logger.error("Redis client is not initialized.")
        raise Exception("Redis client is not initialized.")

    current_timestamp = int(datetime.now(UTC).timestamp())
    window_start = current_timestamp - (current_timestamp % period)

    sanitized_path = sanitize_path(path)
    key = f"ratelimit:{user_id}:{sanitized_path}:{window_start}"

    try:
        current_count = await redis_client.client.incr(key)
        if current_count == 1:
            await redis_client.client.expire(key, period)

        if current_count > limit:
            return True

    except Exception as e:
        logger.exception(
            f"Error checking rate limit for user {user_id} on path {path}: {e}"
        )
        raise e

    return False
