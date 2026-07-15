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
        if attach.file_type == AttachmentType.IMAGE:
            dir = 'images'
            suffix = '.png'
        elif attach.file_type == AttachmentType.VIDEO:
            dir = 'videos'
            suffix = '.mp4'

        full_dir = BASE_PATH / dir
        full_dir.mkdir(parents=True, exist_ok=True)

        return full_dir / Path(str(attach.id)).with_suffix(suffix)

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
