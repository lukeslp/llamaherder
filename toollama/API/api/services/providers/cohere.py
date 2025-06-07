#!/usr/bin/env python
"""
Cohere API Provider Implementation
This module provides an interface to the Cohere API for streaming chat responses.
"""

import os
import sys
import json
import requests
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
import logging

# Configure logging
logger = logging.getLogger(__name__)

class CohereProvider:
    """Provider implementation for Cohere API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Cohere client with the provided API key."""
        # Try to get API key from init param, then environment, then use a placeholder
        self.api_key = api_key or os.environ.get("COHERE_API_KEY", "placeholder_key")
        self.base_url = 'https://api.cohere.com/v2'
        self.dataset_url = 'https://api.cohere.com/v1/datasets'
        
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
        
        logger.info("Initialized Cohere provider")

    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 1000,
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Retrieve available Cohere models.
        
        Args:
            sort_by (str): Field to sort by (created/id/capabilities)
            page (int): Page number for pagination
            page_size (int): Number of models per page
            capability_filter (Optional[str]): Filter by capability
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Get models filtered for chat endpoint
            response = requests.get(
                "https://api.cohere.com/v1/models",  # Models endpoint still v1
                headers=headers,
                params={"endpoint": "chat"}
            )
            response.raise_for_status()
            
            models = []
            for model in response.json()["models"]:
                # Extract capabilities from model info
                capabilities = []
                if "chat" in model.get("endpoints", []):
                    capabilities.append("chat")
                if model.get("finetuned"):
                    capabilities.append("finetuned")
                
                models.append({
                    "id": model["name"],
                    "name": model["name"],
                    "description": f"Cohere {model['name']} model",
                    "endpoints": model["endpoints"],
                    "context_length": model.get("context_length", 4096),
                    "is_finetuned": model.get("finetuned", False),
                    "capabilities": capabilities,
                    "created_at": datetime.now().isoformat(),
                    "owned_by": "Cohere"
                })
            
            # Apply capability filter if specified
            if capability_filter:
                models = [m for m in models if capability_filter in m["capabilities"]]
            
            # Sort models
            if sort_by == "created":
                models.sort(key=lambda x: x["created_at"], reverse=True)
            elif sort_by == "capabilities":
                models.sort(key=lambda x: len(x["capabilities"]), reverse=True)
            else:  # sort by id
                models.sort(key=lambda x: x["id"])
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            # Fallback to known models if API fails
            return [{
                "id": "command-r-plus-08-2024",
                "name": "command-r-plus-08-2024",
                "description": "Cohere Command-R Plus model",
                "endpoints": ["chat"],
                "context_length": 4096,
                "is_finetuned": False,
                "capabilities": ["chat"],
                "created_at": datetime.now().isoformat(),
                "owned_by": "Cohere"
            }, {
                "id": "command-light",
                "name": "command-light",
                "description": "Cohere Command Light model",
                "endpoints": ["chat"],
                "context_length": 4096,
                "is_finetuned": False,
                "capabilities": ["chat"],
                "created_at": datetime.now().isoformat(),
                "owned_by": "Cohere"
            }]

    def stream_chat_response(
        self,
        message: str,
        model: str = "command-r-plus-08-2024",
        max_tokens: int = 1024,
        temperature: float = 0.3,
        image_data: Optional[Union[str, List[str]]] = None,
        image_path: Optional[str] = None,
        file_data: Optional[str] = None,
        is_url: bool = False,
        **kwargs
    ) -> Generator[Dict, None, None]:
        """
        Stream a chat response from Cohere.
        
        Args:
            message (str): The user's input message
            model (str): The Cohere model to use
            max_tokens (int): Maximum number of tokens in the response
            temperature (float): Response temperature (0.0 to 1.0)
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            image_path (Optional[str]): Path to an image file to process
            file_data (Optional[str]): Base64 encoded file data
            is_url (bool): Whether image_data contains URLs
            
        Yields:
            Dict: Chunks of the response text as they arrive
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Process image_path if provided
        if image_path and not image_data:
            try:
                with open(image_path, "rb") as image_file:
                    image_data = b64encode(image_file.read()).decode('utf-8')
            except Exception as e:
                logger.error(f"Error reading image file: {e}")
                yield {"content": f"Error reading image file: {str(e)}"}
                return
        
        # Format message content based on whether we have attachments
        content = self._format_message_with_attachments(message, image_data, file_data, is_url)
        
        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": content
        })
        
        payload = {
            "model": model,
            "messages": self.chat_history,
            "temperature": temperature,
            "stream": True,
            "connectors": [{"id":"web-search"}],
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # Remove "data: " prefix
                        data = json.loads(line_text)
                        
                        # Handle different event types
                        if data["type"] == "content-delta":
                            text = data["delta"]["message"]["content"]["text"]
                            full_response += text
                            yield {"content": text}
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}")
                        continue
            
            # Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            # Remove the user message if request failed
            self.chat_history.pop()
            yield {"content": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            # Remove the user message if request failed
            self.chat_history.pop()
            yield {"content": str(e)}

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
        logger.info("Cleared conversation history")
        return {"status": "success", "message": "Conversation cleared"}

    def _format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """Format a message with optional image and file data for the API."""
        if not image_data and not file_data:
            return message
        
        content = [{"type": "text", "text": message}]
        
        # Add images
        if image_data:
            # Convert single image to list
            if isinstance(image_data, str):
                image_data = [image_data]
            
            for img in image_data:
                if is_url:
                    content.append({
                        "type": "image_url",
                        "image_url": img
                    })
                else:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img}"
                        }
                    })
        
        # Add file if provided
        if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{file_data}"
            })
        
        return content 