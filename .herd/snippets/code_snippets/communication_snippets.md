# Code Snippets from toollama/moe/core/communication.py

File: `toollama/moe/core/communication.py`  
Language: Python  
Extracted: 2025-06-07 05:11:47  

## Snippet 1
Lines 2-17

```Python
Communication layer for the MoE system.
Handles message passing between different models and components.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field
import asyncio
import json
import httpx
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 19-25

```Python
"""Base class for model communication"""
    model_id: str = Field(..., description="Unique identifier of the model")
    message_type: str = Field(..., description="Type of message (e.g., task, query, response)")
    content: Dict[str, Any] = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
```

## Snippet 3
Lines 26-34

```Python
class ModelResponse(BaseModel):
    """Standardized model response"""
    model_id: str = Field(..., description="ID of the responding model")
    response_type: str = Field(..., description="Type of response")
    content: Dict[str, Any] = Field(..., description="Response content")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
```

## Snippet 4
Lines 39-42

```Python
class ModelTimeoutError(ModelError):
    """Raised when model communication times out"""
    pass
```

## Snippet 5
Lines 43-46

```Python
class ModelNotFoundError(ModelError):
    """Raised when target model is not found"""
    pass
```

## Snippet 6
Lines 50-69

```Python
def __init__(self, config: Dict[str, Any]):
        """
        Initialize the communicator.

        Args:
            config: Configuration dictionary containing:
                - model_endpoints: Dict[str, str] - Model endpoints
                - timeouts: Dict[str, int] - Model timeouts
                - retry_config: Dict[str, Any] - Retry configuration
        """
        self.config = config
        self.active_models: Dict[str, Dict[str, Any]] = {}
        self.message_queue = asyncio.Queue()
        self.retry_config = config.get('retry_config', {
            'max_retries': 3,
            'backoff_factor': 1.5,
            'max_backoff': 30
        })

        # Initialize active models
```

## Snippet 7
Lines 70-76

```Python
for model_id, endpoint in config.get('model_endpoints', {}).items():
            self.active_models[model_id] = {
                'endpoint': endpoint,
                'timeout': config.get('timeouts', {}).get(model_id, 30),
                'status': 'ready'
            }
```

## Snippet 8
Lines 77-98

```Python
async def send_message(
        self,
        target_model: str,
        message: Union[ModelMessage, Dict[str, Any]],
        timeout: Optional[int] = None
    ) -> ModelResponse:
        """
        Send message to target model.

        Args:
            target_model: ID of the target model
            message: Message to send
            timeout: Optional timeout override

        Returns:
            ModelResponse object

        Raises:
            ModelNotFoundError: If target model not found
            ModelTimeoutError: If request times out
            ModelError: For other errors
        """
```

## Snippet 9
Lines 103-124

```Python
if isinstance(message, dict):
            message = ModelMessage(
                model_id=target_model,
                **message
            )

        # Add to queue
        await self.message_queue.put({
            'target': target_model,
            'message': message
        })

        try:
            # Process message with retries
            response = await self._process_message_with_retry(
                target_model,
                message,
                timeout or self.active_models[target_model]['timeout']
            )
            return ModelResponse(**response)

        except asyncio.TimeoutError:
```

## Snippet 10
Lines 129-146

```Python
async def broadcast_message(
        self,
        message: Union[ModelMessage, Dict[str, Any]],
        targets: List[str],
        timeout: Optional[int] = None
    ) -> List[ModelResponse]:
        """
        Send message to multiple models.

        Args:
            message: Message to broadcast
            targets: List of target model IDs
            timeout: Optional timeout override

        Returns:
            List of ModelResponse objects
        """
        tasks = []
```

## Snippet 11
Lines 162-171

```Python
async def _process_message_with_retry(
        self,
        target: str,
        message: ModelMessage,
        timeout: int
    ) -> Dict[str, Any]:
        """Process message with exponential backoff retry"""
        retries = 0
        last_error = None
```

## Snippet 12
Lines 172-177

```Python
while retries < self.retry_config['max_retries']:
            try:
                return await self._process_message(target, message, timeout)
            except Exception as e:
                last_error = e
                retries += 1
```

## Snippet 13
Lines 178-184

```Python
if retries < self.retry_config['max_retries']:
                    # Calculate backoff
                    backoff = min(
                        self.retry_config['backoff_factor'] * (2 ** (retries - 1)),
                        self.retry_config['max_backoff']
                    )
                    logger.warning(
```

## Snippet 14
Lines 191-226

```Python
async def _process_message(
        self,
        target: str,
        message: ModelMessage,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Process individual message.

        Args:
            target: Target model ID
            message: Message to send
            timeout: Request timeout

        Returns:
            Response dictionary
        """
        model_config = self.active_models[target]

        async with httpx.AsyncClient() as client:
            start_time = datetime.utcnow()

            response = await client.post(
                model_config['endpoint'],
                json=message.dict(),
                timeout=timeout
            )
            response.raise_for_status()

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            result = response.json()
            result['execution_time'] = execution_time

            return result
```

## Snippet 15
Lines 232-238

```Python
return {
            'model_id': model_id,
            'status': self.active_models[model_id]['status'],
            'endpoint': self.active_models[model_id]['endpoint'],
            'timeout': self.active_models[model_id]['timeout']
        }
```

