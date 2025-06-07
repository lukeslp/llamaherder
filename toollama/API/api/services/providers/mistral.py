#!/usr/bin/env python
import os
import sys
import io
import json
import base64
import logging
from datetime import datetime
from typing import Dict, Any, List, Generator, Optional

# Configure logging first
logger = logging.getLogger(__name__)

# Import specific modules with proper error handling
try:
    from PIL import Image
    has_pil = True
    logger.info("Successfully imported PIL.Image")
except ImportError:
    has_pil = False
    logger.warning("PIL not available. Image processing will be disabled.")

# Direct import of requests - simpler approach from flask_chat_mistral.py
try:
    import requests
    has_requests = True
    logger.info("Successfully imported requests library")
except ImportError:
    has_requests = False
    logger.error("Requests library not available. Please install it with 'pip install requests'")

# Import base provider class
try:
    from api.services.providers.base import BaseProvider
except ImportError:
    # Define BaseProvider here if not available
    class BaseProvider:
        """Base class for all API providers."""
        def __init__(self, api_key: str):
            self.api_key = api_key

        def list_models(self, **kwargs):
            raise NotImplementedError("Subclasses must implement list_models")

        def stream_chat_response(self, prompt: str, **kwargs):
            raise NotImplementedError("Subclasses must implement stream_chat_response")

        def clear_conversation(self):
            raise NotImplementedError("Subclasses must implement clear_conversation")


class MistralProvider(BaseProvider):
    """
    Provider implementation for Mistral AI API.
    Supports chat streaming, vision capabilities, and function calling.
    """
    def __init__(self, api_key: str):
        """Initialize the Mistral client with the provided API key."""
        super().__init__(api_key)
        self.api_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CaminaChat/1.0"
        }
        # Initialize with system message
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
        logger.info("Initialized Mistral Provider")
        
        # Verify dependencies are available
        if not has_requests:
            logger.error("The 'requests' library is required but not installed. Please install it with 'pip install requests'")
        if not has_pil and logger:
            logger.warning("The 'Pillow' library is recommended for image processing. Install with 'pip install Pillow'")

    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 50,
        capability_filter: str = None,
        category_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve available Mistral models with pagination.
        In case of API failure, fallback models are returned.
        """
        if not has_requests:
            logger.error("Cannot fetch models: 'requests' library not available")
            return self._get_fallback_models(None, None, page, page_size)
            
        try:
            # Use the requests module directly
            logger.info(f"Fetching models from Mistral API")
            response = requests.get(f"{self.api_url}/models", headers=self.headers)
            response.raise_for_status()
            
            # Dictionary to track unique models by ID
            unique_models = {}
            
            for model in response.json()["data"]:
                capabilities = []
                if model["capabilities"]["completion_chat"]:
                    capabilities.append("chat")
                if model["capabilities"]["function_calling"]:
                    capabilities.append("function")
                if model["capabilities"].get("vision"):
                    capabilities.append("vision")
                
                model_id = model["id"].lower()
                
                # Determine category (just for information, not filtering)
                if "mixtral" in model_id:
                    category = "mixtral"
                elif "pixtral" in model_id:
                    category = "pixtral"
                else:
                    category = "mistral"
                
                # NOTE: Removed capability and category filters to include all models
                
                # Create model info
                model_info = {
                    "id": model["id"],
                    "name": model["name"] or model["id"].replace("-", " ").title(),
                    "description": model["description"] or f"Mistral {model['id']} model",
                    "context_length": model["max_context_length"],
                    "created_at": datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                    "created": model["created"],
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "category": category,
                    "owned_by": model["owned_by"],
                    "deprecated_at": model.get("deprecation")
                }
                
                # Store model in unique_models dictionary
                unique_models[model["id"]] = model_info
            
            # Convert dictionary to list
            models = list(unique_models.values())
            
            # Sort models
            if sort_by == "created":
                models.sort(key=lambda x: x["created"], reverse=True)
            elif sort_by == "context_length":
                models.sort(key=lambda x: x["context_length"], reverse=True)
            else:
                models.sort(key=lambda x: x["id"], reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            logger.info(f"Retrieved {len(models)} unique models from Mistral API")
            return models[start_idx:end_idx]
        except Exception as e:
            logger.error(f"Error fetching Mistral models: {e}")
            return self._get_fallback_models(None, None, page, page_size)

    def _get_fallback_models(self, capability_filter, category_filter, page, page_size):
        """Return fallback models when API is unavailable"""
        # Fallback models
        logger.info("Using fallback models for Mistral")
        fallback_models = [{
            "id": "mistral-tiny",
            "name": "Mistral Tiny",
            "description": "Mistral Tiny model",
            "context_length": 32768,
            "created_at": "2024-03-01",
            "created": datetime.now().timestamp(),
            "capabilities": ["chat"],
            "capability_count": 1,
            "category": "mistral",
            "owned_by": "mistralai"
        }, {
            "id": "mistral-small",
            "name": "Mistral Small",
            "description": "Mistral Small model",
            "context_length": 32768,
            "created_at": "2024-03-01",
            "created": datetime.now().timestamp(),
            "capabilities": ["chat", "function"],
            "capability_count": 2,
            "category": "mistral",
            "owned_by": "mistralai"
        }, {
            "id": "mistral-medium",
            "name": "Mistral Medium",
            "description": "Mistral Medium model",
            "context_length": 32768,
            "created_at": "2024-03-01",
            "created": datetime.now().timestamp(),
            "capabilities": ["chat", "function"],
            "capability_count": 2,
            "category": "mistral",
            "owned_by": "mistralai"
        }, {
            "id": "pixtral-large-2411",
            "name": "Pixtral Large",
            "description": "Pixtral Large model with vision capabilities",
            "context_length": 32768,
            "created_at": "2024-05-01",
            "created": datetime.now().timestamp(),
            "capabilities": ["chat", "function", "vision"],
            "capability_count": 3,
            "category": "pixtral",
            "owned_by": "mistralai"
        }]
        # Return all fallback models without filtering
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return fallback_models[start_idx:end_idx]

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """Create a test image and return its base64 encoding."""
        if not has_pil:
            logger.error("Cannot create test image: PIL not available")
            return None
            
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error creating test image: {e}")
            return None

    def process_image(self, file_path: str) -> Optional[str]:
        """Load an image from a file and return its base64 encoding."""
        if not has_pil:
            logger.error("Cannot process image: PIL not available")
            return None
            
        try:
            logger.info(f"Processing image from path: {file_path}")
            
            # Check if the file exists
            if not os.path.exists(file_path):
                logger.error(f"File does not exist: {file_path}")
                return None
                
            # Try to determine image format from file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            format_map = {
                '.png': 'PNG',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.webp': 'WEBP',
                '.gif': 'GIF'
            }
            
            # Default format to use if we can't determine from extension
            default_format = 'PNG'
            img_format = format_map.get(file_ext, default_format)
            
            # Open the image
            with Image.open(file_path) as img:
                # If the image has a format, use it; otherwise use our determined format
                img_format = img.format or img_format
                
                if img_format not in ['PNG', 'JPEG', 'WEBP', 'GIF']:
                    logger.error(f"Unsupported image format: {img_format}.")
                    return None
                    
                if img_format == 'GIF' and getattr(img, 'is_animated', False):
                    logger.error("Animated GIFs are not supported.")
                    return None
                    
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                # Resize if too large
                if img.size[0] > 1024 or img.size[1] > 1024:
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Save to bytes with explicit format
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img_format)
                
                # Check file size
                if img_byte_arr.tell() > 10 * 1024 * 1024:
                    logger.error("Image file size exceeds 10MB limit.")
                    return None
                
                # Encode to base64
                encoded_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                logger.info(f"Successfully processed image, format={img_format}, length={len(encoded_data)}")
                return encoded_data
                
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def format_message_with_image(self, message: str, image_data=None, is_url: bool = False):
        """
        Format a message with optional image data.
        If image_data is provided, returns a list of content objects.
        """
        if not image_data:
            return message
        
        if isinstance(image_data, str):
            image_data = [image_data]
        
        if len(image_data) > 8:
            logger.warning("Maximum 8 images per request. Using first 8 images.")
            image_data = image_data[:8]
        
        content = [{"type": "text", "text": message}]
        
        for img in image_data:
            if is_url:
                content.append({"type": "image_url", "image_url": img})
            else:
                # For base64 encoded images, use data URI format
                content.append({
                    "type": "image_url", 
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}",
                        "detail": "high"
                    }
                })
        
        logger.info(f"Formatted message with {len(image_data)} images")
        return content

    def stream_chat_response(
        self,
        prompt: str,
        model: str = "mistral-tiny",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 1.0,
        safe_prompt: bool = True,
        image_data=None,
        image_path=None,
        is_url: bool = False,
        file_data=None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Mistral.
        """
        if not has_requests:
            logger.error("Cannot stream chat: 'requests' library not available")
            yield "Error: The 'requests' library is required but not installed."
            return
            
        try:
            # Process image if path is provided
            if image_path and not image_data:
                logger.info(f"Processing image from path: {image_path}")
                image_data = self.process_image(image_path)
                if not image_data:
                    logger.error(f"Failed to process image from path: {image_path}")
            
            # Format message content based on whether we have images or files
            content = prompt
            if image_data:
                logger.info(f"Processing message with image data (is_url={is_url})")
                content = self.format_message_with_image(prompt, image_data, is_url)
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": content})
            
            # Prepare API payload
            payload = {
                "model": model,
                "messages": self.conversation_history,
                "stream": True,
                "temperature": temperature,
                "top_p": top_p,
                "safe_prompt": safe_prompt
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            # Print debug info
            logger.info(f"Sending request to Mistral API with model: {model}")
            if image_data:
                logger.info(f"Request includes image data of length: {len(image_data) if isinstance(image_data, str) else 'multiple images'}")
            
            # Make API request using the requests module directly
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                yield f"Error: {error_msg}"
                self.conversation_history.pop()  # Remove the user message if request failed
                return
                
            response.raise_for_status()
            
            # Process streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        line_text = line_text[6:]
                    if line_text == "[DONE]":
                        continue
                    try:
                        data = json.loads(line_text)
                        content_chunk = data['choices'][0]['delta'].get('content', '')
                        if content_chunk:
                            full_response += content_chunk
                            yield content_chunk
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing chunk: {e}")
                        continue
            
            # Add assistant's response to history
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            self.conversation_history.pop()  # Remove the user message if request failed
            yield f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            self.conversation_history.pop()
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear conversation history (keeping only the system prompt)."""
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

    def call_tool(self, prompt: str, model: str, tools: List[Dict[str, Any]], max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Call tools using the Mistral API's function calling capabilities.
        
        Args:
            prompt: The user's prompt
            model: The model to use
            tools: List of tool definitions
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing the response and any tool calls
        """
        try:
            if not has_requests:
                logger.error("Cannot call tools: 'requests' library not available")
                return {
                    "error": "Requests library not available",
                    "content": "Error: The 'requests' library is required but not installed.",
                    "tool_calls": [],
                    "model": model,
                    "provider": "mistral"
                }

            # Convert our tools format to Mistral's format if needed
            mistral_tools = []
            for tool in tools:
                if "function" in tool:
                    mistral_tools.append({
                        "function": tool["function"]
                    })
            
            # Add user message to history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Prepare API payload
            payload = {
                "model": model,
                "messages": self.conversation_history,
                "tools": mistral_tools,
                "temperature": 0.7,
                "top_p": 1.0,
                "max_tokens": max_tokens
            }
            
            # Make API request using the requests module directly
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract content and tool calls
            message = result["choices"][0]["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])
            
            # Add assistant's response to history
            self.conversation_history.append({
                "role": "assistant", 
                "content": content,
                "tool_calls": tool_calls
            })
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "model": model,
                "provider": "mistral"
            }
            
        except Exception as e:
            logger.error(f"Error calling tools: {e}")
            return {
                "error": str(e),
                "content": f"Error calling tools: {str(e)}",
                "tool_calls": [],
                "model": model,
                "provider": "mistral"
            }

    def encode_image(self, file_path: str) -> Optional[str]:
        """
        Encode an image to base64 for use with the API.
        
        Args:
            file_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if encoding failed
        """
        logger.info(f"Encoding image from path: {file_path}")
        return self.process_image(file_path) 