import asyncio
import datetime
import logging

from app.services.base import BaseService
from app.repositories import JobRepository
from app.models import JobModel, JobPriority
from app.common.database import get_db_context
from server.app.models.job import JobStatus


logger = logging.getLogger("worker")


class QueueManager:
    def __init__(
        self,
        api_url: str,
        daily_posts_amount: int = 15,
        polling_interval: float = 5.0,
    ):
        self.api_url = api_url
        self.daily_posts_amount = daily_posts_amount
        self.polling_interval = polling_interval
        self._is_running = False

    async def start_loop(self):
        """Infinite loop driving the continuous background execution."""
        self._is_running = True
        logger.info("Background Generation Worker started successfully.")

        while self._is_running:
            try:
                await self.run_single_generation_cycle()
            except Exception as e:
                logger.error(f"Unexpected error in background cycle loop: {e}")

            # Use short non-blocking sleep before pulling the next queue item
            await asyncio.sleep(self.polling_interval)

    async def run_single_generation_cycle(self):
        async with get_db_context() as session:
            repo = JobRepository(session)

            # 1. Fetch the highest priority job from the queue
            job = await repo.fetch_next_job()

            if not job:
                # 2. If it's a new day - create daily jobs batch
                last_done_standard_job = await repo.fetch_last_job()
                if not last_done_standard_job.created_at.date() < datetime.date.today():
                    return  # Queue is empty, loop will sleep and check again

                # creating daily batch
                daily_batch = [{} for _ in range(self.daily_posts_amount)]
                jobs = await repo.create_batch(daily_batch)
                job = jobs[0]

            job = await repo.update(job, update_data={'status': JobStatus.PROCESSING})

        # TODO...

        # Mark it as processing so other concurrent hooks don't touch it
        job.is_processing = True
        await session.commit()

        logger.info(f"Processing job {job.id} for user {job.username}...")

        # 2. Fire your external generative API logic
        success = await self._call_generational_api(job)

        if success:
            await session.delete(job)  # Clean it out on success
        else:
            job.is_processing = False  # Return to queue on failure

    async def _generate_post(self, job) -> bool:
        # Insert your httpx async request logic here
        return True

    def stop(self):
        """Signals the background runner loop to halt execution."""
        logger.info("Signaling background worker shutdown sequence...")
        self._is_running = False
