from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base  

class Branch(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )
    rating_1_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    rating_2_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    rating_3_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    rating_4_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    rating_5_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
