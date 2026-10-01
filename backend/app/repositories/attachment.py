from app.models import AttachmentModel
from app.repositories.base import BaseRepository


class AttachmentRepository(BaseRepository[AttachmentModel]):
    model = AttachmentModel
