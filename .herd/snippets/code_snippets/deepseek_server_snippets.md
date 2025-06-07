# Code Snippets from toollama/moe/servers/deepseek_server.py

File: `toollama/moe/servers/deepseek_server.py`  
Language: Python  
Extracted: 2025-06-07 05:11:55  

## Snippet 1
Lines 1-19

```Python
'''
DeepSeek Server (Background Reasoning)
Based on the deepseek-r1:7b model.
This server accepts POST requests at the /chat endpoint and processes background reasoning tasks.
'''

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('deepseek_server')
```

## Snippet 2
Lines 23-27

```Python
def chat():
    '''
    Endpoint to receive background reasoning tasks.
    Expected JSON payload:
    {
```

## Snippet 3
Lines 30-35

```Python
}
    '''
    try:
        data = request.get_json()
        content = data.get('content', '')
        task_id = data.get('task_id', '')
```

## Snippet 4
Lines 36-47

```Python
logger.info(f"Received reasoning request with task_id: {task_id} and content: {content}")

        # Simulate background reasoning using DeepSeek's model (deepseek-r1:7b)
        response_str = f"DeepSeek reasoning on: {content}"

        response_payload = {
            "status": "success",
            "task_id": task_id,
            "agent": "DeepSeek Reasoner (Background)",
            "result": response_str
        }
        return jsonify(response_payload), 200
```

## Snippet 5
Lines 48-50

```Python
except Exception as e:
        logger.error(f"Error processing reasoning task: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500
```

