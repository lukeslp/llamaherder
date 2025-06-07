'''
Belters Server (File Manipulation)
Based on the mistral:7b model.
This server accepts POST requests at the /chat endpoint and processes file manipulation tasks.
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
logger = logging.getLogger('belters_server')


@app.route('/chat', methods=['POST'])
def chat():
    '''
    Endpoint to receive file manipulation tasks.
    Expected JSON payload:
    {
      "content": "instruction for file manipulation",
      "task_id": "optional_task_id"
    }
    '''
    try:
        data = request.get_json()
        content = data.get('content', '')
        task_id = data.get('task_id', '')
        logger.info(f"Received file manipulation request with task_id: {task_id} and content: {content}")
        
        # Simulate file manipulation processing using Belters' model (mistral:7b)
        response_str = f"Belters processing file operation: {content}"
        
        response_payload = {
            "status": "success",
            "task_id": task_id,
            "agent": "Belters (File Manipulation)",
            "result": response_str
        }
        return jsonify(response_payload), 200
    except Exception as e:
        logger.error(f"Error processing file manipulation task: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 6001))
    logger.info(f"Starting Belters Server on port {port}")
    app.run(host='0.0.0.0', port=port) 