# Code Snippets from toollama/moe/tools/knowledge/research/knowledge_dictionary.py

File: `toollama/moe/tools/knowledge/research/knowledge_dictionary.py`  
Language: Python  
Extracted: 2025-06-07 05:13:29  

## Snippet 1
Lines 1-3

```Python
import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel
```

## Snippet 2
Lines 7-11

```Python
class UserValves(BaseModel):
        """Requires MIRRIAM_WEBSTER_LEARNERS or MIRRIAM_WEBSTER_MEDICAL API Key"""
        MIRRIAM_WEBSTER_LEARNERS: str
        MIRRIAM_WEBSTER_MEDICAL: str
```

## Snippet 3
Lines 12-16

```Python
def __init__(self, learners_key: str, medical_key: str):
        self.learners_key = learners_key
        self.medical_key = medical_key
        self.base_url = "https://www.dictionaryapi.com/api/v3/references/"
```

## Snippet 4
Lines 17-33

```Python
async def fetch_definition(
        self,
        word: str,
        dictionary_type: str = "learners",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch word definitions from Merriam-Webster Dictionary API.

        Args:
            word (str): The word to look up.
            dictionary_type (str): The type of dictionary ("learners" or "medical").

        Returns:
            str: Formatted dictionary entry.
        """
```

## Snippet 5
Lines 34-42

```Python
if dictionary_type == "medical":
            api_key = self.medical_key
            endpoint = "medical/json/"
        else:
            api_key = self.learners_key
            endpoint = "learners/json/"

        url = f"{self.base_url}{endpoint}{word}?key={api_key}"
```

## Snippet 6
Lines 43-47

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
```

## Snippet 7
Lines 54-58

```Python
try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            definitions = response.json()
```

## Snippet 8
Lines 70-79

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

## Snippet 9
Lines 82-86

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 10
Lines 89-93

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 97-103

```Python
if __name__ == "__main__":
    learners_key = "d035a35e-5b52-41ea-8823-47002751436b"  # Replace with your actual Learners Dictionary key
    medical_key = "a1ab4851-ebc1-4521-b6e6-5d0465aeec09"  # Replace with your actual Medical Dictionary key
    dictionary_client = MerriamWebsterClient(learners_key, medical_key)
    word = "artificial"
    import asyncio
    print(asyncio.run(dictionary_client.fetch_definition(word)))
```

