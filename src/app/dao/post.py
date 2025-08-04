from app.dao import BaseDAO
from app.models.post import Post


class PostDAO(BaseDAO):
    model = Post
