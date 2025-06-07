import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class WindyWebcamsClient:
    class UserValves(BaseModel):
        """Requires WINDY_WEBCAMS API Key"""
        WINDY_WEBCAMS: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.windy.com/api/webcams/v2/list"

    async def fetch_webcams(
        self,
        lat: float,
        lon: float,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch live webcams for a given location.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            str: Formatted response with webcam details and links.
        """
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

            if not webcams:
                return f"No webcams found near ({lat}, {lon})."

            results = f"Live Webcams near ({lat}, {lon}):\n\n"
            for i, webcam in enumerate(webcams, 1):
                title = webcam.get("title", "No Title")
                status = webcam.get("status", "Unknown Status")
                image = webcam.get("image", {}).get("current", {}).get("preview", "No Image")
                stream = webcam.get("player", {}).get("live", {}).get("embed", "No Stream URL")

                results += f"{i}. {title}\n"
                results += f"   Status: {status}\n"
                results += f"   Image: {image}\n"
                results += f"   Stream: {stream}\n\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching webcams: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg


# Example usage:
if __name__ == "__main__":
    api_key = "oEr5iOwUmtblbu9prTMVQBTilkIVlr2j"  # Replace with your actual Windy Webcams key
    webcams_client = WindyWebcamsClient(api_key)
    lat, lon = 37.7749, -122.4194  # Example: San Francisco
    import asyncio
    print(asyncio.run(webcams_client.fetch_webcams(lat, lon)))