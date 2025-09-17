from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base  

class Branch(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )
    rating: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=5,
    )
    voice_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    