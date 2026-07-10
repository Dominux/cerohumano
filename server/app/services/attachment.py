from app.services.base import BaseService
from app.repositories import AttachmentRepository
from app.models import AttachmentModel


class AttachmentService(BaseService[AttachmentModel]):
    repository_class = AttachmentRepository
