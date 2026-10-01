import os
from typing import List, Optional

from pydantic import BaseModel
import httpx

from app.models.cerohumano import CeroHumanoCupDescription
from clients.generation_setting_picker import (
    pick_random_clothes,
    pick_random_cup,
    pick_random_looking_direction,
    pick_random_position,
    pick_random_settings,
    pick_random_camera_angle,
    pick_random_crop,
    pick_random_photo_type,
)


LLM_HOST = os.environ['LLM_HOST']
LLM_PORT = os.environ['LLM_PORT']
LLM_URL = f'http://{LLM_HOST}:{LLM_PORT}/api/chat'
BASE_TRIGGER_WORD = 'cerohumano'
# Set a safe, long timeout for the entire request lifecycle
LLM_TIMEOUT = httpx.Timeout(300.0, connect=10.0)


class ChatMessage(BaseModel):
    role: str
    content: str
    images: Optional[List[str]] = None


class OllamaChatResponse(BaseModel):
    model: str
    created_at: str
    message: ChatMessage
    done: bool
    # Performance metrics (optional but returned by Ollama)
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


class LLMClient:
    def __init__(self, trigger_word: str, min_cup: CeroHumanoCupDescription) -> None:
        self.trigger_word = trigger_word
        self.min_cup = min_cup

    async def generate_post(self, images_amount=4) -> 'tuple[str, list[str]]':
        post_settings = pick_random_settings()
        clothes = pick_random_clothes()
        cup = pick_random_cup(self.min_cup)
        if cup:
            post_settings['bust'] = cup.name

        prompts = []

        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            for photo_number in range(images_amount):
                msg_settings = post_settings.copy()
                msg_settings['photo crop'] = pick_random_crop()
                msg_settings['camera angle'] = pick_random_camera_angle()
                msg_settings['photo type'] = pick_random_photo_type()
                msg_settings['looking direction'] = pick_random_looking_direction()
                msg_settings['position'] = pick_random_position()

                if photo_number == 0:
                    msg_settings['clothes'] = clothes
                elif photo_number == 1:
                    msg_settings['clothes'] = clothes
                    msg_settings['nudity'] = 'topless'
                else:
                    msg_settings['nudity'] = 'completely naked'

                msg_content = (
                    f"You are a prompt reconstruction engine for Krea 2 Turbo. "
                    f"You will be given a raw text description or image tags. "
                    f"Your goal is to clean up, expand, and structure this data into a highly efficient Krea 2 Turbo natural language prompt.\n\n"
                    f"CRITICAL CONSTRAINTS:\n"
                    f"1. NEVER use generic gender nouns like"
                    f'"woman", "girl", "female", "lady", "man", or "boy", use the name "Cerohumano" instead, but only once and never use it again! '
                    f'Further use words like "she" and "her"\n'
                    f"2. She must be looking at camera\n"
                    f"3. USE GIVEN SETTING: {msg_settings}\n\n"
                    f"Standardize the output format strictly into this block sequence:\n"
                    f"A [Camera Angle, Photo Type, & Photo Crop] of [Name + Subject Features]. [Attire Details]. "
                    f"[Pose, Expression, & Action]. [Environment & Location]. [Camera, Framing, & Depth]. [Lighting, Mood, & Texture].\n\n"
                    f"Output ONLY the finalized prompt text inside a single paragraph. No intro, no commentary, no conversational filler."
                )

                payload = {
                    "model": "t2i-prompt-post",
                    "stream": False,
                    "think": False,
                    "keep_alive": 0, # to unload the model after the request
                    "messages": [
                        {
                            "role": "user",
                            "content": msg_content,
                        },
                    ],
                }

                prompt = await self._request_llm(client, payload)

                # cleaning prompt
                prompt = prompt.lower().replace(BASE_TRIGGER_WORD, self.trigger_word)

                prompts.append(prompt)

            return '❤️❤️❤️', prompts

    @staticmethod
    async def _request_llm(client, payload) -> str:
        try:
            # Send payload using the 'json' parameter (automatically sets Content-Type header)
            response = await client.post(LLM_URL, json=payload)

            # Raise an exception for 4xx or 5xx status codes
            response.raise_for_status()

            # 3. Parse the JSON response
            response_data = response.json()

        except httpx.HTTPStatusError as e:
            print(f"Server error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Network error occurred: {e}")
            raise

        else:
            print("Successful LLM response")
            # Parse directly into the Pydantic model
            ollama_response = OllamaChatResponse.model_validate(response_data)
            return ollama_response.message.content
