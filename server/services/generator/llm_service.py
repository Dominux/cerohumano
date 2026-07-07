import os
from typing import List, Optional

from pydantic import BaseModel
import httpx


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


class LLMService:
    def __init__(self, trigger_word: str) -> None:
        self.trigger_word = trigger_word

    async def generate_post(self, images_amount=4) -> 'tuple[str, list[str]]':
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            # 1. getting caption
            first_msg = (
                "Act as a close female friend posting a hot, "
                "sexy photo from a recent fun night out or a private moment. "
                "Write a single-line, flirtatious, casual caption in your own voice "
                "describing the vibe, outfit, or location. "
                "Keep it realistic, authentic, and appealing without sounding like "
                "a commercial influencer. Do not include any links or marketing text. "
                "Output only the caption line."
            )

            payload = {
                "model": "t2i-prompt-post",
                "stream": False,
                "think": False,
                "keep_alive": 0, # to unload the model after the request
                "messages": [
                    {
                        "role": "user",
                        "content": first_msg,
                    },
                ],
            }

            caption = await self._request_llm(client, payload)

            # 2. getting prompts list
            payload['messages'].extend(
                [
                    {
                        "role": "assistant",
                        "content": caption,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Perfect. Now, based EXACTLY on the vibe, outfit, "
                            f"and setting implied in that caption, generate exactly {images_amount} distinct, "
                            "highly appealing, and striking image generation prompts (one per line) "
                            "for a single continuous photo session.\n\nFollow these rules perfectly:\n"
                            "1. Describe the scene directly from a cinematic camera perspective.\n"
                            "2. You MUST include the exact trigger word \"cerohumano\" in every single prompt line to represent her.\n"
                            "3. Use pronouns like \"she\" or \"her\" to describe her positioning "
                            "and actions naturally from the camera's point of view.\n"
                            "4. Do NOT use generic words like \"girl\", \"woman\", \"model\", or \"lady\". "
                            "Do not describe her baseline natural features (hair color, eye color, body type).\n"
                            "5. Focus heavily on her alluring styling, the textures of her clothing (matching the caption), "
                            "realistic lighting, professional camera angles, and hot, natural poses to make the shots "
                            "look incredibly attractive and real. Do not include numbers or bullet points."
                        ),
                    },
                ]
            )

            prompts_text = await self._request_llm(client, payload)
            prompts = []
            for line in reversed(prompts_text.splitlines()):
                if BASE_TRIGGER_WORD in line:
                    prompt = line.replace(BASE_TRIGGER_WORD, self.trigger_word)
                    prompts.append(prompt)

                    if len(prompts) == images_amount:
                        break

            return caption, prompts

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
        except httpx.RequestError as e:
            print(f"Network error occurred: {e}")

        else:
            print("Success:", response_data)
            # Parse directly into the Pydantic model
            ollama_response = OllamaChatResponse.model_validate(response_data)
            return ollama_response.message.content
