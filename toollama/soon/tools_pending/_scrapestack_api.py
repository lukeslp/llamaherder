import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class ScrapestackClient:
    class UserValves(BaseModel):
        """Requires SCRAPESTACK API Key"""
        SCRAPESTACK: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.scrapestack.com/scrape"

    async def scrape_url(
        self,
        url: str,
        render_js: bool = False,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Scrape a webpage and retrieve its HTML content.

        Args:
            url (str): The webpage URL to scrape.
            render_js (bool): Whether to enable JavaScript rendering (default: False).

        Returns:
            str: Scraped HTML content.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Scraping URL: {url}...",
                        "done": False,
                    },
                }
            )

        params = {"access_key": self.api_key, "url": url, "render_js": str(render_js).lower()}

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            html_content = response.text

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Scraping completed", "done": True},
                    }
                )

            return f"Scraped content from {url}:\n\n{html_content[:500]}..."  # Return first 500 chars

        except requests.RequestException as e:
            error_msg = f"Error scraping URL: {str(e)}"
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
    api_key = "141991d2b4d9784c24f5ec7b2ecb261a"  # Replace with your actual Scrapestack key
    scrapestack_client = ScrapestackClient(api_key)
    url = "https://lukesteuber.com"
    import asyncio
    print(asyncio.run(scrapestack_client.scrape_url(url)))