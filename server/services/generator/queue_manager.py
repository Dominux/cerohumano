import asyncio
import datetime
import logging
import random
import sys

from app.repositories import JobRepository, CeroHumanoRepository, PostRepository
from app.models import JobStatus, JobType, JobModel, AttachmentType
from app.services import AttachmentService
from app.common.database import get_db_context
from t2i_service import T2IService
from llm_service import LLMService


logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)

# 2. Prevent logs from duplicating if they bubble up to the root handler
logger.propagate = False

# 3. Create a StreamHandler targeting standard system output (sys.stdout)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)

# 4. Define a clean, scannable format (Timestamp, Log Level, Message)
log_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) -> %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
stdout_handler.setFormatter(log_formatter)

# 5. Bind the handler to your daemon logger
logger.addHandler(stdout_handler)


class QueueManager:
    def __init__(
        self,
        daily_posts_amount: int = 5,
        polling_interval: float = 5.0,
    ):
        self.daily_posts_amount = daily_posts_amount
        self.polling_interval = polling_interval
        self._is_running = False

    async def start_loop(self):
        """Infinite loop driving the continuous background execution."""
        self._is_running = True
        logger.info("Background Generation Worker started successfully.")

        while self._is_running:
            try:
                await self.run_single_cycle()
            except Exception as e:
                logger.error(f"Unexpected error in background cycle loop: {e}")

            # Use short non-blocking sleep before pulling the next queue item
            await asyncio.sleep(self.polling_interval)

    async def run_single_cycle(self):
        async with get_db_context() as session:
            repo = JobRepository(session)

            # 1. Fetch the highest priority job from the queue
            job = await repo.fetch_next_job()

            if not job:
                # 2. If it's a new day - create daily jobs batch
                last_done_standard_job = await repo.fetch_last_job()
                if last_done_standard_job and not last_done_standard_job.created_at.date() < datetime.date.today():
                    return  # Queue is empty, loop will sleep and check again

                # creating daily batch
                cerohumanos_ids = await CeroHumanoRepository(session).list_ids()
                if not cerohumanos_ids:
                    logger.info('Cero cerohumanos, skipping job creation')
                    return

                daily_batch = [
                    {
                        'cerohumano_id': random.choice(cerohumanos_ids)
                    }
                    for _ in range(self.daily_posts_amount)
                ]
                jobs = await repo.create_batch(daily_batch)
                job = jobs[0]

            job = await repo.update(job, update_data={'status': JobStatus.PROCESSING})

        if job.job_type == JobType.POST:
            caption, images = await self._generate_post(job)
        else:
            logger.error(f'Unexpected job type: {job.job_type}')
            return

        async with get_db_context() as session:
            attach_service = AttachmentService(session)
            post = await PostRepository(session).create(
                {
                    'title': caption,
                    'author': job.cerohumano,
                }
            )
            for img in images:
                img = await attach_service.create(
                    payload={
                        'post': post,
                        'file_type': AttachmentType.IMAGE,
                        'author': job.cerohumano,
                    },
                    content=img,
                )

    async def _generate_post(self, job: 'JobModel'):
        images_amount = random.randint(3, 7)

        llm_service = LLMService(job.cerohumano.trigger_word)
        caption, prompts = await llm_service.generate_post(images_amount)

        print('\n\n', caption, prompts)

        t2i_service = T2IService(job.cerohumano.trigger_word, job.cerohumano.lora_name)
        images = [await t2i_service.generate(prompt) for prompt in prompts]
        return caption, images

    def stop(self):
        """Signals the background runner loop to halt execution."""
        logger.info("Signaling background worker shutdown sequence...")
        self._is_running = False
