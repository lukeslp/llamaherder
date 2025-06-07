import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class PixabayClient:
    class UserValves(BaseModel):
        """Requires PIXABAY API Key"""
        PIXABAY: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://pixabay.com/api/"

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
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Searching images for '{query}'...",
                        "done": False,
                    },
                }
            )

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

            if not images:
                return f"No images found for '{query}'."

            results = f"Images related to '{query}':\n\n"
            for i, image in enumerate(images, 1):
                img_url = image.get("webformatURL", "No URL")
                page_url = image.get("pageURL", "No URL")
                photographer = image.get("user", "Unknown Photographer")

                results += f"{i}. Photographer: {photographer}\n"
                results += f"   Image URL: {img_url}\n"
                results += f"   Page URL: {page_url}\n\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Search completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching images: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg


# Example usage:
if __name__ == "__main__":
    api_key = "45497543-be9605f4a10e5812fff3aa61f"  # Replace with your actual Pixabay key
    pixabay_client = PixabayClient(api_key)
    query = "Artificial Intelligence"
    import asyncio
    print(asyncio.run(pixabay_client.fetch_images(query)))