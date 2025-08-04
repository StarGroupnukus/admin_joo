from datetime import datetime

from sqlalchemy import TIMESTAMP, MetaData, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from app.core.config import settings
from app.core.utils.case_converter import convert_and_pluralize


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.db.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{convert_and_pluralize(cls.__name__)}"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        server_default=None,
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        default=None,
        server_default=None,
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
    )
