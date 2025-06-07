#!/usr/bin/env python
from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Optional, Any, Union


class BaseProvider(ABC):
    """
    Base class for all API providers.
    
    This abstract class defines the interface that all provider implementations
    must follow to ensure consistent behavior across different AI services.
    """
    
    @abstractmethod
    def __init__(self, api_key: str):
        """
        Initialize the provider with an API key.
        
        Args:
            api_key: The API key for authentication with the provider's service
        """
        self.api_key = api_key
    
    @abstractmethod
    def list_models(self, **kwargs) -> List[Dict[str, Any]]:
        """
        List available models from this provider.
        
        Args:
            **kwargs: Additional provider-specific parameters
            
        Returns:
            List of model objects containing at minimum 'id' and 'name' fields
        """
        raise NotImplementedError("Subclasses must implement list_models")
    
    @abstractmethod
    def stream_chat_response(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Stream a chat response from the provider.
        
        Args:
            prompt: The user's message
            **kwargs: Additional parameters like model, max_tokens, etc.
            
        Returns:
            A generator yielding content chunks as they become available
        """
        raise NotImplementedError("Subclasses must implement stream_chat_response")
    
    @abstractmethod
    def clear_conversation(self):
        """Clear the conversation history."""
        raise NotImplementedError("Subclasses must implement clear_conversation")
    
    @abstractmethod
    def process_image(self, file_path: str) -> Optional[str]:
        """
        Process an image for use in multimodal requests.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Encoded image data or None if processing failed
        """
        raise NotImplementedError("Subclasses must implement process_image")
    
    @abstractmethod
    def call_tool(self, prompt: str, model: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Use the model to call tools based on the prompt.
        
        Args:
            prompt: The user's message
            model: The model to use
            tools: List of tool definitions
            **kwargs: Additional parameters
            
        Returns:
            Dict containing the response and any tool calls
        """
        raise NotImplementedError("Subclasses must implement call_tool")
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """
        Format a date string for consistent output.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Formatted date string
        """
        pass
    
    @abstractmethod
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 or other format required by the provider.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Encoded image data or None if encoding failed
        """
        pass 