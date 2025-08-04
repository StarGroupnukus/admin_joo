from http import HTTPStatus
from typing import Union

from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        # Используем message, если он указан, иначе используем detail
        actual_detail = message if message is not None else detail

        if not actual_detail:  # pragma: no cover
            actual_detail = HTTPStatus(status_code).description
        super().__init__(
            status_code=status_code,
            detail=actual_detail,
        )


class BadRequestException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            message=message,
        )  # pragma: no cover


class NotFoundException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            message=message,
        )  # pragma: no cover


class ForbiddenException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            message=message,
        )  # pragma: no cover


class UnauthorizedException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            message=message,
        )  # pragma: no cover


class UnprocessableEntityException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            message=message,
        )  # pragma: no cover


class DuplicateValueException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            message=message,
        )


class RateLimitException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            message=message,
        )  # pragma: no cover


class TooManyRequestsException(CustomException):
    def __init__(
        self,
        detail: Union[str, None] = None,
        message: Union[str, None] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            message=message,
        )  # pragma: no cover
