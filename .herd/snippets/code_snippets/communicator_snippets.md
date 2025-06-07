# Code Snippets from toollama/moe/core/communicator.py

File: `toollama/moe/core/communicator.py`  
Language: Python  
Extracted: 2025-06-07 05:11:45  

## Snippet 1
Lines 2-12

```Python
Model communication system for interacting with model endpoints.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 20-34

```Python
def __init__(self, config: Dict[str, Any]):
        """
        Initialize the communicator.

        Args:
            config: Configuration dictionary containing model endpoints
        """
        self.endpoints = config.get('model_endpoints', {})
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        self.retries = 3
        self.retry_delay = 1.0  # seconds
```

## Snippet 3
Lines 35-54

```Python
async def send_message(
        self,
        model_id: str,
        message: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a model endpoint.

        Args:
            model_id: Model identifier
            message: Message to send
            timeout: Optional request timeout

        Returns:
            Model response

        Raises:
            CommunicationError: If communication fails
        """
```

## Snippet 4
Lines 61-73

```Python
for attempt in range(self.retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        endpoint,
                        json=message,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                    return response.json()

            except httpx.HTTPError as e:
                logger.warning(
```

## Snippet 5
Lines 79-85

```Python
except Exception as e:
                logger.error(f"Error communicating with {model_id}: {e}")
                raise CommunicationError(f"Error communicating with {model_id}: {e}")

            # Wait before retrying
            await asyncio.sleep(self.retry_delay * (2 ** attempt))
```

## Snippet 6
Lines 86-89

```Python
async def close(self) -> None:
        """Close the communicator and cleanup resources"""
        await self.client.aclose()
```

## Snippet 7
Lines 92-102

```Python
Get endpoint URL for a model.

        Args:
            model_id: Model identifier

        Returns:
            Endpoint URL

        Raises:
            CommunicationError: If no endpoint configured
        """
```

## Snippet 8
Lines 107-115

```Python
def add_endpoint(self, model_id: str, endpoint: str) -> None:
        """
        Add a new model endpoint.

        Args:
            model_id: Model identifier
            endpoint: Endpoint URL
        """
        self.endpoints[model_id] = endpoint
```

## Snippet 9
Lines 118-124

```Python
def remove_endpoint(self, model_id: str) -> None:
        """
        Remove a model endpoint.

        Args:
            model_id: Model identifier
        """
```

## Snippet 10
Lines 129-136

```Python
def update_endpoint(self, model_id: str, endpoint: str) -> None:
        """
        Update an existing model endpoint.

        Args:
            model_id: Model identifier
            endpoint: New endpoint URL
        """
```

