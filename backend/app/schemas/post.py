import uuid

from app.schemas.base import BaseSchema
from app.schemas import CeroHumanoResponse
from app.models.attachment import AttachmentType


class AttachmentPostSchema(BaseSchema):
    id: uuid.UUID
    file_type: AttachmentType


class PostWithAttachmentsResponse(BaseSchema):
    id: uuid.UUID
    author: CeroHumanoResponse
    title: str
    attachments: 'list[AttachmentPostSchema]'

