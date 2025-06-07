import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class OpenStatesClient:
    class UserValves(BaseModel):
        """Requires OPENSTATES API Key"""
        OPENSTATES: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://v3.openstates.org/bills"

    async def fetch_legislation(
        self,
        query: str,
        state: str = "US",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch recent legislative bills related to a search query.

        Args:
            query (str): The search term (e.g., "education", "healthcare").
            state (str): State code (default: "US" for federal).

        Returns:
            str: Formatted list of legislative bills including title, state, session, and URL.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Searching OpenStates for '{query}'...",
                        "done": False,
                    },
                }
            )

        params = {
            "q": query,
            "jurisdiction": state,
            "sort": "latest",
            "per_page": 5,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            bills = response.json().get("results", [])

            if not bills:
                return f"No legislative bills found for '{query}' in {state}."

            results = f"Recent legislative bills on '{query}' in {state}:\n\n"
            for i, bill in enumerate(bills, 1):
                title = bill.get("title", "No Title")
                session = bill.get("session", "Unknown Session")
                state_name = bill.get("jurisdiction", {}).get("name", "Unknown State")
                url = bill.get("openstates_url", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Session: {session}\n"
                results += f"   State: {state_name}\n"
                results += f"   URL: {url}\n\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Search completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching legislation: {str(e)}"
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
    api_key = "083f77a7-3f7a-49bf-ac44-d92047b7902a"  # Replace with your actual OpenStates key
    openstates_client = OpenStatesClient(api_key)
    query = "Artificial Intelligence"
    import asyncio
    print(asyncio.run(openstates_client.fetch_legislation(query)))