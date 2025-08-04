from fastapi import APIRouter

from app.core.config import settings

from .post import router as post_router
from .rate_limit import router as rate_limit_router
from .tier import router as tier_router
from .user import router as user_router

router = APIRouter(
    prefix=settings.api.v1.superuser,
    tags=["Superadmin"],
)

router.include_router(
    user_router,
)
router.include_router(
    post_router,
)

router.include_router(
    tier_router,
)
router.include_router(
    rate_limit_router,
)
