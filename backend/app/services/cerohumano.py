from app.models.cerohumano import CeroHumanoCupDescription
from app.services.base import BaseService
from app.repositories import CeroHumanoRepository
from app.models import CeroHumanoModel


class CeroHumanoService(BaseService[CeroHumanoModel]):
    repository_class = CeroHumanoRepository

    async def set_cup(self, cerohumano: CeroHumanoCupDescription):
        return await self.repository.set_cup(cerohumano)
