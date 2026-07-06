
from fastapi import FastAPI

from llm_service import LLMService
from t2i_service import T2IService


app = FastAPI()


@app.get("/llm_gen")
async def llm_gen():
    llm_service = LLMService('яблоzаткни')
    captions, prompts = await llm_service.generate_post()
    print('\n\n', captions, prompts)


@app.get("/t2i_gen")
async def t2i_gen():
    trigger_word = 'cerohumano'
    t2i_service = T2IService(trigger_word, f'{trigger_word}_v1.safetensors')
    await t2i_service.generate(f"A 1910s portrait of {trigger_word} as a classic bunny")
