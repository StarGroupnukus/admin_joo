import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from arq.connections import RedisSettings, create_pool
from fastapi import FastAPI
from redis.asyncio import ConnectionPool, Redis

# from app.core.utils import queue, rate_limit, cache,redis_client
# from arq import create_pool
# from arq.connections import RedisSettings
from app.core.config import settings
from app.core.db import db_helper
from app.core.utils import redis_client, task_queue
from app.models import Base

logger = logging.getLogger(__name__)


# -------------- database --------------
async def create_tables() -> None:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# -------------- redis --------------
async def create_redis_pool() -> None:
    try:
        redis_client.pool = ConnectionPool.from_url(
            f"redis://:{settings.redis_client.PASSWORD}@{settings.redis_client.HOST}:{settings.redis_client.PORT}"
        )
        redis_client.client = Redis(connection_pool=redis_client.pool)  # type: ignore
        await redis_client.client.ping()
        logger.info("Redis client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection pool: {e}")
        raise


async def close_redis_pool() -> None:
    await redis_client.client.aclose()  # type: ignore


# -------------- queue --------------
async def create_redis_queue_pool() -> None:
    task_queue.pool = await create_pool(
        RedisSettings(
            password=settings.redis_client.PASSWORD,
            host=settings.redis_client.HOST,
            port=settings.redis_client.PORT,
        )
    )


async def close_redis_queue_pool() -> None:
    await task_queue.pool.aclose()  # type: ignore


# -------------- cache --------------
# async def create_redis_cache_pool() -> None:
#     cache.pool = ConnectionPool.from_url(settings.redis_cache.REDIS_CACHE_URL)
#     cache.client = Redis(connection_pool=cache.pool)  # type: ignore


# async def close_redis_cache_pool() -> None:
#     await cache.client.aclose()  # type: ignore
#
#
#
#
# # -------------- rate limit --------------
# async def create_redis_rate_limit_pool() -> None:
#     rate_limit.pool = ConnectionPool.from_url(
#         settings.redis_rate_limiter.REDIS_RATE_LIMIT_URL
#     )
#     rate_limit.client = Redis.from_pool(rate_limit.pool)  # type: ignore
#
#
# async def close_redis_rate_limit_pool() -> None:
#     await rate_limit.client.aclose()  # type: ignore


# -------------- application --------------
# async def set_threadpool_tokens(number_of_tokens: int = 100) -> None:
#     limiter = anyio.to_thread.current_default_thread_limiter()
#     limiter.total_tokens = number_of_tokens


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    # await set_threadpool_tokens()

    if settings.db.CREATE_TABLES_ON_START:
        await create_tables()
    if settings.db.DROP_TABLES_ON_START:
        await drop_tables()
    await create_redis_pool()
    await create_redis_queue_pool()
    yield
    # shutdown
    await close_redis_pool()

    await close_redis_queue_pool()

    await db_helper.dispose()
