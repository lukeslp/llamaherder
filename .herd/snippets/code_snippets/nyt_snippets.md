# Code Snippets from toollama/API/api-tools/tools/search/nyt.py

File: `toollama/API/api-tools/tools/search/nyt.py`  
Language: Python  
Extracted: 2025-06-07 05:19:33  

## Snippet 1
Lines 1-6

```Python
"""New York Times API tool for the MoE system."""

import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from ..base import BaseTool
```

## Snippet 2
Lines 10-13

```Python
class UserValves(BaseTool.UserValves):
        """Requires NYT API Key"""
        NYT: str
```

## Snippet 3
Lines 14-18

```Python
def __init__(self, credentials: Dict[str, str]):
        super().__init__(credentials)
        self.api_key = credentials['NYT']
        self.base_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
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
Search for NYT articles.

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
Lines 41-54

```Python
)

        params = {
            "q": query,
            "api-key": self.api_key,
            "sort": "newest",
            "page": 0,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            articles = response.json().get("response", {}).get("docs", [])
```

## Snippet 8
Lines 55-57

```Python
if not articles:
                await self.emit_event(
                    "status",
```

## Snippet 9
Lines 65-82

```Python
for i, article in enumerate(articles[:5], 1):
                title = article.get("headline", {}).get("main", "No Title")
                pub_date = article.get("pub_date", "Unknown Date")[:10]
                url = article.get("web_url", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Published: {pub_date}\n"
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
Lines 83-100

```Python
except requests.RequestException as e:
            error_msg = f"Error fetching NYT news: {str(e)}"
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

