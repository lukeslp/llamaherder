# Code Snippets from toollama/soon/tools_pending/_openweather_api.py

File: `toollama/soon/tools_pending/_openweather_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:41  

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
        self.base_url = "https://api.openweathermap.org/data/2.5/air_pollution"
```

## Snippet 4
Lines 15-22

```Python
async def fetch_air_quality(
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
Fetch real-time air quality data for a given location.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            str: Formatted air quality report.
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
Lines 43-49

```Python
params = {"lat": lat, "lon": lon, "appid": self.api_key}

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json().get("list", [])
```

## Snippet 8
Lines 64-73

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
Lines 76-80

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
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
Lines 91-96

```Python
if __name__ == "__main__":
    api_key = "93eaf4ae2611e5c4576823656e0c82415633c077"  # Replace with your actual OpenWeather Air Quality key
    air_quality_client = OpenWeatherAirQualityClient(api_key)
    lat, lon = 37.7749, -122.4194  # Example: San Francisco
    import asyncio
    print(asyncio.run(air_quality_client.fetch_air_quality(lat, lon)))
```

