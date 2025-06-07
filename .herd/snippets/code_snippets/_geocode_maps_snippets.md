# Code Snippets from toollama/soon/tools_pending/_geocode_maps.py

File: `toollama/soon/tools_pending/_geocode_maps.py`  
Language: Python  
Extracted: 2025-06-07 05:13:43  

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
        """Requires GEOCODE_MAPS API Key"""
        GEOCODE_MAPS: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.geocode.maps/api/geocode"
```

## Snippet 4
Lines 15-21

```Python
async def fetch_coordinates(
        self,
        address: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 22-29

```Python
Fetch latitude and longitude for a given address.

        Args:
            address (str): The address to geocode.

        Returns:
            str: Formatted response with latitude and longitude.
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
Lines 41-51

```Python
params = {
            "key": self.api_key,
            "q": address,
            "format": "json",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            results = response.json().get("results", [])
```

## Snippet 8
Lines 61-70

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results_str
```

## Snippet 9
Lines 73-77

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 10
Lines 80-84

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 88-93

```Python
if __name__ == "__main__":
    api_key = "66be6044be017202539979xpl8d5b6b"  # Replace with your actual Geocode Maps key
    geocode_client = GeocodeMapsClient(api_key)
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    import asyncio
    print(asyncio.run(geocode_client.fetch_coordinates(address)))
```

