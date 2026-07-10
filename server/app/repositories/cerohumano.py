from app.models import CeroHumanoModel
from app.repositories.base import BaseRepository


class CeroHumanoRepository(BaseRepository[CeroHumanoModel]):
    model = CeroHumanoModel
