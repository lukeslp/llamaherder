"""
Base server class for model endpoints.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message(BaseModel):
    """Message model for requests"""
    content: str
    task_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Response(BaseModel):
    """Response model for all endpoints"""
    status: str
    task_id: Optional[str] = None
    content: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseModelServer:
    """Base class for all model servers"""
    
    DEFAULT_PORT = 6000  # Base port, each model type will offset from this
    OLLAMA_API = "http://localhost:11434/api"
    
    def __init__(
        self,
        model_name: str,
        port: Optional[int] = None,
        host: str = "0.0.0.0",
        debug: bool = False
    ):
        """
        Initialize the model server.
        
        Args:
            model_name: Name of the Ollama model to use
            port: Port to run the server on (optional)
            host: Host to bind to
            debug: Enable debug logging
        """
        self.model_name = model_name
        self.port = port or self.DEFAULT_PORT
        self.host = host
        
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        self.app = FastAPI(
            title=f"{model_name} Server",
            description=f"API server for {model_name} model",
            version="0.1.0"
        )
        
        # Register routes
        self.setup_routes()
        
        logger.info(f"Initialized {model_name} server on port {self.port}")
        
    def setup_routes(self) -> None:
        """Set up API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            try:
                # Try to ping the model
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.OLLAMA_API}/chat",
                        json={
                            "model": self.model_name,
                            "messages": [{"role": "user", "content": "test"}]
                        }
                    )
                    response.raise_for_status()
                    return {"status": "healthy", "model": self.model_name}
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail=str(e))
                
        @self.app.post("/chat")
        async def chat(message: Message):
            """Chat endpoint"""
            try:
                # Process message
                response = await self.process_message(message)
                return response
            except Exception as e:
                logger.error(f"Chat error: {e}")
                return Response(
                    status="error",
                    task_id=message.task_id,
                    error=str(e)
                )
                
    async def process_message(self, message: Message) -> Response:
        """
        Process an incoming message.
        
        Args:
            message: Message to process
            
        Returns:
            Response object
        """
        try:
            # Get response from model using HTTP API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.OLLAMA_API}/chat",
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": message.content}]
                    }
                )
                response.raise_for_status()
                
                # Handle streaming response
                full_response = ""
                for line in response.text.split('\n'):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if 'message' in data and 'content' in data['message']:
                            full_response += data['message']['content']
                    except json.JSONDecodeError:
                        continue
                
                return Response(
                    status="success",
                    task_id=message.task_id,
                    content=full_response,
                    metadata=message.metadata
                )
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise
            
    def run(self) -> None:
        """Run the server"""
        import uvicorn
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="debug"
        ) 