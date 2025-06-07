# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_ewolframalpha.py

File: `toollama/soon/tools_pending/unprocessed/dev_ewolframalpha.py`  
Language: Python  
Extracted: 2025-06-07 05:15:58  

## Snippet 1
Lines 1-12

```Python
"""
title: WolframAlpha API
author: ex0dus
author_url: https://github.com/roryeckel/open-webui-wolframalpha-tool
version: 0.2.0
"""

import os
import requests
import urllib.parse
from pydantic import BaseModel, Field
from typing import Callable, Awaitable
```

## Snippet 2
Lines 15-28

```Python
async def query_simple(
    query_string: str, app_id: str, __event_emitter__: Callable[[dict], Awaitable[None]]
) -> None:
    base_url = "http://api.wolframalpha.com/v1/simple"
    params = {"i": query_string, "appid": app_id}

    result_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    await __event_emitter__(
        {
            "type": "message",
            "data": {"content": f"![WolframAlpha Simple Result]({result_url})"},
        }
    )
```

## Snippet 3
Lines 31-53

```Python
async def query_short_answer(
    query_string: str, app_id: str, __event_emitter__: Callable[[dict], Awaitable[None]]
) -> str:
    base_url = "http://api.wolframalpha.com/v1/result"
    params = {
        "i": query_string,
        "appid": app_id,
        "format": "plaintext",
    }

    await __event_emitter__(
        {
            "data": {
                "description": f"Performing WolframAlpha short answer query: {query_string}",
                "status": "in_progress",
                "done": False,
            },
            "type": "status",
        }
    )

    try:
        response = requests.get(base_url, params=params)
```

## Snippet 4
Lines 54-67

```Python
response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        text_response = response.text

        await __event_emitter__(
            {
                "data": {
                    "description": f"WolframAlpha returned: {text_response}",
                    "status": "complete",
                    "done": True,
                },
                "type": "status",
            }
        )
        return "WolframAlpha: " + text_response
```

## Snippet 5
Lines 68-80

```Python
except Exception as e:
        print(e)
        await __event_emitter__(
            {
                "data": {
                    "description": f"Error: WolframAlpha returned {e}",
                    "status": "complete",
                    "done": True,
                },
                "type": "status",
            }
        )
        return f"There was an error fetching WolframAlpha response. You are required to report the following message to the user: {str(e)}"
```

## Snippet 6
Lines 84-90

```Python
class Valves(BaseModel):
        WOLFRAMALPHA_APP_ID: str = Field(
            default="",
            description="The App ID (api key) to authorize WolframAlpha",
        )
        ENABLE_SIMPLE_API: bool = Field(
            default=True,
```

## Snippet 7
Lines 104-116

```Python
async def perform_query(
        self, query_string: str, __event_emitter__: Callable[[dict], Awaitable[None]]
    ) -> str:
        """
        Query the WolframAlpha knowledge engine to answer a wide variety of complex mathematical formulas including trigonometry and differential equations.
        The engine also supports textual queries stated in English about other topics.
        You should cite this tool when it is used. It can also be used to supplement and back up knowledge you already know.
        WolframAlpha can be used as a last resort when the answer to a question is unclear, or when real time data is required.
        :param query_string: The question or mathematical equation to ask the WolframAlpha engine. DO NOT use backticks or markdown when writing your JSON request.
        :return: A short answer or explanation of the result of the query_string
        """
        app_id = self.valves.WOLFRAMALPHA_APP_ID or os.getenv("WOLFRAMALPHA_APP_ID")
        print(f"App ID = {app_id}")
```

## Snippet 8
Lines 117-131

```Python
if not app_id:
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Error: WolframAlpha APP_ID is not set",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
            return "You are required to report the following error message to the user: App ID is not set in the Valves or the environment variable 'WOLFRAMALPHA_APP_ID'."

        short_answer = await query_short_answer(query_string, app_id, __event_emitter__)
```

## Snippet 9
Lines 132-135

```Python
if self.valves.ENABLE_SIMPLE_API:
            await query_simple(query_string, app_id, __event_emitter__)

        return short_answer
```

