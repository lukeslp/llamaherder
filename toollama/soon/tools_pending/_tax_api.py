import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class TaxDataClient:
    class UserValves(BaseModel):
        """Requires TAX_DATA API Key"""
        TAX_DATA: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.taxdata.com/rates"

    async def fetch_tax_rates(
        self,
        country: str = "US",
        state: Optional[str] = None,
        city: Optional[str] = None,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch tax rates for a specific country, state, or city.

        Args:
            country (str): Country code (default: "US").
            state (Optional[str]): State code (if applicable).
            city (Optional[str]): City name (if applicable).

        Returns:
            str: Formatted tax rate information.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching tax rates for {city or state or country}...",
                        "done": False,
                    },
                }
            )

        params = {"api_key": self.api_key, "country": country}
        if state:
            params["state"] = state
        if city:
            params["city"] = city

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            tax_data = response.json()

            if not tax_data:
                return f"No tax data found for {city or state or country}."

            results = f"Tax Data for {city or state or country}:\n\n"
            for key, value in tax_data.items():
                results += f"  {key}: {value}%\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching tax data: {str(e)}"
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
    api_key = "PiHucpwCUfpA87dOUSWhqV0MJXQLBo89"  # Replace with your actual Tax Data key
    tax_data_client = TaxDataClient(api_key)
    country, state, city = "US", "CA", "San Francisco"
    import asyncio
    print(asyncio.run(tax_data_client.fetch_tax_rates(country, state, city)))