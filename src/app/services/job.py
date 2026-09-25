from app.services.base import BaseService
from app.repositories import JobRepository
from app.models import JobModel


class JobService(BaseService[JobModel]):
    repository_class = JobRepository
