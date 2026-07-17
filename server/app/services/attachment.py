from pathlib import Path
from typing import Any

import aiofiles
from fastapi import UploadFile

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

    async def create(self, payload: dict[str, Any], file: UploadFile) -> AttachmentModel:
        attach = await super().create(payload)
        await self._save_file(attach, file)
        return attach

    async def _save_file(self, attach: AttachmentModel, file: UploadFile):
        filepath = self._get_filepath(attach)
        async with aiofiles.open(filepath, "wb") as out_file:
            while chunk := await file.read(1024 * 64):  # Read in 64kb chunks
                await out_file.write(chunk)

    def _get_file(self, attach: AttachmentModel):
        return self._get_filepath(attach)

    def _delete_file(self, attach: AttachmentModel):
        filepath = self._get_filepath(attach)
        filepath.unlink(missing_ok=True)
