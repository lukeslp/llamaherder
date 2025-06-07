# Code Snippets from toollama/API/api-tools/tools/llm/cohere/llm_cohere.py

File: `toollama/API/api-tools/tools/llm/cohere/llm_cohere.py`  
Language: Python  
Extracted: 2025-06-07 05:20:48  

## Snippet 1
Lines 2-15

```Python
Cohere LLM tool for the MoE system.
Provides access to Cohere's language models.
"""

import os
import logging
import cohere
from typing import Dict, Any, Optional, List
from ...base import BaseTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 19-23

```Python
def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Cohere tool.

        Args:
```

## Snippet 3
Lines 28-32

```Python
if not self.api_key:
            raise ValueError("Cohere API key must be provided")

        self.client = cohere.Client(self.api_key)
```

## Snippet 4
Lines 33-38

```Python
async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request to Cohere's API.

        Args:
            parameters: Dictionary containing:
```

## Snippet 5
Lines 39-50

```Python
- prompt: Text prompt for generation/completion
                - model: Model to use (e.g., 'command', 'command-light')
                - max_tokens: Maximum tokens to generate
                - temperature: Sampling temperature
                - k: Top-k sampling parameter
                - p: Top-p sampling parameter
                - frequency_penalty: Frequency penalty parameter
                - presence_penalty: Presence penalty parameter
                - stop_sequences: List of sequences to stop generation
                - return_likelihoods: Whether to return token likelihoods
                - task: Task type ('generate', 'embed', 'classify', etc.)
```

## Snippet 6
Lines 51-57

```Python
Returns:
            Dictionary containing the API response
        """
        try:
            # Emit start event
            await self.emit_status_event(
                "status",
```

## Snippet 7
Lines 69-76

```Python
elif task == "summarize":
                response = await self._summarize(parameters)
            else:
                raise ValueError(f"Unknown task type: {task}")

            # Emit completion event
            await self.emit_status_event(
                "status",
```

## Snippet 8
Lines 78-81

```Python
)

            return response
```

## Snippet 9
Lines 82-89

```Python
except Exception as e:
            logger.error(f"Error executing Cohere task: {str(e)}")
            await self.emit_status_event(
                "error",
                {"message": f"Cohere task failed: {str(e)}"}
            )
            raise
```

## Snippet 10
Lines 90-110

```Python
async def _generate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text generation tasks"""
        response = self.client.generate(
            prompt=parameters["prompt"],
            model=parameters.get("model", "command"),
            max_tokens=parameters.get("max_tokens", 256),
            temperature=parameters.get("temperature", 0.7),
            k=parameters.get("k", 0),
            p=parameters.get("p", 0.75),
            frequency_penalty=parameters.get("frequency_penalty", 0.0),
            presence_penalty=parameters.get("presence_penalty", 0.0),
            stop_sequences=parameters.get("stop_sequences", []),
            return_likelihoods=parameters.get("return_likelihoods", None)
        )

        return {
            "text": response.generations[0].text,
            "finish_reason": response.generations[0].finish_reason,
            "tokens": response.generations[0].token_count
        }
```

## Snippet 11
Lines 111-123

```Python
async def _embed(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text embedding tasks"""
        response = self.client.embed(
            texts=parameters["texts"],
            model=parameters.get("model", "embed-english-v3.0"),
            truncate=parameters.get("truncate", None)
        )

        return {
            "embeddings": response.embeddings,
            "meta": response.meta
        }
```

## Snippet 12
Lines 124-140

```Python
async def _classify(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text classification tasks"""
        response = self.client.classify(
            inputs=parameters["inputs"],
            examples=parameters["examples"],
            model=parameters.get("model", "embed-english-v3.0"),
            preset=parameters.get("preset", None),
            truncate=parameters.get("truncate", None)
        )

        return {
            "classifications": [
                {
                    "prediction": c.prediction,
                    "confidence": c.confidence,
                    "labels": c.labels
                }
```

## Snippet 13
Lines 145-159

```Python
async def _summarize(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle text summarization tasks"""
        response = self.client.summarize(
            text=parameters["text"],
            model=parameters.get("model", "command"),
            length=parameters.get("length", "medium"),
            format=parameters.get("format", "paragraph"),
            extractiveness=parameters.get("extractiveness", "medium"),
            temperature=parameters.get("temperature", 0.3)
        )

        return {
            "summary": response.summary,
            "meta": response.meta
        }
```

