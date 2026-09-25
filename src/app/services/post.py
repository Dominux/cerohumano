import uuid

from app.services.base import BaseService
from app.services.attachment import AttachmentService
from app.repositories import PostRepository
from app.models import PostModel, AttachmentType


class PostService(BaseService[PostModel]):
    repository_class = PostRepository

    async def upload_post(
        self,
        author_id: uuid.UUID,
        caption: str,
        files
    ) -> PostModel:
        # creating post
        payload = {
            'title': caption,
            'author_id': author_id,
        }
        post = await self.create(payload)

        # creaing attachs
        attach_service = AttachmentService(self.repository.session)
        for file in files:
            attach = await attach_service.create(
                payload={
                    'post': post,
                    'file_type': AttachmentType.IMAGE,
                    'author_id': author_id,
                },
                file=file,
            )

        return post
