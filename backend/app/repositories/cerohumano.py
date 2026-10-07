from typing import Sequence
import uuid

import sqlalchemy as sa

from app.models import CeroHumanoModel
from app.repositories.base import BaseRepository
from app.schemas.cerohumano import CeroHumanoSetCup


class CeroHumanoRepository(BaseRepository[CeroHumanoModel]):
    model = CeroHumanoModel

    async def list_ids(self) -> 'Sequence[uuid.UUID]':
        stmt = sa.select(self.model.id)

        # Execute asynchronously using scalars directly
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_by_username(self, username: str):
        stmt = sa.select(self.model).filter_by(username=username)

        result = await self.session.scalars(stmt)
        return result.one()

    async def set_cup(self, cerohumano: CeroHumanoSetCup):
        return await self.update(cerohumano.id, {'min_cup': cerohumano.min_cup})
