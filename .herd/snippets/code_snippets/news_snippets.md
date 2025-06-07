# Code Snippets from toollama/API/api-tools/tools/search/news.py

File: `toollama/API/api-tools/tools/search/news.py`  
Language: Python  
Extracted: 2025-06-07 05:19:28  

## Snippet 1
Lines 1-6

```Python
"""News API tool for the MoE system."""

import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from ..base import BaseTool
```

## Snippet 2
Lines 10-13

```Python
class UserValves(BaseTool.UserValves):
        """Requires NEWSAPI key"""
        NEWSAPI: str
```

## Snippet 3
Lines 14-18

```Python
def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.api_key = credentials['NEWSAPI']
        self.base_url = "https://newsapi.org/v2/everything"
```

## Snippet 4
Lines 19-25

```Python
async def execute(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
```

## Snippet 5
Lines 26-30

```Python
Search for news articles.

        Args:
            query: Search query
            __user__: User context
```

## Snippet 6
Lines 33-37

```Python
Returns:
            Formatted article results
        """
        await self.emit_event(
            "status",
```

## Snippet 7
Lines 41-55

```Python
)

        params = {
            "q": query,
            "apiKey": self.api_key,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 5
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            articles = response.json().get("articles", [])
```

## Snippet 8
Lines 56-58

```Python
if not articles:
                await self.emit_event(
                    "status",
```

## Snippet 9
Lines 66-85

```Python
for i, article in enumerate(articles, 1):
                title = article.get("title", "No Title")
                source = article["source"].get("name", "Unknown Source")
                published = article.get("publishedAt", "Unknown Date")[:10]
                url = article.get("url", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Source: {source}\n"
                results += f"   Published: {published}\n"
                results += f"   URL: {url}\n\n"

            await self.emit_event(
                "status",
                "Search completed",
                True,
                __event_emitter__
            )

            return results
```

## Snippet 10
Lines 86-103

```Python
except requests.RequestException as e:
            error_msg = f"Error fetching news: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg
```

