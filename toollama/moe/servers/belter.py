"""
Belter server - Domain specialist for the MoE system.
"""

import logging
from typing import Dict, Any
from .base import BaseModelServer, Message, Response

logger = logging.getLogger(__name__)

class BelterServer(BaseModelServer):
    """Server for Belter domain specialists"""
    
    DEFAULT_PORT = 6001  # Belter base port
    
    def __init__(self, **kwargs):
        """Initialize the Belter server"""
        super().__init__(
            model_name="belter-base",
            port=kwargs.get('port', self.DEFAULT_PORT),
            host=kwargs.get('host', 'localhost'),
            debug=kwargs.get('debug', False)
        )
        
    async def process_message(self, message: Message) -> Response:
        """
        Process a message with the Belter model.
        
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
            logger.error(f"Belter processing error: {e}")
            raise

def create_app(**kwargs):
    """Create the Belter server application"""
    server = BelterServer(**kwargs)
    return server.app

if __name__ == "__main__":
    server = BelterServer()
    server.run() 