import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from llm_service import LLMService
from queue_manager import QueueManager
from t2i_service import T2IService


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue_manager = QueueManager()
    daemon_task = asyncio.create_task(queue_manager.start_loop())

    yield

    queue_manager.stop()
    daemon_task.cancel()
    await asyncio.gather(daemon_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/llm_gen")
async def llm_gen():
    llm_service = LLMService('яблоzаткни')
    caption, prompts = await llm_service.generate_post()
    print('\n\n', caption, prompts)


@app.get("/t2i_gen")
async def t2i_gen():
    trigger_word = 'cerohumano'
    t2i_service = T2IService(trigger_word, f'{trigger_word}_v1.safetensors')
    await t2i_service.generate(f"A 1910s portrait of {trigger_word} as a classic bunny")


@app.get('/gen_post')
async def gen_post(trigger_word: str, lora_name: str):
    llm_service = LLMService(trigger_word)
    caption, prompts = await llm_service.generate_post()

    print('\n\n', caption, prompts)

    t2i_service = T2IService(trigger_word, lora_name)
    for prompt in prompts:
        await t2i_service.generate(prompt)
