from app.services.base import BaseService
from app.repositories import PostRepository
from app.models import PostModel


class PostService(BaseService[PostModel]):
    repository_class = PostRepository
