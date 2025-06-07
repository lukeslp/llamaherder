import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class OpenWeatherAirQualityClient:
    class UserValves(BaseModel):
        """Requires AIR_QUALITY_OPEN_DATA API Key"""
        AIR_QUALITY_OPEN_DATA: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/air_pollution"

    async def fetch_air_quality(
        self,
        lat: float,
        lon: float,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch real-time air quality data for a given location.

        Args:
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            str: Formatted air quality report.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching air quality for ({lat}, {lon})...",
                        "done": False,
                    },
                }
            )

        params = {"lat": lat, "lon": lon, "appid": self.api_key}

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json().get("list", [])

            if not data:
                return f"No air quality data found for ({lat}, {lon})."

            aqi = data[0]["main"]["aqi"]
            components = data[0]["components"]

            results = f"Air Quality for ({lat}, {lon}):\n\n"
            results += f"  AQI (Air Quality Index): {aqi}\n"
            results += f"  PM2.5: {components['pm2_5']} µg/m³\n"
            results += f"  PM10: {components['pm10']} µg/m³\n"
            results += f"  CO: {components['co']} µg/m³\n"
            results += f"  NO2: {components['no2']} µg/m³\n"
            results += f"  SO2: {components['so2']} µg/m³\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching air quality data: {str(e)}"
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
    api_key = "93eaf4ae2611e5c4576823656e0c82415633c077"  # Replace with your actual OpenWeather Air Quality key
    air_quality_client = OpenWeatherAirQualityClient(api_key)
    lat, lon = 37.7749, -122.4194  # Example: San Francisco
    import asyncio
    print(asyncio.run(air_quality_client.fetch_air_quality(lat, lon)))