from typing import Sequence
import uuid

import sqlalchemy as sa

from app.models import CeroHumanoModel
from app.repositories.base import BaseRepository


class CeroHumanoRepository(BaseRepository[CeroHumanoModel]):
    model = CeroHumanoModel

    async def list_ids(self) -> 'Sequence[uuid.UUID]':
        stmt = sa.select(self.model.id)

        # Execute asynchronously using scalars directly
        result = await self.session.scalars(stmt)
        return result.all()
