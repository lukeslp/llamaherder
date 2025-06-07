import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class FootballDataClient:
    class UserValves(BaseModel):
        """Requires FOOTBALL_DATA API Key"""
        FOOTBALL_DATA: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4/matches"

    async def fetch_matches(
        self,
        league_code: str = "PL",  # English Premier League default
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch recent football matches for a given league.

        Args:
            league_code (str): The league code (e.g., "PL" for Premier League, "SA" for Serie A).

        Returns:
            str: Formatted match results including teams, scores, and match status.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching football matches for league '{league_code}'...",
                        "done": False,
                    },
                }
            )

        headers = {"X-Auth-Token": self.api_key}
        params = {"competitions": league_code, "status": "FINISHED"}

        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            matches = response.json().get("matches", [])

            if not matches:
                return f"No matches found for league '{league_code}'."

            results = f"Recent football matches for '{league_code}':\n\n"
            for match in matches[:5]:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                score = match.get("score", {})
                full_time_score = score.get("fullTime", {})
                home_score = full_time_score.get("home", "N/A")
                away_score = full_time_score.get("away", "N/A")

                results += f"{home_team} {home_score} - {away_score} {away_team}\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching football matches: {str(e)}"
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
    api_key = "3f1bdd93fe424ac78f52173ac3bd9ea7"  # Replace with your actual Football Data API key
    football_client = FootballDataClient(api_key)
    league = "PL"  # Premier League
    import asyncio
    print(asyncio.run(football_client.fetch_matches(league)))