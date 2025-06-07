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


@app.route('/chat', methods=['POST'])
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
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 6000))
    logger.info(f"Starting Caminaå Server on port {port}")
    app.run(host='0.0.0.0', port=port) 