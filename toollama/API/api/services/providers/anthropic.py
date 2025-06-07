#!/usr/bin/env python
import os
import base64
import json
import logging
import io
import requests
from typing import Generator, List, Dict, Optional, Any, Union
from datetime import datetime
import sys
from io import BytesIO

# Configure logger
logger = logging.getLogger(__name__)

# Import PIL with proper error handling
try:
    from PIL import Image, ImageDraw, ImageFont
    has_pil = True
    logger.info("Successfully imported PIL modules")
except ImportError:
    has_pil = False
    logger.warning("PIL not available. Image processing will be disabled.")

from api.services.providers.base import BaseProvider
from api.utils.errors import ProviderError, ModelNotAvailableError

def convert_to_bool(value):
    """Convert a value to boolean, supporting both string and boolean inputs."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)

class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, api_key: str):
        """Initialize the Anthropic provider with direct API access."""
        try:
            self.api_key = api_key
            self.api_version = "2023-06-01"
            self.base_url = "https://api.anthropic.com"
            self.headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json"
            }
            self.conversation_history = []
            logger.info("Initialized Anthropic provider with direct API access")
            
            # Try to import the anthropic library for version info
            try:
                import anthropic
                logger.info(f"Using Anthropic library version: {anthropic.__version__}")
                
                # Try to initialize the client using the library
                try:
                    # Try the newer API first (v1)
                    self.client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Successfully initialized Anthropic client with v1 API")
                except Exception as e1:
                    logger.warning(f"Failed to initialize standard Anthropic client: {e1}")
                    try:
                        # Fall back to legacy client
                        self.client = anthropic.Client(api_key=api_key)
                        logger.info("Successfully initialized Anthropic client with legacy API")
                    except Exception as e2:
                        logger.warning(f"Failed to initialize legacy Anthropic client: {e2}")
                        logger.info("Using direct API access as fallback")
                        self.client = None
            except ImportError:
                logger.warning("Anthropic library not available, using direct API access")
                self.client = None
                
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise
        
    def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 10,
        capability_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve available Claude models with pagination.
        
        Args:
            sort_by (str): Field to sort by ('created', 'id', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('vision', 'text')
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Make direct API call to list models
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error fetching models: {response.status_code} - {response.text}")
                return self._get_fallback_models(capability_filter, page, page_size, sort_by, reverse)
                
            models_data = response.json()
            
            # Process and enhance model data
            processed_models = []
            for model in models_data.get('data', []):
                if not model['id'].startswith("claude"):
                    continue
                
                # Determine capabilities based on model name
                capabilities = ["text"]  # All models support text
                if "claude-3" in model['id'].lower():
                    if "opus" in model['id'].lower():
                        capabilities.extend(["vision", "code", "analysis"])
                    elif "sonnet" in model['id'].lower():
                        capabilities.extend(["vision", "code"])
                    elif "haiku" in model['id'].lower():
                        capabilities.append("vision")
                
                # Skip if doesn't match capability filter
                if capability_filter and capability_filter not in capabilities:
                    continue
                
                # Create enhanced model info
                model_info = {
                    "id": model['id'],
                    "name": model.get('display_name', model['id'].replace("-", " ").title()),
                    "description": f"Claude {model['id'].split('-')[1].title()}",
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": model['created_at'],
                    "created_at": self.format_date(model['created_at']),
                    "owned_by": "anthropic",
                    "provider": "anthropic"
                }
                processed_models.append(model_info)
            
            # Sort models
            if sort_by == "created":
                processed_models.sort(key=lambda x: x["created"], reverse=reverse)
            elif sort_by == "capabilities":
                processed_models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by id
                processed_models.sort(key=lambda x: x["id"], reverse=reverse)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return processed_models[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            # Fallback to static model list if API fails
            return self._get_fallback_models(capability_filter, page, page_size, sort_by, reverse)
    
    def _get_fallback_models(self, capability_filter, page, page_size, sort_by="created", reverse=True):
        """Return fallback models when API is unavailable"""
        models = [
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "description": "Claude 3 Opus",
                "capabilities": ["text", "vision", "code", "analysis"],
                "capability_count": 4,
                "created": "2024-02-29",
                "created_at": "February 29, 2024",
                "owned_by": "anthropic",
                "provider": "anthropic"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "description": "Claude 3 Sonnet",
                "capabilities": ["text", "vision", "code"],
                "capability_count": 3,
                "created": "2024-02-29",
                "created_at": "February 29, 2024",
                "owned_by": "anthropic",
                "provider": "anthropic"
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "description": "Claude 3 Haiku",
                "capabilities": ["text", "vision"],
                "capability_count": 2,
                "created": "2024-03-07",
                "created_at": "March 7, 2024",
                "owned_by": "anthropic",
                "provider": "anthropic"
            }
        ]
        
        # Apply capability filter
        if capability_filter:
            models = [m for m in models if capability_filter in m.get("capabilities", [])]
            
        # Sort by the specified field
        if sort_by == "created":
            models.sort(key=lambda x: x["created"], reverse=reverse)
        elif sort_by == "capabilities":
            models.sort(key=lambda x: x["capability_count"], reverse=reverse)
        else:  # sort by id
            models.sort(key=lambda x: x["id"], reverse=reverse)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return models[start_idx:end_idx]
    
    def create_test_image(self) -> str:
        """
        Create a test image with some shapes and text.
        Returns base64 encoded PNG image.
        """
        if not has_pil:
            logger.error("Cannot create test image: PIL not available")
            return None
            
        # Create a new image with a white background
        width, height = 400, 200
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
        draw.ellipse([200, 50, 300, 150], fill='blue', outline='black')
        
        # Add text
        draw.text((150, 160), "Test Image", fill='black')
        
        # Convert to base64
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode('utf-8')

    def process_image(self, image_path: str) -> Optional[Dict]:
        """
        Process an image file and return it in the format required by Claude.
        Supports PNG, JPEG, GIF, and WEBP formats.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[Dict]: Image data formatted for Claude API or None if invalid
        """
        if not has_pil:
            logger.error("Cannot process image: PIL not available")
            return None
            
        try:
            logger.info(f"Processing image from path: {image_path}")
            with Image.open(image_path) as img:
                # Convert format name to mime type
                format_to_mime = {
                    'PNG': 'image/png',
                    'JPEG': 'image/jpeg',
                    'GIF': 'image/gif',
                    'WEBP': 'image/webp'
                }
                
                if img.format not in format_to_mime:
                    logger.error(f"Unsupported image format: {img.format}. Must be PNG, JPEG, GIF, or WEBP.")
                    return None
                
                # Convert to bytes
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                image_data = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": format_to_mime[img.format],
                        "data": base64.b64encode(img_byte_arr).decode('utf-8')
                    }
                }
                logger.info(f"Successfully processed image from path, data length: {len(image_data['source']['data'])}")
                return image_data
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None

    def _get_model_limits(self, model: str) -> Dict[str, int]:
        """Get the token limits for a specific model."""
        # Enforce strict 4096 token limit for all models
        logger.warning(f"Enforcing strict 4096 token limit for Anthropic model: {model}")
        return {"max_tokens": 4096}

    def stream_chat_response(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 1024,
        image_path: Optional[str] = None,
        image_data: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Claude using direct API access.
        
        Args:
            prompt (str): The user's input message
            model (str): The Claude model to use
            max_tokens (int): Maximum number of tokens in the response (strictly limited to 4096)
            image_path (Optional[str]): Path to an image file (PNG, JPEG, GIF, or WEBP)
            image_data (Optional[str]): Base64-encoded image data
            **kwargs: Additional provider-specific parameters
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Enforce strict 4096 token limit
            max_tokens = min(max_tokens, 4096)
            logger.info(f"Using max_tokens: {max_tokens} for model: {model}")

            # Handle conversation history and system prompt if provided
            system_prompt = kwargs.get("system_prompt", "")
            use_test_image = kwargs.get("use_test_image", False)
            
            # Construct the message content
            message_content = [{"type": "text", "text": prompt}]
            
            if use_test_image:
                message_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": self.create_test_image()
                    }
                })
            elif image_path and os.path.exists(image_path):
                logger.info(f"Processing image from path: {image_path}")
                image_data_obj = self.process_image(image_path)
                if image_data_obj:
                    message_content.append(image_data_obj)
                    logger.info("Successfully added image from path")
                else:
                    logger.error(f"Failed to process image from path: {image_path}")
            elif image_data:
                # Process base64 image data
                try:
                    logger.info("Processing image from base64 data")
                    # Detect if image_data already has a media type prefix
                    if "," in image_data and ";base64," in image_data:
                        # Extract media type and base64 data
                        prefix, base64_data = image_data.split(",", 1)
                        media_type = prefix.split(";")[0].split(":")[1]
                        message_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data
                            }
                        })
                    else:
                        # Assume it's raw base64 data
                        message_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",  # Default assumption
                                "data": image_data
                            }
                        })
                    logger.info(f"Added image from base64 data, length: {len(image_data)}")
                except Exception as e:
                    logger.error(f"Error processing base64 image data: {e}")

            # Add the new message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message_content
            })
            
            # If we have a client, try to use it first
            if self.client:
                try:
                    logger.info(f"Using Anthropic client library for streaming with model: {model}")
                    
                    # Check if we're using the newer API (v1) or legacy
                    if hasattr(self.client, 'messages'):
                        # Newer API (v1)
                        with self.client.messages.stream(
                            max_tokens=max_tokens,
                            messages=self.conversation_history,
                            model=model,
                        ) as stream:
                            response_text = ""
                            for text in stream.text_stream:
                                response_text += text
                                yield {"content": text}  # Yield as dict with content key
                            
                            # Add assistant's response to conversation history
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": response_text
                            })
                            return
                    else:
                        # Legacy API
                        response = self.client.completion_stream(
                            prompt=self._format_prompt_for_legacy_api(),
                            model=model,
                            max_tokens_to_sample=max_tokens,
                            stream=True
                        )
                        
                        full_response = ""
                        for completion in response:
                            chunk = completion.completion
                            full_response += chunk
                            yield {"content": chunk}  # Yield as dict with content key
                            
                        # Add assistant's response to conversation history
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": full_response
                        })
                        return
                        
                except Exception as e:
                    logger.warning(f"Error using Anthropic client library: {e}. Falling back to direct API access.")
                    # Continue with direct API access
            
            # Prepare messages list with system prompt if provided
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                
            # Add all conversation history
            messages.extend(self.conversation_history)

            # Prepare the API request
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            logger.info(f"Sending request to Anthropic API with model: {model}")
            if image_path or image_data or use_test_image:
                logger.info("Request includes image data")
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=payload,
                stream=True
            )
            
            if response.status_code != 200:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                yield {"error": error_msg}
                return
                
            response.raise_for_status()
            full_response = ""
            
            # Process the streaming response
            for line in response.iter_lines():
                if not line.strip():
                    continue
                if line.startswith(b"data: "):
                    line = line[6:]
                if line == b"[DONE]":
                    continue
                try:
                    data = json.loads(line)
                    if "delta" in data and "text" in data["delta"]:
                        text = data["delta"]["text"]
                        full_response += text
                        yield {"content": text}  # Yield as dict with content key
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    continue
            
            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            yield {"error": str(e)}
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Unexpected error in stream_chat_response: {e}")
            yield {"error": error_msg}
            
    def _format_prompt_for_legacy_api(self):
        """Format the conversation history for the legacy Anthropic API."""
        formatted_prompt = "\n\n"
        
        for message in self.conversation_history:
            role = message["role"]
            
            if role == "user":
                formatted_prompt += "Human: "
                if isinstance(message["content"], list):
                    # Handle content that might have text and images
                    for content_item in message["content"]:
                        if content_item.get("type") == "text":
                            formatted_prompt += content_item.get("text", "")
                else:
                    formatted_prompt += message["content"]
                formatted_prompt += "\n\n"
            elif role == "assistant":
                formatted_prompt += "Assistant: "
                formatted_prompt += message["content"]
                formatted_prompt += "\n\n"
            elif role == "system":
                # System messages are handled differently in legacy API
                formatted_prompt = f"{message['content']}\n\n{formatted_prompt}"
        
        # Add the final assistant prompt
        formatted_prompt += "Assistant:"
        
        return formatted_prompt

    def generate_alt_text(
        self,
        image_path: Optional[str] = None,
        image_data: Optional[str] = None,
        prompt: str = "Generate a detailed description of this image for accessibility purposes.",
        model: str = "claude-3-opus-20240229",
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], Generator[str, None, None]]:
        """
        Generate alt text for an image.
        
        Args:
            image_path: Path to an image file
            image_data: Base64-encoded image data
            prompt: Specific prompt for alt text generation
            model: Model ID to use
            stream: Whether to stream the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary with alt text or a generator yielding response chunks
        """
        try:
            max_tokens = kwargs.get("max_tokens", 1024)
            
            # Handle the case where both image_path and image_data are None
            if not image_path and not image_data:
                raise ValueError("Either image_path or image_data must be provided")
            
            # Use the stream_chat_response method which handles both streaming and non-streaming
            if stream:
                return self.stream_chat_response(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    image_path=image_path,
                    image_data=image_data,
                    **kwargs
                )
            else:
                # For non-streaming, collect all the chunks into a single response
                alt_text = ""
                for chunk in self.stream_chat_response(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    image_path=image_path,
                    image_data=image_data,
                    **kwargs
                ):
                    alt_text += chunk
                
                return {
                    "alt_text": alt_text,
                    "model": model,
                    "provider": "anthropic"
                }
            
        except Exception as e:
            logger.error(f"Error generating alt text: {str(e)}")
            if not stream:
                return {
                    "error": str(e),
                    "alt_text": "",
                    "model": model,
                    "provider": "anthropic"
                }
            else:
                yield f"Error: {str(e)}"

    def call_tool(
        self,
        prompt: str,
        model: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call tools with Claude using direct API access.
        
        Args:
            prompt: The user's prompt/query
            model: Model ID to use
            tools: List of tool definitions in the expected format
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Response including content and tool calls
        """
        try:
            system_prompt = kwargs.get("system_prompt", "")
            
            # Prepare messages list with system prompt if provided
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
                
            # Add conversation history
            if self.conversation_history:
                messages.extend(self.conversation_history)
            
            # Add the user message
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Format tools as required by Anthropic API
            formatted_tools = []
            for tool in tools:
                if tool.get("type") == "function":
                    formatted_tools.append({
                        "name": tool["function"]["name"],
                        "description": tool["function"].get("description", ""),
                        "input_schema": tool["function"]["parameters"]
                    })
            
            # Prepare API payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "tools": formatted_tools if formatted_tools else None
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/v1/messages",
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response content and tool calls
            content = ""
            tool_calls = []
            
            # Extract content
            for content_block in result.get("content", []):
                if content_block.get("type") == "text":
                    content += content_block.get("text", "")
            
            # Extract tool calls
            for tool_use in result.get("tool_use", []):
                tool_call = {
                    "id": tool_use.get("id", ""),
                    "type": "function",
                    "function": {
                        "name": tool_use.get("name", ""),
                        "arguments": json.dumps(tool_use.get("input", {}))
                    }
                }
                tool_calls.append(tool_call)
            
            # Save to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            
            self.conversation_history.append({
                "role": "assistant",
                "content": content
            })
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "model": model,
                "provider": "anthropic"
            }
            
        except Exception as e:
            logger.error(f"Error calling tool: {str(e)}")
            return {
                "error": str(e),
                "content": "",
                "tool_calls": [],
                "model": model,
                "provider": "anthropic"
            }

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Cleared conversation history")
        
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 for use with the API.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if encoding failed
        """
        if not has_pil:
            logger.error("Cannot encode image: PIL not available")
            return None
            
        try:
            logger.info(f"Encoding image from path: {image_path}")
            with Image.open(image_path) as img:
                # Convert format name to mime type
                format_to_mime = {
                    'PNG': 'image/png',
                    'JPEG': 'image/jpeg',
                    'GIF': 'image/gif',
                    'WEBP': 'image/webp'
                }
                
                if img.format not in format_to_mime:
                    logger.error(f"Unsupported image format: {img.format}. Must be PNG, JPEG, GIF, or WEBP.")
                    return None
                
                # Convert to bytes
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                # Return base64 encoded image data
                encoded_data = base64.b64encode(img_byte_arr).decode('utf-8')
                logger.info(f"Successfully encoded image, length: {len(encoded_data)}")
                return encoded_data
                
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            return None
    
    @staticmethod
    def format_date(date_str: str) -> str:
        """Format a date string in a human-readable format."""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y")
        except Exception:
            return date_str 