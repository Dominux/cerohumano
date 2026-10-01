from app.models import PostModel
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[PostModel]):
    model = PostModel
