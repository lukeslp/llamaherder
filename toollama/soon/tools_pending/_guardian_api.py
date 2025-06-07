import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class GuardianNewsClient:
    class UserValves(BaseModel):
        """Requires GUARDIAN API Key"""
        GUARDIAN: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://content.guardianapis.com/search"

    async def fetch_guardian_news(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch news articles from The Guardian based on a search query.

        Args:
            query (str): The search term (e.g., "AI", "Accessibility")

        Returns:
            str: Formatted list of news articles including title, date, and URL.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Searching Guardian articles for '{query}'...",
                        "done": False,
                    },
                }
            )

        params = {
            "q": query,
            "api-key": self.api_key,
            "order-by": "newest",
            "page-size": 5,  # Number of results
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            articles = response.json().get("response", {}).get("results", [])

            if not articles:
                return f"No Guardian articles found for '{query}'."

            results = f"Latest Guardian articles on '{query}':\n\n"
            for i, article in enumerate(articles, 1):
                title = article.get("webTitle", "No Title")
                pub_date = article.get("webPublicationDate", "Unknown Date")[:10]
                url = article.get("webUrl", "No URL")

                results += f"{i}. {title}\n"
                results += f"   Published: {pub_date}\n"
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
            error_msg = f"Error fetching Guardian news: {str(e)}"
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
    api_key = "d4be32d-c296-430c-b599-3d223efb7df7"  # Replace with your actual Guardian key
    guardian_client = GuardianNewsClient(api_key)
    query = "Artificial Intelligence"
    import asyncio
    print(asyncio.run(guardian_client.fetch_guardian_news(query)))