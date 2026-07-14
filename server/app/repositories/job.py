from typing import Any, Sequence

import sqlalchemy as sa

from app.models import JobModel, JobStatus, JobPriority
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobModel]):
    model = JobModel

    async def create_batch(self, batch_data: list[dict[str, Any]]) -> Sequence[JobModel]:
        """
        Instantiate and persist a batch of model records efficiently in a single transaction.
        :param batch_data: A list of dictionaries containing model attributes.
        :return: A sequence of the fully instantiated and persisted ORM model objects.
        """
        if not batch_data:
            return []

        # 1. Map list of raw dictionaries into ORM object instances
        db_objects = [self.model(**obj_dict) for obj_dict in batch_data]

        # 2. Stage all objects into the session tracking layer at once
        self.session.add_all(db_objects)

        # 3. Commit the transaction to write rows back-to-back to the database
        await self.session.commit()

        # 4. Refresh objects so that database-generated defaults (like UUID ids, created_at timestamps)
        # are populated and readable on the returned Python objects.
        for obj in db_objects:
            await self.session.refresh(obj, attribute_names=["cerohumano"])

        return db_objects


    async def fetch_last_job(
        self,
        priority: JobPriority = JobPriority.STANDARD,
        status: JobStatus = JobStatus.DONE,
    ) -> 'JobModel | None':
        stmt = (
            sa.select(JobModel)
            .where(
                JobModel.priority == priority,
                JobModel.status == status,
            )
            .order_by(JobModel.created_at.desc())
            .limit(1)
        )

        result = await self.session.scalars(stmt)
        return result.first()

    async def fetch_next_job(self) -> 'JobModel | None':
        stmt = (
            sa.select(JobModel)
            .where(JobModel.status == JobStatus.PENDING)
            .order_by(JobModel.priority.desc(), JobModel.created_at.asc())
            .limit(1)
        )

        result = await self.session.scalars(stmt)
        return result.first()
