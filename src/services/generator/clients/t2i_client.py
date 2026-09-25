import asyncio
import copy
import json
import os
import random

import httpx


T2I_HOST = os.environ['T2I_HOST']
T2I_PORT = os.environ['T2I_PORT']
T2I_BASEURL = f'http://{T2I_HOST}:{T2I_PORT}'
T2I_TIMEOUT = httpx.Timeout(
    timeout=60.0,       # Global fallback limit (60 seconds)
    connect=10.0,       # Time allowed to establish the socket connection
    read=None,          # DISABLE read timeout so slow image generation won't crash your script
    write=30.0          # Time allowed to upload your workflow JSON or heavy input images
)


with open("./clients/ZIT_cerohumano_workflow.json", "r") as f:
    WORKFLOW = json.load(f)


class T2IClient:
    def __init__(self, trigger_word: str, lora_name: str) -> None:
        self.trigger_word = trigger_word
        self.lora_name = lora_name

    async def generate(self, prompt: str) -> bytes:
        async with httpx.AsyncClient(timeout=T2I_TIMEOUT) as client:
            wf = copy.deepcopy(WORKFLOW)

            # positive prompt
            positive_prompt_inputs = wf["57:27"]["inputs"]
            positive_prompt_inputs["text"] = f"{prompt} {positive_prompt_inputs['text']}"

            # lora name
            wf["57:69"]["inputs"]["lora_name"] = self.lora_name

            # seed
            wf["57:86"]["inputs"]["seed"] = random.randint(0, 18446744073709551615)

            return await self._request_comfy(client, wf)

    @classmethod
    async def _request_comfy(cls, client, workflow) -> bytes:
        payload = {"prompt": workflow, "client_id": "cerohumano_app"}

        try:
            # 1. Queue the prompt
            response = await client.post(f"{T2I_BASEURL}/prompt", json=payload)
            response.raise_for_status()

            target_id = response.json()["prompt_id"]
            print(f"🚀 Job Queued. Prompt ID: {target_id}")

            # 2. Poll the lightweight /queue endpoint every n seconds
            while True:
                await asyncio.sleep(3.0)

                queue_res = await client.get(f"{T2I_BASEURL}/queue")
                queue_res.raise_for_status()
                queue_data = queue_res.json()

                # The structure of /queue returns arrays of arrays: [ [prompt_id, ...], ... ]
                pending = [job[1] for job in queue_data.get("queue_pending", []) if len(job) > 1]
                running = [job[1] for job in queue_data.get("queue_running", []) if len(job) > 1]

                if target_id in pending:
                    print("⏳ Status: Waiting in ComfyUI queue...")
                elif target_id in running:
                    print("⚙️ Status: Active rendering on GPU...")
                else:
                    print("🏁 Generation finished! Exiting poll loop.")
                    break

            # 3. Retrieve final history data once dropped from the queue
            history_res = await client.get(f"{T2I_BASEURL}/history/{target_id}")
            history_res.raise_for_status()
            history_data = history_res.json()

        except httpx.HTTPStatusError as e:
            print(f"Server error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            print(f"Network error occurred: {e}")

        # Return the isolated history data payload for this specific execution
        if target_id in history_data:
            job_data = history_data[target_id]
        else:
            print("❌ Job cleared the queue but no history payload was found.")
            return

        outputs = job_data.get("outputs", {})
        # 1. Safely extract metadata from Node 66
        if not ("66" in outputs and "images" in outputs["66"]):
            return

        image_list = outputs["66"]["images"]

        if not image_list:
            return

        first_image = image_list[0]

        # 2. Grab the specific strings
        filename = first_image.get("filename")
        subfolder = first_image.get("subfolder", "")

        return await cls.download_comfy_image(filename, subfolder)

    @staticmethod
    async def download_comfy_image(filename: str, subfolder: str):
        # 1. Construct the precise query parameters required by ComfyUI
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": "output"
        }

        # 2. Use a dedicated client with an open read timeout for large streams
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=None)) as client:
            print(f"📥 Downloading {filename} from host server...")

            response = await client.get(f"{T2I_BASEURL}/view", params=params)
            response.raise_for_status()  # Throws exception if file doesn't exist

            return response.content

    @staticmethod
    async def unload_model():
        async with httpx.AsyncClient(timeout=T2I_TIMEOUT) as client:
            payload = {
                "unload_models": True,
                "free_memory": True
            }

            try:
                response = await client.post(f"{T2I_BASEURL}/free", json=payload)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"Server error {e.response.status_code}: {e.response.text}")
            except httpx.RequestError as e:
                print(f"Network error occurred: {e}")
            else:
                if response.status_code == 200:
                    print("Models successfully unloaded and cache cleared.")
