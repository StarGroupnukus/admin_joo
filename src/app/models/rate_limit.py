from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RateLimit(Base):
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    path: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    period: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    tier_id: Mapped[int] = mapped_column(
        ForeignKey("tiers.id"),
        index=True,
    )
