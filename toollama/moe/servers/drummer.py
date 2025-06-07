"""
Drummer server - Task executor for the MoE system.
"""

import logging
from typing import Dict, Any
from .base import BaseModelServer, Message, Response

logger = logging.getLogger(__name__)

class DrummerServer(BaseModelServer):
    """Server for Drummer task executors"""
    
    DEFAULT_PORT = 6002  # Drummer base port
    
    def __init__(self, **kwargs):
        """Initialize the Drummer server"""
        super().__init__(
            model_name="drummer-base",
            port=kwargs.get('port', self.DEFAULT_PORT),
            host=kwargs.get('host', 'localhost'),
            debug=kwargs.get('debug', False)
        )
        
    async def process_message(self, message: Message) -> Response:
        """
        Process a message with the Drummer model.
        
        Args:
            message: Message to process
            
        Returns:
            Response object
        """
        try:
            # Get response from model
            response = await super().process_message(message)
            
            # Parse JSON response if possible
            try:
                import json
                content = json.loads(response.content)
                response.content = content
            except:
                pass
                
            return response
            
        except Exception as e:
            logger.error(f"Drummer processing error: {e}")
            raise

def create_app(**kwargs):
    """Create the Drummer server application"""
    server = DrummerServer(**kwargs)
    return server.app

if __name__ == "__main__":
    server = DrummerServer()
    server.run() 