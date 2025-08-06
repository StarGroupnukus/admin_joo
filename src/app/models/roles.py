<<<<<<< HEAD
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
=======

from sqlalchemy import String
>>>>>>> dcd45f201b9f0ceed7c3e04dc25c0f870acec82e
from sqlalchemy.orm import Mapped, mapped_column


from .base import Base

class Role(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    
