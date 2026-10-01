import uuid
from typing import Any

from app.schemas.base import BaseSchema


class AttachmentResponse(BaseSchema):
    meta_data: dict[str, Any] | None = None
    author_id: uuid.UUID
    post_id: uuid.UUID | None = None
