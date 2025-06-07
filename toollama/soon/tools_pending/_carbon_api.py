import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class CarbonMarketplaceClient:
    class UserValves(BaseModel):
        """Requires CARBON_MARKETPLACE API Key"""
        CARBON_MARKETPLACE: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.carbonmarketplace.com/offsets"

    async def fetch_carbon_credits(
        self,
        region: str = "global",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch available carbon credits for purchase.

        Args:
            region (str): Region for carbon credits (e.g., "US", "EU", "global").

        Returns:
            str: List of available carbon credit programs and pricing.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching carbon credits for region '{region}'...",
                        "done": False,
                    },
                }
            )

        params = {"region": region, "api_key": self.api_key}

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            credits = response.json().get("credits", [])

            if not credits:
                return f"No carbon credit programs found for region '{region}'."

            results = f"Available Carbon Credits in '{region}':\n\n"
            for i, credit in enumerate(credits, 1):
                project = credit.get("project", "Unknown Project")
                price = credit.get("price", "N/A")
                description = credit.get("description", "No description available")
                url = credit.get("url", "No URL")

                results += f"{i}. {project}\n"
                results += f"   Price: {price} per ton\n"
                results += f"   Description: {description}\n"
                results += f"   More info: {url}\n\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching carbon credits: {str(e)}"
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
    api_key = "VNfO2257BW0K4zEkCnKKdg"  # Replace with your actual Carbon Marketplace key
    carbon_client = CarbonMarketplaceClient(api_key)
    region = "global"
    import asyncio
    print(asyncio.run(carbon_client.fetch_carbon_credits(region)))