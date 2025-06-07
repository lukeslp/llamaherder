"""
Camina server - Primary agent for the MoE system.
"""

import os
import logging
from tools.api_utils import send_post_request

logger = logging.getLogger('camina')
logging.basicConfig(level=logging.INFO)

# Define endpoints for other agents (with environment variable overrides if needed)
BELTERS_URL = os.getenv('BELTERS_URL', 'http://localhost:6001/chat')
DRUMMERS_URL = os.getenv('DRUMMERS_URL', 'http://localhost:6002/chat')
DEEPSEEK_URL = os.getenv('DEEPSEEK_URL', 'http://localhost:6003/chat')


def coordinate_task(task_id: str, content: str) -> str:
    """
    Coordinates the task by sending the content to Belters, Drummers, and DeepSeek.
    Aggregates their responses and returns a synthesized result.

    Args:
      task_id (str): Unique identifier for the task.
      content (str): The task content or query.

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


if __name__ == '__main__':
    # For standalone testing of the coordination function
    test_task_id = "test123"
    test_content = "Test input for the primary agent."
    result = coordinate_task(test_task_id, test_content)
    print("Synthesized Result:")
    print(result) 