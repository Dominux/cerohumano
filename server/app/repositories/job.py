from app.models import JobModel
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobModel]):
    model = JobModel
