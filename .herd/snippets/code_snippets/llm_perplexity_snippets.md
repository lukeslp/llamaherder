# Code Snippets from toollama/API/api-tools/tools/llm/perplexity/llm_perplexity.py

File: `toollama/API/api-tools/tools/llm/perplexity/llm_perplexity.py`  
Language: Python  
Extracted: 2025-06-07 05:20:43  

## Snippet 1
Lines 2-15

```Python
Perplexity LLM tool for the MoE system.
Provides access to Perplexity's language models.
"""

import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from ...base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 21-25

```Python
def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity tool.

        Args:
```

## Snippet 3
Lines 30-37

```Python
if not self.api_key:
            raise ValueError("Perplexity API key must be provided")

        self.client = httpx.AsyncClient(
            base_url=self.API_URL,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
```

## Snippet 4
Lines 38-60

```Python
async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request to Perplexity's API.

        Args:
            parameters: Dictionary containing:
                - messages: List of message dictionaries with 'role' and 'content'
                - model: Model to use (e.g., 'pplx-7b-chat', 'pplx-70b-chat')
                - temperature: Sampling temperature
                - max_tokens: Maximum tokens to generate
                - top_p: Top-p sampling parameter
                - top_k: Top-k sampling parameter
                - presence_penalty: Presence penalty parameter
                - frequency_penalty: Frequency penalty parameter
                - task: Task type ('chat', 'completion')

        Returns:
            Dictionary containing the API response
        """
        try:
            # Emit start event
            await self.emit_status_event(
                "status",
```

## Snippet 5
Lines 68-75

```Python
elif task == "completion":
                response = await self._completion(parameters)
            else:
                raise ValueError(f"Unknown task type: {task}")

            # Emit completion event
            await self.emit_status_event(
                "status",
```

## Snippet 6
Lines 77-80

```Python
)

            return response
```

## Snippet 7
Lines 81-88

```Python
except Exception as e:
            logger.error(f"Error executing Perplexity task: {str(e)}")
            await self.emit_status_event(
                "error",
                {"message": f"Perplexity task failed: {str(e)}"}
            )
            raise
```

## Snippet 8
Lines 89-115

```Python
async def _chat(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chat completion tasks"""
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": parameters.get("model", "pplx-7b-chat"),
                "messages": parameters["messages"],
                "temperature": parameters.get("temperature", 0.7),
                "max_tokens": parameters.get("max_tokens", None),
                "top_p": parameters.get("top_p", 1.0),
                "top_k": parameters.get("top_k", None),
                "presence_penalty": parameters.get("presence_penalty", 0.0),
                "frequency_penalty": parameters.get("frequency_penalty", 0.0)
            }
        )
        response.raise_for_status()
        data = response.json()

        return {
            "message": {
                "role": data["choices"][0]["message"]["role"],
                "content": data["choices"][0]["message"]["content"]
            },
            "usage": data["usage"],
            "finish_reason": data["choices"][0]["finish_reason"]
        }
```

## Snippet 9
Lines 116-139

```Python
async def _completion(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text completion tasks"""
        response = await self.client.post(
            "/completions",
            json={
                "model": parameters.get("model", "pplx-7b-chat"),
                "prompt": parameters["prompt"],
                "temperature": parameters.get("temperature", 0.7),
                "max_tokens": parameters.get("max_tokens", None),
                "top_p": parameters.get("top_p", 1.0),
                "top_k": parameters.get("top_k", None),
                "presence_penalty": parameters.get("presence_penalty", 0.0),
                "frequency_penalty": parameters.get("frequency_penalty", 0.0)
            }
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["text"],
            "usage": data["usage"],
            "finish_reason": data["choices"][0]["finish_reason"]
        }
```

## Snippet 10
Lines 140-142

```Python
async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
```

