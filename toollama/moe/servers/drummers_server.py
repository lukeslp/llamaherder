'''
Drummers Server (Information Gathering)
Based on the mistral:7b model.
This server accepts POST requests at the /chat endpoint and processes information gathering tasks.
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
logger = logging.getLogger('drummers_server')


@app.route('/chat', methods=['POST'])
def chat():
    '''
    Endpoint to receive information gathering tasks.
    Expected JSON payload:
    {
      "content": "instruction for information gathering",
      "task_id": "optional_task_id"
    }
    '''
    try:
        data = request.get_json()
        content = data.get('content', '')
        task_id = data.get('task_id', '')
        logger.info(f"Received information gathering request with task_id: {task_id} and content: {content}")
        
        # Simulate information gathering using Drummers' model (mistral:7b)
        response_str = f"Drummers gathering information: {content}"
        
        response_payload = {
            "status": "success",
            "task_id": task_id,
            "agent": "Drummers (Information Gathering)",
            "result": response_str
        }
        return jsonify(response_payload), 200
    except Exception as e:
        logger.error(f"Error processing information gathering task: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 6002))
    logger.info(f"Starting Drummers Server on port {port}")
    app.run(host='0.0.0.0', port=port) 