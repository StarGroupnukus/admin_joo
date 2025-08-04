from fastapi import APIRouter

from app.core.config import settings

from .auth import router as auth_router
from .post import router as post_router
from .superuser import router as superuser_router
from .user import router as user_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)


@router.get("/")
def index():
    return {"message": "Hello, World!"}


router.include_router(
    auth_router,
)
router.include_router(
    user_router,
)
router.include_router(
    post_router,
)

router.include_router(
    superuser_router,
)
