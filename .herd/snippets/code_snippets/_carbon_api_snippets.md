# Code Snippets from toollama/soon/tools_pending/_carbon_api.py

File: `toollama/soon/tools_pending/_carbon_api.py`  
Language: Python  
Extracted: 2025-06-07 05:14:35  

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
        """Requires CARBON_MARKETPLACE API Key"""
        CARBON_MARKETPLACE: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.carbonmarketplace.com/offsets"
```

## Snippet 4
Lines 15-21

```Python
async def fetch_carbon_credits(
        self,
        region: str = "global",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 27-29

```Python
Returns:
            str: List of available carbon credit programs and pricing.
        """
```

## Snippet 6
Lines 30-34

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
```

## Snippet 7
Lines 41-47

```Python
params = {"region": region, "api_key": self.api_key}

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            credits = response.json().get("credits", [])
```

## Snippet 8
Lines 52-58

```Python
for i, credit in enumerate(credits, 1):
                project = credit.get("project", "Unknown Project")
                price = credit.get("price", "N/A")
                description = credit.get("description", "No description available")
                url = credit.get("url", "No URL")

                results += f"{i}. {project}\n"
```

## Snippet 9
Lines 63-72

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results
```

## Snippet 10
Lines 75-79

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 82-86

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 12
Lines 90-95

```Python
if __name__ == "__main__":
    api_key = "VNfO2257BW0K4zEkCnKKdg"  # Replace with your actual Carbon Marketplace key
    carbon_client = CarbonMarketplaceClient(api_key)
    region = "global"
    import asyncio
    print(asyncio.run(carbon_client.fetch_carbon_credits(region)))
```

