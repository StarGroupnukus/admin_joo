<<<<<<< HEAD
from typing import TYPE_CHECKING
=======

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
>>>>>>> dcd45f201b9f0ceed7c3e04dc25c0f870acec82e

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base  

class Department(Base):
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id"),
        nullable=False,
    )
    