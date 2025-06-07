# Code Snippets from toollama/soon/tools_pending/_guardian_api.py

File: `toollama/soon/tools_pending/_guardian_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:56  

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
        """Requires GUARDIAN API Key"""
        GUARDIAN: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://content.guardianapis.com/search"
```

## Snippet 4
Lines 15-29

```Python
async def fetch_guardian_news(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch news articles from The Guardian based on a search query.

        Args:
            query (str): The search term (e.g., "AI", "Accessibility")

        Returns:
            str: Formatted list of news articles including title, date, and URL.
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
            "q": query,
            "api-key": self.api_key,
            "order-by": "newest",
            "page-size": 5,  # Number of results
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            articles = response.json().get("response", {}).get("results", [])
```

## Snippet 7
Lines 57-65

```Python
for i, article in enumerate(articles, 1):
                title = article.get("webTitle", "No Title")
                pub_date = article.get("webPublicationDate", "Unknown Date")[:10]
                url = article.get("webUrl", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Published: {pub_date}\n"
                results += f"   URL: {url}\n\n"
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
    api_key = "d4be32d-c296-430c-b599-3d223efb7df7"  # Replace with your actual Guardian key
    guardian_client = GuardianNewsClient(api_key)
    query = "Artificial Intelligence"
    import asyncio
    print(asyncio.run(guardian_client.fetch_guardian_news(query)))
```

