# Code Snippets from toollama/soon/tools_pending/_scrapestack_api.py

File: `toollama/soon/tools_pending/_scrapestack_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:36  

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
        """Requires SCRAPESTACK API Key"""
        SCRAPESTACK: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.scrapestack.com/scrape"
```

## Snippet 4
Lines 15-31

```Python
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
```

## Snippet 5
Lines 32-49

```Python
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
```

## Snippet 6
Lines 50-59

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Scraping completed", "done": True},
                    }
                )

            return f"Scraped content from {url}:\n\n{html_content[:500]}..."  # Return first 500 chars
```

## Snippet 7
Lines 62-66

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 8
Lines 69-73

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 9
Lines 77-82

```Python
if __name__ == "__main__":
    api_key = "141991d2b4d9784c24f5ec7b2ecb261a"  # Replace with your actual Scrapestack key
    scrapestack_client = ScrapestackClient(api_key)
    url = "https://lukesteuber.com"
    import asyncio
    print(asyncio.run(scrapestack_client.scrape_url(url)))
```

