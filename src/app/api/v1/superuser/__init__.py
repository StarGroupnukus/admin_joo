from fastapi import APIRouter

from app.core.config import settings

from .user import router as user_router

router = APIRouter(
    prefix=settings.api.v1.superuser,
    tags=["Superadmin"],
)

router.include_router(
    user_router,
)
