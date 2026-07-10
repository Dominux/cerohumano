import asyncio
import datetime
import logging
import random

import httpx
from sqlalchemy import select, func
from sqlalchemy.orm import Session

# from app.models import CeroHumanoModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class GenerationalAPIManager:
    def __init__(
        self,
        api_url: str,
        db_engine,
        min_runs: int,
        max_runs: int,
        poll_interval_seconds: float = 60.0
    ):
        self.api_url = api_url
        self.engine = db_engine
        self.min_runs = min_runs
        self.max_runs = max_runs

        # How often to check if a new day has arrived when idle
        self.poll_interval = poll_interval_seconds

        self._is_running = False
        self._task: asyncio.Task | None = None

    async def _get_dynamic_payload(self) -> dict | None:
        """Retrieves operational data from your CeroHumano model to build the API payload."""
        try:
            # Open a synchronous block or use AsyncSession depending on engine setup
            with Session(self.engine) as session:
                stmt = select(CeroHumanoModel).order_by(func.random()).limit(1)
                user = session.execute(stmt).scalar_or_none()

                if not user:
                    logging.warning("No users found in cerohumanos table. Skipping generation step.")
                    return None

                return {
                    "username": user.username,
                    "lora_name": user.lora_name,
                    "default_cup_enhancer": user.default_cup_enhancer
                }
        except Exception as e:
            logging.error(f"Database retrieval failed: {e}")
            return None

    async def _execute_generation(self, client: httpx.AsyncClient, payload: dict) -> bool:
        """Sends the request. Returns True if successful, False if it failed."""
        try:
            response = await client.post(self.api_url, json=payload, timeout=45.0)
            response.raise_for_status()
            logging.info(f"Generation complete! Response: {response.status_code}")
            return True
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logging.error(f"API communication failure: {e}")
            return False

    async def _scheduler_loop(self):
        """Runs generation batches back-to-back, then enters retrieval polling mode."""
        current_day = datetime.date.today()

        # Decide the randomized workflow target for today
        target_runs_today = random.randint(self.min_runs, self.max_runs)
        completed_runs_today = 0

        logging.info(f"New day initialized. Target run count for today: {target_runs_today}")

        async with httpx.AsyncClient() as client:
            while self._is_running:
                # 1. Reset metrics if a calendar day rollover occurred
                today = datetime.date.today()
                if today != current_day:
                    current_day = today
                    target_runs_today = random.randint(self.min_runs, self.max_runs)
                    completed_runs_today = 0
                    logging.info(f"Calendar day shifted. New target defined: {target_runs_today}")

                # 2. Back-to-Back Generation Mode (No interval delays)
                if completed_runs_today < target_runs_today:
                    payload = await self._get_dynamic_payload()

                    if payload:
                        success = await self._execute_generation(client, payload)
                        if success:
                            completed_runs_today += 1
                            logging.info(f"Progress: [{completed_runs_today}/{target_runs_today}] complete.")
                        else:
                            # Short fallback wait if the remote API crashes to avoid spinning tight loops
                            logging.warning("API failed. Backing off for 5 seconds before retrying...")
                            await asyncio.sleep(5.0)
                    else:
                        # Database was empty or unreachable; wait before looking again
                        await asyncio.sleep(10.0)

                # 3. Retrieval/Idle Polling Mode
                else:
                    # Target met! Sleep until the database metrics indicate a calendar day turnover.
                    logging.debug(f"Target met ({completed_runs_today}). Polling for next calendar day...")
                    await asyncio.sleep(self.poll_interval)

    def start(self):
        """Spawns the loop process in the background."""
        if not self._is_running:
            self._is_running = True
            self._task = asyncio.create_task(self._scheduler_loop())
            logging.info(f"Manager active. Generation range target constraint: [{self.min_runs}-{self.max_runs}]")

    async def stop(self):
        """Gracefully halts execution loops."""
        if self._is_running:
            self._is_running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logging.info("Manager stopped cleanly.")
