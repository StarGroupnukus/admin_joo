import logging

import uvicorn
from fastapi import HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router as api_v1_router
from app.core.config import SOURCE_DIR, settings
from app.create_app import create_app

logger = logging.getLogger(__name__)

main_app = create_app()

main_app.include_router(
    api_v1_router,
    prefix=settings.api.prefix,
)


main_app.mount(
    "/storage",
    StaticFiles(directory=str(SOURCE_DIR / "storage/")),
    name="storage",
)
main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # в продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@main_app.middleware("http")
async def limit_body_size(request: Request, call_next):
    content_length = request.headers.get("Content-Length")
    if (
        content_length and int(content_length) > settings.upload_settings.MAX_FILE_SIZE
    ):  # 10 MB limit
        raise HTTPException(
            status_code=413,
            detail="Payload Too Large",
        )
    return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.HOST,
        port=settings.run.PORT,
        reload=True,
    )
