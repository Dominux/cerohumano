from pathlib import Path
from typing import Any

from app.services.base import BaseService
from app.repositories import AttachmentRepository
from app.models import AttachmentModel, AttachmentType


BASE_PATH = Path('/data')


class AttachmentService(BaseService[AttachmentModel]):
    repository_class = AttachmentRepository

    @staticmethod
    def _get_filepath(attach: AttachmentModel):
        filepath = BASE_PATH / str(attach.id)
        suffix = 'png' if attach.file_type == AttachmentType.IMAGE else 'mp4'
        return filepath.with_suffix(suffix)

    async def create(self, payload: dict[str, Any], content: bytes) -> AttachmentModel:
        attach = await super().create(payload)
        self._save_file(attach, content)
        return attach

    def _save_file(self, attach: AttachmentModel, content: bytes):
        filepath = self._get_filepath(attach)
        with filepath.open('wb') as f:
            f.write(content)

    def _get_file(self, attach: AttachmentModel):
        return self._get_filepath(attach)

    def _delete_file(self, attach: AttachmentModel):
        filepath = self._get_filepath(attach)
        filepath.unlink(missing_ok=True)
