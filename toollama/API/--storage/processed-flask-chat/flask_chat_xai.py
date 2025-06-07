#!/usr/bin/env python
"""
X.AI API Chat Implementation for Flask
This module provides a Flask interface to the X.AI API with support for:
- Interactive model selection
- Response streaming
- Multimodal inputs (text + images)
"""

import os
import sys
import tempfile
import io
import json
from openai import OpenAI
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image

class XAIChat:
    def __init__(self, api_key: str):
        """Initialize the X.AI client with the provided API key."""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
            }
        ]
    
    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [self.conversation_history[0]]
    
    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 1000,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available X.AI models dynamically.
        
        Args:
            sort_by (str): Field to sort by (created/capabilities/id)
            page (int): Page number for pagination
            page_size (int): Number of models per page
            capability_filter (Optional[str]): Filter by capability
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Fetch models from the X.AI API
            response = self.client.models.list()
            
            # Process and format the models
            models = []
            for model in response.data:
                # Extract capabilities from model metadata
                capabilities = []
                if "vision" in model.id or "image" in model.id:
                    capabilities.append("images")
                capabilities.extend(["text", "code"])  # All models support text and code
                
                model_data = {
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
                    "description": f"X.AI {model.id} model",
                    "capabilities": capabilities,
                    "context_window": getattr(model, "context_window", 8192),
                    "created_at": datetime.fromtimestamp(model.created).strftime("%Y-%m-%d")
                }
                
                # Apply capability filter if specified
                if capability_filter and capability_filter not in capabilities:
                    continue
                
                models.append(model_data)
            
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
            print(f"Error fetching models: {e}", file=sys.stderr)
            # Fallback to basic Grok model if API fails
            return [{
                "id": "grok-2-latest",
                "name": "Grok 2 Latest",
                "description": "X.AI Grok 2 base model",
                "capabilities": ["text", "code", "images"],
                "context_window": 8192,
                "created_at": "2024-02-01"
            }]
    
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                return b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None

    def create_test_image(self) -> str:
        """Create a simple test image and return its base64 encoding."""
        # Create a 100x100 red square image
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return b64encode(img_byte_arr).decode('utf-8')

    def stream_chat_response(
        self,
        prompt: str,
        model: str,
        image: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from X.AI.
        
        Args:
            prompt (str): The user's input message
            model (str): The X.AI model to use
            image (Optional[str]): Base64 encoded image data
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        # Add image content if provided
        if image:
            message_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image}"
                    }
                }
            ]
        else:
            message_content = prompt

        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message_content
        })

        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                stream=True
            )
            
            response_text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    yield text
            
            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
                    
        except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)
            # Remove the user message if request failed
            self.conversation_history.pop()
            yield str(e) 