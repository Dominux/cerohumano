from typing import Iterable
import uuid

import httpx


BASE_URL = f'http://cerohumano_server:8000'


class ServerClient:
    async def upload_post(
        self,
        author_id: uuid.UUID,
        caption: str,
        files: 'Iterable[bytes]',
    ):
        url = f"{BASE_URL}/posts"

        multipart_files = []

        for i, file in enumerate(files):
            # Form field key name must exactly match the list variable name in your router ("files")
            multipart_files.append(("files", (f"image_{i}.png", file, "image/png")))

        form_data = {
            "author_id": str(author_id),
            "caption": caption,
        }

        async with httpx.AsyncClient() as client:
            # Pass the formatted list of tuples to the files parameter
            response = await client.post(url, data=form_data, files=multipart_files)
            response.raise_for_status()
            return response
