import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class GeocodeMapsClient:
    class UserValves(BaseModel):
        """Requires GEOCODE_MAPS API Key"""
        GEOCODE_MAPS: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.geocode.maps/api/geocode"

    async def fetch_coordinates(
        self,
        address: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch latitude and longitude for a given address.

        Args:
            address (str): The address to geocode.

        Returns:
            str: Formatted response with latitude and longitude.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching coordinates for '{address}'...",
                        "done": False,
                    },
                }
            )

        params = {
            "key": self.api_key,
            "q": address,
            "format": "json",
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            results = response.json().get("results", [])

            if not results:
                return f"Could not retrieve coordinates for '{address}'."

            lat, lon = results[0]["geometry"]["lat"], results[0]["geometry"]["lng"]

            results_str = f"Coordinates for '{address}':\n\n"
            results_str += f"  Latitude: {lat}\n"
            results_str += f"  Longitude: {lon}\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results_str

        except requests.RequestException as e:
            error_msg = f"Error fetching coordinates: {str(e)}"
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
    api_key = "66be6044be017202539979xpl8d5b6b"  # Replace with your actual Geocode Maps key
    geocode_client = GeocodeMapsClient(api_key)
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    import asyncio
    print(asyncio.run(geocode_client.fetch_coordinates(address)))