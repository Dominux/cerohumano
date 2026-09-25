import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from queue_manager import QueueManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue_manager = QueueManager()
    daemon_task = asyncio.create_task(queue_manager.start_loop())

    yield

    queue_manager.stop()
    daemon_task.cancel()
    await asyncio.gather(daemon_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)
