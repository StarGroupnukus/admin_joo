from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


from .base import Base

class Role(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    
