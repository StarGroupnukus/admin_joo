from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )
    phone_number: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String)

    image_url: Mapped[str] = mapped_column(
        String,
        default="https://profileimageurl.com",
    )
    is_active: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_verified: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
