from app.services.base import BaseService
from app.repositories import CeroHumanoRepository
from app.models import CeroHumanoModel


class CeroHumanoService(BaseService[CeroHumanoModel]):
    repository_class = CeroHumanoRepository
