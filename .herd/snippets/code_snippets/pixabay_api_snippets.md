# Code Snippets from toollama/moe/archive/old_tools/inbox/processed/pixabay_api.py

File: `toollama/moe/archive/old_tools/inbox/processed/pixabay_api.py`  
Language: Python  
Extracted: 2025-06-07 05:12:22  

## Snippet 1
Lines 1-3

```Python
import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel
```

## Snippet 2
Lines 7-10

```Python
class UserValves(BaseModel):
        """Requires PIXABAY API Key"""
        PIXABAY: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api/"
```

## Snippet 4
Lines 15-29

```Python
async def fetch_images(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch image results based on a search query.

        Args:
            query (str): The search term (e.g., "AI", "nature").

        Returns:
            str: Formatted list of image URLs.
        """
```

## Snippet 5
Lines 30-34

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
```

## Snippet 6
Lines 41-52

```Python
params = {
            "key": self.api_key,
            "q": query,
            "image_type": "photo",
            "per_page": 5,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            images = response.json().get("hits", [])
```

## Snippet 7
Lines 57-65

```Python
for i, image in enumerate(images, 1):
                img_url = image.get("webformatURL", "No URL")
                page_url = image.get("pageURL", "No URL")
                photographer = image.get("user", "Unknown Photographer")

                results += f"{i}. Photographer: {photographer}\n"
                results += f"   Image URL: {img_url}\n"
                results += f"   Page URL: {page_url}\n\n"
```

## Snippet 8
Lines 66-75

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Search completed", "done": True},
                    }
                )

            return results
```

## Snippet 9
Lines 78-82

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 10
Lines 85-89

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 93-98

```Python
if __name__ == "__main__":
    api_key = "45497543-be9605f4a10e5812fff3aa61f"  # Replace with your actual Pixabay key
    pixabay_client = PixabayClient(api_key)
    query = "Artificial Intelligence"
    import asyncio
    print(asyncio.run(pixabay_client.fetch_images(query)))
```

