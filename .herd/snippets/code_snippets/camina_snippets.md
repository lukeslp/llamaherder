# Code Snippets from toollama/moe/servers/camina.py

File: `toollama/moe/servers/camina.py`  
Language: Python  
Extracted: 2025-06-07 05:12:07  

## Snippet 1
Lines 2-11

```Python
Camina server - Primary agent for the MoE system.
"""

import os
import logging
from tools.api_utils import send_post_request

logger = logging.getLogger('camina')
logging.basicConfig(level=logging.INFO)
```

## Snippet 2
Lines 12-15

```Python
# Define endpoints for other agents (with environment variable overrides if needed)
BELTERS_URL = os.getenv('BELTERS_URL', 'http://localhost:6001/chat')
DRUMMERS_URL = os.getenv('DRUMMERS_URL', 'http://localhost:6002/chat')
DEEPSEEK_URL = os.getenv('DEEPSEEK_URL', 'http://localhost:6003/chat')
```

## Snippet 3
Lines 18-23

```Python
def coordinate_task(task_id: str, content: str) -> str:
    """
    Coordinates the task by sending the content to Belters, Drummers, and DeepSeek.
    Aggregates their responses and returns a synthesized result.

    Args:
```

## Snippet 4
Lines 27-52

```Python
Returns:
      str: A synthesized result string combining responses from all agents.
    """
    belters_payload = {"content": f"file operation: {content}", "task_id": task_id}
    drummers_payload = {"content": f"information inquiry: {content}", "task_id": task_id}
    deepseek_payload = {"content": f"reasoning check: {content}", "task_id": task_id}

    logger.info("Sending task to Belters...")
    belters_response = send_post_request(BELTERS_URL, belters_payload)

    logger.info("Sending task to Drummers...")
    drummers_response = send_post_request(DRUMMERS_URL, drummers_payload)

    logger.info("Sending task to DeepSeek Reasoner...")
    deepseek_response = send_post_request(DEEPSEEK_URL, deepseek_payload)

    # Combine responses. More sophisticated synthesis can be implemented here.
    synthesized_result = (
        f"Coordinator results:\n"
        f"Belters: {belters_response.get('result', 'No result')}\n"
        f"Drummers: {drummers_response.get('result', 'No result')}\n"
        f"DeepSeek: {deepseek_response.get('result', 'No result')}"
    )

    logger.info("Task coordination complete.")
    return synthesized_result
```

## Snippet 5
Lines 55-57

```Python
if __name__ == '__main__':
    # For standalone testing of the coordination function
    test_task_id = "test123"
```

