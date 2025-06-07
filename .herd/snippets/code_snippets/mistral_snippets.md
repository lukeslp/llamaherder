# Code Snippets from toollama/API/api-tools/tools/Untitled/mistral.py

File: `toollama/API/api-tools/tools/Untitled/mistral.py`  
Language: Python  
Extracted: 2025-06-07 05:20:31  

## Snippet 1
Lines 1-7

```Python
from typing import AsyncIterator, Dict, List, Optional, Union
import aiohttp
import json

from .base import BaseProvider
from ..utils.config import Config
```

## Snippet 2
Lines 11-16

```Python
def __init__(self):
        self.config = Config()
        self.api_key = self.config.get_provider_key('mistral')
        self.api_base = self.config.get_provider_endpoint('mistral')
        self.default_model = self.config.get_default_model('mistral')
```

## Snippet 3
Lines 20-47

```Python
async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        stream: bool = True,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Generate chat completions using Mistral's API."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "messages": messages,
            "stream": stream,
            "model": kwargs.get("model", self.default_model),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0)
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
```

## Snippet 4
Lines 50-52

```Python
if line:
                            try:
                                event_data = json.loads(line.decode('utf-8').split('data: ')[1])
```

## Snippet 5
Lines 53-59

```Python
if event_data.get("choices"):
                                    content = event_data["choices"][0].get("delta", {}).get("content", "")
                                    yield {
                                        "type": "delta",
                                        "content": content,
                                        "tokens": event_data.get("usage", {}).get("total_tokens", 0)
                                    }
```

## Snippet 6
Lines 62-69

```Python
else:
                    response_data = await response.json()
                    yield {
                        "type": "complete",
                        "content": response_data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "tokens": response_data.get("usage", {}).get("total_tokens", 0)
                    }
```

## Snippet 7
Lines 70-78

```Python
async def process_file(
        self,
        file_data: bytes,
        file_type: str,
        task_type: str,
        **kwargs
    ) -> AsyncIterator[Dict[str, str]]:
        """Process a file using Mistral's API."""
```

## Snippet 8
Lines 79-84

```Python
# Convert file to base64 for transmission
        import base64
        file_b64 = base64.b64encode(file_data).decode('utf-8')

        # Construct a prompt based on the task type
        prompts = {
```

## Snippet 9
Lines 85-87

```Python
"alt_text": "Generate detailed alt text for this image:",
            "analysis": "Analyze this image in detail:",
            "ocr": "Extract and format all text from this image:"
```

## Snippet 10
Lines 96-104

```Python
async for chunk in self.chat_completion(
            messages=messages,
            stream=True,
            model=kwargs.get("model", self.default_model),
            image=file_b64,
            **kwargs
        ):
            yield chunk
```

## Snippet 11
Lines 105-118

```Python
async def embeddings(
        self,
        text: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings using Mistral's API."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": kwargs.get("model", "mistral-embed"),
```

## Snippet 12
Lines 120-128

```Python
}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/v1/embeddings",
                headers=headers,
                json=data
            ) as response:
                response_data = await response.json()
```

