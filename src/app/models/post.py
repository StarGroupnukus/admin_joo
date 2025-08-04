from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixins import UserRelationMixin


class Post(UserRelationMixin, Base):
    title: Mapped[str] = mapped_column(String(30))
    text: Mapped[str] = mapped_column(String(63206))
    image_url: Mapped[str | None] = mapped_column(
        String,
        default=None,
    )
    _user_id_unique = False
    _user_back_populates = "posts"
