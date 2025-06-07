# Code Snippets from toollama/API/api-tools/tools/property/environment/airquality_api.py

File: `toollama/API/api-tools/tools/property/environment/airquality_api.py`  
Language: Python  
Extracted: 2025-06-07 05:24:48  

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
        """Requires AIR_QUALITY_OPEN_DATA API Key"""
        AIR_QUALITY_OPEN_DATA: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.waqi.info/feed"
```

## Snippet 4
Lines 15-21

```Python
async def fetch_air_quality(
        self,
        city: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 22-29

```Python
Fetch air quality data for a given city.

        Args:
            city (str): The city to fetch air quality data for.

        Returns:
            str: Formatted air quality report.
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
url = f"{self.base_url}/{city}/?token={self.api_key}"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
```

## Snippet 8
Lines 60-69

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

## Snippet 9
Lines 72-76

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 10
Lines 79-83

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 87-92

```Python
if __name__ == "__main__":
    api_key = "93eaf4ae2611e5c4576823656e0c82415633c077"  # Replace with your actual Air Quality key
    air_quality_client = AirQualityClient(api_key)
    city = "San Francisco"
    import asyncio
    print(asyncio.run(air_quality_client.fetch_air_quality(city)))
```

