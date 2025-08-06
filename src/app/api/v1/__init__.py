from fastapi import APIRouter

from app.core.config import settings

from .auth import router as auth_router
<<<<<<< HEAD
from .post import router as post_router
from .superuser import router as superuser_router
=======
from .department import router as department_router
from .person import router as person_router
from .role import router as role_router
>>>>>>> dcd45f201b9f0ceed7c3e04dc25c0f870acec82e
from .user import router as user_router
from .role import router as role_router
from .department import router as department_router
from .person import router as person_router


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
    person_router,
)
router.include_router(
    department_router,
)

router.include_router(
    role_router,
)
