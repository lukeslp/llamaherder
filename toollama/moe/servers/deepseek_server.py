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


@app.route('/chat', methods=['POST'])
def chat():
    '''
    Endpoint to receive background reasoning tasks.
    Expected JSON payload:
    {
      "content": "instruction for reasoning",
      "task_id": "optional_task_id"
    }
    '''
    try:
        data = request.get_json()
        content = data.get('content', '')
        task_id = data.get('task_id', '')
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
    except Exception as e:
        logger.error(f"Error processing reasoning task: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 6003))
    logger.info(f"Starting DeepSeek Server on port {port}")
    app.run(host='0.0.0.0', port=port) 