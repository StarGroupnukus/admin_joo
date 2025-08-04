from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TokenBlacklist(Base):
    jti: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )
    is_blacklisted: Mapped[bool] = mapped_column(
        default=True,
        server_default="true",
    )
