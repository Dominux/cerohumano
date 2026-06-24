
from fastapi import FastAPI

from llm_service import LLMService


app = FastAPI()


@app.get("/gen")
async def main():
    llm_service = LLMService('яблоzаткни')
    captions, prompts = await llm_service.generate_post()
    print('\n\n', captions, prompts)

