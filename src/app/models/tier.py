from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Tier(Base):
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="tier",
    )
