# Code Snippets from toollama/soon/tools_pending/_football_api.py

File: `toollama/soon/tools_pending/_football_api.py`  
Language: Python  
Extracted: 2025-06-07 05:13:53  

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
        """Requires FOOTBALL_DATA API Key"""
        FOOTBALL_DATA: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4/matches"
```

## Snippet 4
Lines 15-21

```Python
async def fetch_matches(
        self,
        league_code: str = "PL",  # English Premier League default
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 27-29

```Python
Returns:
            str: Formatted match results including teams, scores, and match status.
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
Lines 41-48

```Python
headers = {"X-Auth-Token": self.api_key}
        params = {"competitions": league_code, "status": "FINISHED"}

        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            matches = response.json().get("matches", [])
```

## Snippet 8
Lines 53-60

```Python
for match in matches[:5]:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                score = match.get("score", {})
                full_time_score = score.get("fullTime", {})
                home_score = full_time_score.get("home", "N/A")
                away_score = full_time_score.get("away", "N/A")
```

## Snippet 9
Lines 63-72

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

## Snippet 10
Lines 75-79

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 82-86

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 12
Lines 90-95

```Python
if __name__ == "__main__":
    api_key = "3f1bdd93fe424ac78f52173ac3bd9ea7"  # Replace with your actual Football Data API key
    football_client = FootballDataClient(api_key)
    league = "PL"  # Premier League
    import asyncio
    print(asyncio.run(football_client.fetch_matches(league)))
```

