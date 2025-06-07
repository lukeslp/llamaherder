"""
DeepSeek observer server for real-time system monitoring and commentary.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ..core.events import event_bus, ObservationEvent
from .base import BaseModelServer, Message, Response

logger = logging.getLogger(__name__)

OBSERVER_SYSTEM_PROMPT = """You are the DeepSeek Observer, a meta-analysis agent responsible for monitoring and providing insights about the MoE system's operation.

Your responsibilities include:
1. Monitoring task execution and providing real-time commentary
2. Analyzing system performance and efficiency
3. Identifying potential issues or improvements
4. Providing strategic insights about task handling
5. Integrating user feedback to improve system operation

When providing observations:
- Be concise but informative
- Focus on actionable insights
- Highlight both successes and areas for improvement
- Consider system-wide implications
- Suggest optimizations when relevant

Format your responses as clear, direct observations that can help improve task execution and system performance."""

class ObserverServer(BaseModelServer):
    """DeepSeek observer server for real-time commentary"""
    
    def __init__(self, port: int = 6003):
        """Initialize the observer server"""
        super().__init__(
            model_name="deepseek-r1:14b",
            port=port,
            system_prompt=OBSERVER_SYSTEM_PROMPT
        )
        self.task_history: Dict[str, list[Dict[str, Any]]] = {}
        
    async def process_message(self, message: Message) -> Response:
        """Process incoming message and emit observations"""
        try:
            # Store message in task history
            if message.task_id not in self.task_history:
                self.task_history[message.task_id] = []
            self.task_history[message.task_id].append({
                "timestamp": datetime.now().isoformat(),
                "content": message.content,
                "type": "message"
            })
            
            # Get observation from model
            response = await super().process_message(message)
            
            # Store response in task history
            self.task_history[message.task_id].append({
                "timestamp": datetime.now().isoformat(),
                "content": response.content,
                "type": "observation"
            })
            
            # Emit observation event
            await event_bus.publish(
                "observation",
                ObservationEvent(
                    timestamp=datetime.now(),
                    content=response.content,
                    task_id=message.task_id,
                    metadata={
                        "type": "observer_insight",
                        "task_history_length": len(self.task_history[message.task_id])
                    }
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Observer processing error: {e}", exc_info=True)
            # Emit error observation
            await event_bus.publish(
                "observation",
                ObservationEvent(
                    timestamp=datetime.now(),
                    content=f"Error in observer processing: {str(e)}",
                    task_id=message.task_id,
                    metadata={
                        "type": "observer_error",
                        "error": str(e)
                    }
                )
            )
            raise
            
    async def get_task_history(self, task_id: str) -> list[Dict[str, Any]]:
        """Get the history of a specific task"""
        return self.task_history.get(task_id, [])
        
    def clear_task_history(self, task_id: Optional[str] = None):
        """Clear task history for a specific task or all tasks"""
        if task_id:
            self.task_history.pop(task_id, None)
        else:
            self.task_history.clear()

def create_app(**kwargs):
    """Create the Observer server application"""
    server = ObserverServer(**kwargs)
    return server.app

if __name__ == "__main__":
    server = ObserverServer()
    server.run() 