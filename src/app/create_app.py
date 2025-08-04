import logging
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import ORJSONResponse

from app.api.dependencies.user import get_current_superuser
from app.core.config import EnvironmentOption, settings
from app.core.exceptions.error_handlers import register_errors_handlers

from .app_lifespan import lifespan

logger = logging.getLogger(__name__)


def register_static_docs_routes(app: FastAPI):
    @app.get("/docs", include_in_schema=False)
    def custom_swagger_ui_html(
        current_user: Any = Depends(
            get_current_superuser
            if settings.app_settings.environment.current.value
            == EnvironmentOption.STAGING.value
            else lambda: None
        ),
    ):
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
    def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", include_in_schema=False)
    def redoc_html(
        current_user: Any = Depends(
            get_current_superuser
            if settings.app_settings.environment.current.value
            == EnvironmentOption.STAGING.value
            else lambda: None
        ),
    ):
        return get_redoc_html(
            openapi_url=app.openapi_url,
            title=app.title + " - ReDoc",
            redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
        )


# -------------- application --------------
def create_app() -> FastAPI:
    logger.info("Starting application setup...")
    cond = (
        settings.app_settings.environment.current.value
        == EnvironmentOption.PRODUCTION.value
    )
    logger.info(
        f"Current environment: {settings.app_settings.environment.current.value} cond: {cond}"
    )
    app = FastAPI(
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
        docs_url=None if cond else "/docs",
        redoc_url=None if cond else "/redoc",
        openapi_url=None if cond else "/openapi.json",
    )
    if not cond:
        logger.info("Registering static docs routes...")
        register_static_docs_routes(app)
        app.docs_url = "/docs"
        app.redoc_url = "/redoc"

    logger.info("Setting app metadata...")
    app.title = settings.app_settings.APP_NAME
    app.description = settings.app_settings.APP_DESCRIPTION
    app.contact = {
        "name": settings.app_settings.CONTACT_NAME,
        "email": settings.app_settings.CONTACT_EMAIL,
    }
    app.license_info = {"name": settings.app_settings.LICENSE_NAME}
    register_errors_handlers(app)
    logger.info("Application setup completed successfully")
    return app
