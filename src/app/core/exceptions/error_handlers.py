import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError

from app.core.exceptions.http_exceptions import CustomException

logger = logging.getLogger(__name__)


def register_errors_handlers(app: FastAPI) -> None:
    @app.exception_handler(ValidationError)
    def handle_pydantic_validation_error(
        request: Request,
        exc: ValidationError,
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Unhandled error",
                "error": exc.errors(),
            },
        )

    @app.exception_handler(DatabaseError)
    def handle_db_error(
        request: Request,
        exc: ValidationError,
    ) -> ORJSONResponse:
        logger.error(
            "Unhandled database error",
            exc_info=exc,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )

    @app.exception_handler(ResponseValidationError)
    def handle_response_validation_error(
        request: Request,
        exc: ResponseValidationError,
    ) -> ORJSONResponse:
        logger.error(
            "Response validation error",
            exc_info=exc,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Response validation error",
                "error": str(exc),
            },
        )

    @app.exception_handler(CustomException)
    async def custom_exception_handler(
        request: Request,
        exc: CustomException,
    ):
        return ORJSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request,
        exc: Exception,
    ) -> ORJSONResponse:
        logger.error(
            "Unhandled error",
            exc_info=exc,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "An unexpected error has occurred. "
                "Our admins are already working on it."
            },
        )
