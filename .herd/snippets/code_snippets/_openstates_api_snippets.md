# Code Snippets from toollama/soon/tools_pending/_openstates_api.py

File: `toollama/soon/tools_pending/_openstates_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:59  

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
        """Requires OPENSTATES API Key"""
        OPENSTATES: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.openstates.org/bills"
```

## Snippet 4
Lines 15-26

```Python
async def fetch_legislation(
        self,
        query: str,
        state: str = "US",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch recent legislative bills related to a search query.

        Args:
            query (str): The search term (e.g., "education", "healthcare").
```

## Snippet 5
Lines 29-31

```Python
Returns:
            str: Formatted list of legislative bills including title, state, session, and URL.
        """
```

## Snippet 6
Lines 32-36

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
```

## Snippet 7
Lines 43-55

```Python
params = {
            "q": query,
            "jurisdiction": state,
            "sort": "latest",
            "per_page": 5,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            bills = response.json().get("results", [])
```

## Snippet 8
Lines 60-70

```Python
for i, bill in enumerate(bills, 1):
                title = bill.get("title", "No Title")
                session = bill.get("session", "Unknown Session")
                state_name = bill.get("jurisdiction", {}).get("name", "Unknown State")
                url = bill.get("openstates_url", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Session: {session}\n"
                results += f"   State: {state_name}\n"
                results += f"   URL: {url}\n\n"
```

## Snippet 9
Lines 71-80

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

## Snippet 10
Lines 83-87

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 90-94

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 12
Lines 98-103

```Python
if __name__ == "__main__":
    api_key = "083f77a7-3f7a-49bf-ac44-d92047b7902a"  # Replace with your actual OpenStates key
    openstates_client = OpenStatesClient(api_key)
    query = "Artificial Intelligence"
    import asyncio
    print(asyncio.run(openstates_client.fetch_legislation(query)))
```

