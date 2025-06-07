# Code Snippets from toollama/moe/servers/caminaa_server.py

File: `toollama/moe/servers/caminaa_server.py`  
Language: Python  
Extracted: 2025-06-07 05:12:02  

## Snippet 1
Lines 1-19

```Python
'''
Caminaå Server (Coordinator)
Based on the mistral-small:22b model.
This server accepts POST requests at the /chat endpoint and processes task queries.
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('caminaa_server')
```

## Snippet 2
Lines 23-35

```Python
def chat() -> 'flask.Response':
    '''
    Endpoint to receive chat queries and return a response.
    Expected JSON payload:
    {
      "content": "message",
      "task_id": "optional_task_id"
    }
    '''
    try:
        data = request.get_json()
        content = data.get('content', '')
        task_id = data.get('task_id', '')
```

## Snippet 3
Lines 36-47

```Python
logger.info(f"Received chat request with task_id: {task_id} and content: {content}")

        # Simulate processing using Caminaå's model (mistral-small:22b)
        response_str = f"Caminaå processing: {content}"

        response_payload = {
            "status": "success",
            "task_id": task_id,
            "agent": "Caminaå (Coordinator)",
            "result": response_str
        }
        return jsonify(response_payload), 200
```

## Snippet 4
Lines 48-50

```Python
except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500
```

