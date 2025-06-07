# Code Snippets from toollama/soon/tools_pending/_windy_api.py

File: `toollama/soon/tools_pending/_windy_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:48  

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
        """Requires WINDY_WEBCAMS API Key"""
        WINDY_WEBCAMS: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.windy.com/api/webcams/v2/list"
```

## Snippet 4
Lines 15-22

```Python
async def fetch_webcams(
        self,
        lat: float,
        lon: float,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 23-31

```Python
Fetch live webcams for a given location.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            str: Formatted response with webcam details and links.
        """
```

## Snippet 6
Lines 32-56

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching webcams near ({lat}, {lon})...",
                        "done": False,
                    },
                }
            )

        params = {
            "key": self.api_key,
            "lat": lat,
            "lon": lon,
            "radius": 50,  # Radius in km
            "limit": 5,
            "format": "json",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            webcams = response.json().get("result", {}).get("webcams", [])
```

## Snippet 7
Lines 57-60

```Python
if not webcams:
                return f"No webcams found near ({lat}, {lon})."

            results = f"Live Webcams near ({lat}, {lon}):\n\n"
```

## Snippet 8
Lines 61-71

```Python
for i, webcam in enumerate(webcams, 1):
                title = webcam.get("title", "No Title")
                status = webcam.get("status", "Unknown Status")
                image = webcam.get("image", {}).get("current", {}).get("preview", "No Image")
                stream = webcam.get("player", {}).get("live", {}).get("embed", "No Stream URL")

                results += f"{i}. {title}\n"
                results += f"   Status: {status}\n"
                results += f"   Image: {image}\n"
                results += f"   Stream: {stream}\n\n"
```

## Snippet 9
Lines 72-81

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
Lines 84-88

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 91-95

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 12
Lines 99-104

```Python
if __name__ == "__main__":
    api_key = "oEr5iOwUmtblbu9prTMVQBTilkIVlr2j"  # Replace with your actual Windy Webcams key
    webcams_client = WindyWebcamsClient(api_key)
    lat, lon = 37.7749, -122.4194  # Example: San Francisco
    import asyncio
    print(asyncio.run(webcams_client.fetch_webcams(lat, lon)))
```

