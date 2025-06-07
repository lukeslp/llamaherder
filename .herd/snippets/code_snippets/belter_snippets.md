# Code Snippets from toollama/moe/servers/belter.py

File: `toollama/moe/servers/belter.py`  
Language: Python  
Extracted: 2025-06-07 05:12:12  

## Snippet 1
Lines 2-10

```Python
Belter server - Domain specialist for the MoE system.
"""

import logging
from typing import Dict, Any
from .base import BaseModelServer, Message, Response

logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 16-24

```Python
def __init__(self, **kwargs):
        """Initialize the Belter server"""
        super().__init__(
            model_name="belter-base",
            port=kwargs.get('port', self.DEFAULT_PORT),
            host=kwargs.get('host', 'localhost'),
            debug=kwargs.get('debug', False)
        )
```

## Snippet 3
Lines 25-38

```Python
async def process_message(self, message: Message) -> Response:
        """
        Process a message with the Belter model.

        Args:
            message: Message to process

        Returns:
            Response object
        """
        try:
            # Get response from model
            response = await super().process_message(message)
```

## Snippet 4
Lines 39-48

```Python
# Parse JSON response if possible
            try:
                import json
                content = json.loads(response.content)
                response.content = content
            except:
                pass

            return response
```

## Snippet 5
Lines 49-52

```Python
except Exception as e:
            logger.error(f"Belter processing error: {e}")
            raise
```

## Snippet 6
Lines 53-57

```Python
def create_app(**kwargs):
    """Create the Belter server application"""
    server = BelterServer(**kwargs)
    return server.app
```

