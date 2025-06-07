# Code Snippets from toollama/API/api-tools/tools/data/analysis/data_analyzer.py

File: `toollama/API/api-tools/tools/data/analysis/data_analyzer.py`  
Language: Python  
Extracted: 2025-06-07 05:24:53  

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
        """Requires TISANE_PRIMARY API Key"""
        TISANE_PRIMARY: str
```

## Snippet 3
Lines 11-14

```Python
def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tisane.ai/parse"
```

## Snippet 4
Lines 15-22

```Python
async def analyze_text(
        self,
        text: str,
        language: str = "en",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 5
Lines 23-26

```Python
Analyze text for sentiment, key entities, and offensive content.

        Args:
            text (str): The input text to analyze.
```

## Snippet 6
Lines 29-31

```Python
Returns:
            str: Formatted analysis results.
        """
```

## Snippet 7
Lines 32-56

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Analyzing text with Tisane API...",
                        "done": False,
                    },
                }
            )

        headers = {"Ocp-Apim-Subscription-Key": self.api_key, "Content-Type": "application/json"}
        data = {"language": language, "content": text}

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            analysis = response.json()

            sentiment = analysis.get("sentiment", "Unknown")
            entities = analysis.get("entities", [])
            offenses = analysis.get("offenses", [])

            results = f"Text Analysis Results:\n\n"
            results += f"  Sentiment: {sentiment}\n"
```

## Snippet 8
Lines 60-69

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Analysis completed", "done": True},
                    }
                )

            return results
```

## Snippet 9
Lines 72-76

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 10
Lines 79-83

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 87-92

```Python
if __name__ == "__main__":
    api_key = "52573597091145c2befcc184c54b49ff"  # Replace with your actual Tisane API key
    tisane_client = TisaneClient(api_key)
    text = "This is a fantastic API, but it sometimes struggles with context."
    import asyncio
    print(asyncio.run(tisane_client.analyze_text(text)))
```

