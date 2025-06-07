"""
Model communication system for interacting with model endpoints.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class CommunicationError(Exception):
    """Base class for communication errors"""
    pass

class ModelCommunicator:
    """Handles communication with model endpoints"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the communicator.
        
        Args:
            config: Configuration dictionary containing model endpoints
        """
        self.endpoints = config.get('model_endpoints', {})
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        self.retries = 3
        self.retry_delay = 1.0  # seconds
        
    async def send_message(
        self,
        model_id: str,
        message: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a model endpoint.
        
        Args:
            model_id: Model identifier
            message: Message to send
            timeout: Optional request timeout
            
        Returns:
            Model response
            
        Raises:
            CommunicationError: If communication fails
        """
        if model_id not in self.endpoints:
            raise CommunicationError(f"No endpoint configured for model {model_id}")
            
        endpoint = self.endpoints[model_id]
        
        # Try multiple times with exponential backoff
        for attempt in range(self.retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(
                        endpoint,
                        json=message,
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPError as e:
                logger.warning(
                    f"HTTP error communicating with {model_id} (attempt {attempt + 1}): {e}"
                )
                if attempt == self.retries - 1:
                    raise CommunicationError(f"Failed to communicate with {model_id}: {e}")
                    
            except Exception as e:
                logger.error(f"Error communicating with {model_id}: {e}")
                raise CommunicationError(f"Error communicating with {model_id}: {e}")
                
            # Wait before retrying
            await asyncio.sleep(self.retry_delay * (2 ** attempt))
            
    async def close(self) -> None:
        """Close the communicator and cleanup resources"""
        await self.client.aclose()
        
    def get_endpoint(self, model_id: str) -> str:
        """
        Get endpoint URL for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Endpoint URL
            
        Raises:
            CommunicationError: If no endpoint configured
        """
        if model_id not in self.endpoints:
            raise CommunicationError(f"No endpoint configured for model {model_id}")
        return self.endpoints[model_id]
        
    def add_endpoint(self, model_id: str, endpoint: str) -> None:
        """
        Add a new model endpoint.
        
        Args:
            model_id: Model identifier
            endpoint: Endpoint URL
        """
        self.endpoints[model_id] = endpoint
        logger.info(f"Added endpoint for model {model_id}: {endpoint}")
        
    def remove_endpoint(self, model_id: str) -> None:
        """
        Remove a model endpoint.
        
        Args:
            model_id: Model identifier
        """
        if model_id in self.endpoints:
            del self.endpoints[model_id]
            logger.info(f"Removed endpoint for model {model_id}")
            
    def update_endpoint(self, model_id: str, endpoint: str) -> None:
        """
        Update an existing model endpoint.
        
        Args:
            model_id: Model identifier
            endpoint: New endpoint URL
        """
        if model_id in self.endpoints:
            self.endpoints[model_id] = endpoint
            logger.info(f"Updated endpoint for model {model_id}: {endpoint}")
        else:
            self.add_endpoint(model_id, endpoint) 