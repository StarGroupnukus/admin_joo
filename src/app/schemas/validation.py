from typing import Annotated, Optional

from pydantic import Field
from pydantic.networks import AnyHttpUrl

# Константы
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 20

PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 32

MIN_TITLE_LENGTH = 2
MAX_TITLE_LENGTH = 30

MIN_TEXT_LENGTH = 1
MAX_TEXT_LENGTH = 63206

DEFAULT_MEDIA_URL = "https://www.postimageurl.com"


def zero_to_none(num: int) -> int | None:
    if num == 0:
        return None
    return num


def sanitize_path(path: str) -> str:
    return path.strip("/").replace("/", "_")


def serialize_image_url(
    http_url: Optional[AnyHttpUrl],
) -> Optional[str]:
    if http_url is None:
        return None
    return str(http_url)


NAME_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        min_length=MIN_NAME_LENGTH,
        max_length=MAX_NAME_LENGTH,
        examples=["User Userberg"],
        default=None,
    ),
]
PASSWORD_FIELD = Annotated[
    str,
    Field(
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
        examples=["pass123"],
    ),
]

PHONE_NUMBER_FIELD = Annotated[
    str, Field(pattern=r"^[1-9]\d{1,14}$", examples=["998991234567"])
]

PHONE_NUMBER_FIELD_UPDATE = Annotated[
    str | None,
    Field(
        pattern=r"^[1-9]\d{1,14}$",
        examples=["998991112233"],
        default=None,
    ),
]

VERIFY_CODE_FIELD = Annotated[
    str,
    Field(pattern=r"^\d{5}$", examples=["12345"]),
]

TITLE_FIELD = Annotated[
    str,
    Field(
        min_length=MIN_TITLE_LENGTH,
        max_length=MAX_TITLE_LENGTH,
        examples=["This is my post"],
    ),
]
TITLE_FIELD_UPDATE = Annotated[
    Optional[str],
    Field(
        min_length=MIN_TITLE_LENGTH,
        max_length=MAX_TITLE_LENGTH,
        examples=["This is my updated post"],
        default=None,
    ),
]
TEXT_FIELD = Annotated[
    str,
    Field(
        min_length=MIN_TEXT_LENGTH,
        max_length=MAX_TEXT_LENGTH,
        examples=["This is the content of my post."],
    ),
]
TEXT_FIELD_UPDATE = Annotated[
    Optional[str],
    Field(
        min_length=MIN_TEXT_LENGTH,
        max_length=MAX_TEXT_LENGTH,
        examples=["This is the updated content of my post."],
        default=None,
    ),
]
MEDIA_URL_FIELD = Annotated[
    Optional[AnyHttpUrl],
    Field(
        examples=[DEFAULT_MEDIA_URL],
        default=None,
    ),
]
