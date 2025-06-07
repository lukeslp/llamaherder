#!/usr/bin/env python
import os
import sys
import tempfile
import io
import json
import logging
from typing import Generator, List, Dict, Optional, Union, Any
from datetime import datetime
from base64 import b64encode

# Import base provider class
from api.services.providers.base import BaseProvider

# Configure logging
logger = logging.getLogger(__name__)

# Try to import OpenAI for the X.AI client
try:
    from openai import OpenAI
    has_openai = True
    logger.info("Successfully imported OpenAI library for X.AI interface")
except ImportError:
    has_openai = False
    logger.warning("OpenAI library not available. Install with: pip install openai>=1.0.0")

# Try to import PIL for image processing
try:
    from PIL import Image
    has_pil = True
    logger.info("Successfully imported PIL.Image")
except ImportError:
    has_pil = False
    logger.warning("PIL not available. Image processing will be disabled.")

class XAIProvider(BaseProvider):
    """
    Provider implementation for X.AI (Grok) API.
    Supports chat streaming, vision capabilities, and tool calling.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the X.AI client with the provided API key.
        
        Args:
            api_key: X.AI API key (or use default)
        """
        # Hard-coded API key as requested
        super().__init__(api_key)
        self.api_key = api_key or "ld3Q_RnmV2kz1x04_KbhVg"  # Hard-coded API key for X.AI
        
        # Initialize the client if OpenAI library is available
        self.client = None
        if has_openai:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.x.ai/v1"
                )
                logger.info("Initialized X.AI client")
            except Exception as e:
                logger.error(f"Error initializing X.AI client: {str(e)}")
        
        # Initialize conversation history with system message
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
            }
        ]
    
    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 10,
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve available X.AI models.
        
        Args:
            sort_by: Field to sort by (created/capabilities/id)
            page: Page number for pagination
            page_size: Number of models per page
            capability_filter: Filter by capability
            
        Returns:
            List of available models with their details
        """
        try:
            if not has_openai or not self.client:
                logger.warning("OpenAI library not available, using fallback models")
                return self._get_fallback_models(capability_filter, page, page_size)
            
            # Fetch models from the X.AI API
            response = self.client.models.list()
            
            # Process and format the models
            models = []
            for model in response.data:
                # Extract capabilities from model metadata
                capabilities = []
                if "vision" in model.id or "image" in model.id:
                    capabilities.append("vision")
                capabilities.extend(["text", "function"])  # All models support text and function calls
                
                model_data = {
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
                    "description": f"X.AI {model.id} model",
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "context_length": getattr(model, "context_window", 8192),
                    "created": getattr(model, "created", datetime.now().timestamp()),
                    "created_at": datetime.fromtimestamp(
                        getattr(model, "created", datetime.now().timestamp())
                    ).strftime("%Y-%m-%d"),
                    "owned_by": "xai",
                    "provider": "xai"
                }
                
                # Apply capability filter if specified (but not for alt text generation)
                if capability_filter and capability_filter not in capabilities and "alt_text" not in kwargs.get("purpose", ""):
                    continue
                
                models.append(model_data)
            
            # Sort models
            if sort_by == "created":
                models.sort(key=lambda x: x["created"], reverse=True)
            elif sort_by == "capabilities":
                models.sort(key=lambda x: x["capability_count"], reverse=True)
            else:  # sort by id
                models.sort(key=lambda x: x["id"])
            
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Error fetching X.AI models: {str(e)}")
            return self._get_fallback_models(capability_filter, page, page_size)
    
    def _get_fallback_models(self, capability_filter, page, page_size):
        """Return fallback models when API is unavailable"""
        logger.info("Using fallback models for X.AI")
        fallback_models = [
            {
                "id": "grok-2-latest",
                "name": "Grok 2 Latest",
                "description": "X.AI Grok 2 base model",
                "capabilities": ["text", "function", "vision"],
                "capability_count": 3,
                "context_length": 8192,
                "created": datetime.now().timestamp(),
                "created_at": "2024-02-01",
                "owned_by": "xai",
                "provider": "xai"
            },
            {
                "id": "grok-1",
                "name": "Grok 1",
                "description": "X.AI Grok 1 base model",
                "capabilities": ["text", "function"],
                "capability_count": 2,
                "context_length": 8192,
                "created": datetime(2023, 11, 1).timestamp(),
                "created_at": "2023-11-01",
                "owned_by": "xai",
                "provider": "xai"
            },
            {
                "id": "grok-2-image",
                "name": "Grok 2 Image",
                "description": "X.AI Grok 2 model with image generation capabilities",
                "capabilities": ["text", "function", "vision", "image-generation"],
                "capability_count": 4,
                "context_length": 8192,
                "created": datetime.now().timestamp(),
                "created_at": "2024-03-01",
                "owned_by": "xai",
                "provider": "xai"
            }
        ]
        
        # Apply capability filter if specified
        if capability_filter:
            fallback_models = [m for m in fallback_models if capability_filter in m["capabilities"]]
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return fallback_models[start_idx:end_idx]
    
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image data or None if encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_data = b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image from path: {image_path}")
                return encoded_data
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return None
    
    def process_image(self, file_path: str) -> Optional[str]:
        """
        Process an image for use in multimodal requests.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Encoded image data or None if processing failed
        """
        if not has_pil:
            logger.error("Cannot process image: PIL not available")
            return self.encode_image(file_path)
            
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
                encoded_data = b64encode(img_byte_arr.getvalue()).decode('utf-8')
                logger.info(f"Successfully processed image, format={img_format}, length={len(encoded_data)}")
                return encoded_data
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def create_test_image(self) -> Optional[str]:
        """
        Create a simple test image and return its base64 encoding.
        
        Returns:
            Base64 encoded image data or None if creation fails
        """
        if not has_pil:
            logger.error("Cannot create test image: PIL not available")
            return None
            
        try:
            img = Image.new('RGB', (100, 100), color='red')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            encoded_data = b64encode(img_byte_arr).decode('utf-8')
            logger.info(f"Successfully created test image, length={len(encoded_data)}")
            return encoded_data
        except Exception as e:
            logger.error(f"Error creating test image: {e}")
            return None
    
    def stream_chat_response(
        self,
        prompt: str,
        model: str = "grok-2-latest",
        image_data: Optional[str] = None,
        image_path: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        use_test_image: bool = False,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from X.AI (Grok).
        
        Args:
            prompt: The user's input message
            model: The X.AI model to use
            image_data: Base64 encoded image data
            image_path: Path to an image file
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            use_test_image: Whether to use a test image
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response text as they arrive
        """
        try:
            if not has_openai or not self.client:
                yield {"error": "OpenAI library not available or X.AI client initialization failed."}
                return
            
            # Process image if path is provided
            if image_path and not image_data:
                logger.info(f"Processing image from path: {image_path}")
                image_data = self.process_image(image_path)
                if not image_data:
                    logger.error(f"Failed to process image from path: {image_path}")
            
            # Create test image if requested
            if use_test_image and not image_data:
                logger.info("Creating test image")
                image_data = self.create_test_image()
                if not image_data:
                    logger.error("Failed to create test image")
            
            # Prepare message content
            # Only include image if image_data is provided and not explicitly None
            if image_data and image_data is not None:
                message_content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
                logger.info("Including image data in request")
            else:
                message_content = prompt
                logger.info("No image data included in request")
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message_content
            })
            
            # Make streaming request
            logger.info(f"Sending request to X.AI API with model: {model}")
            if image_data:
                logger.info("Request includes image data")
            
            stream = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
            
            response_text = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    yield {"content": text}  # Yield as dict with content key
            
            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
                    
        except Exception as e:
            logger.error(f"Error in stream_chat_response: {str(e)}")
            # Remove the user message if request failed
            if len(self.conversation_history) > 0 and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            yield {"error": str(e)}  # Yield error as dict with error key
    
    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [self.conversation_history[0]]
        logger.info("Cleared conversation history")
    
    def call_tool(
        self,
        prompt: str,
        model: str,
        tools: List[Dict[str, Any]],
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Use the model to call tools based on the prompt.
        
        Args:
            prompt: The user's message
            model: The model to use
            tools: List of tool definitions
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Dict containing the response and any tool calls
        """
        try:
            if not has_openai or not self.client:
                return {
                    "error": "OpenAI library not available or X.AI client initialization failed.",
                    "content": "Error: X.AI API not available.",
                    "tool_calls": [],
                    "model": model,
                    "provider": "xai"
                }
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API request
            logger.info(f"Calling tools with X.AI model: {model}")
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                max_tokens=max_tokens,
                tools=tools
            )
            
            # Extract content and tool calls
            content = response.choices[0].message.content or ""
            tool_calls = []
            
            # Process tool calls if present
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
            
            # Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls
            })
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "model": model,
                "provider": "xai"
            }
            
        except Exception as e:
            logger.error(f"Error calling tools: {str(e)}")
            return {
                "error": str(e),
                "content": f"Error calling tools: {str(e)}",
                "tool_calls": [],
                "model": model,
                "provider": "xai"
            }

    def generate_image(
        self,
        prompt: str,
        model: str = "grok-2-image",
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        response_format: str = "url",
        **kwargs
    ) -> Dict:
        """
        Generate an image using X.AI's image generation API.
        
        Args:
            prompt: The text prompt to generate the image from
            model: The X.AI model to use
            n: Number of images to generate
            size: Size of the generated image (1024x1024, 1024x1792, 1792x1024)
            quality: Quality of the generated image (standard, hd)
            style: Style of the generated image (vivid, natural)
            response_format: Format of the response (url or b64_json)
            **kwargs: Additional parameters including:
                api_key: Optional API key override
                seed: Optional seed for reproducible generation
                hdr: Optional HDR flag for higher quality images
            
        Returns:
            Dict containing the generated image data or error information
        """
        # Check for API key override in kwargs
        api_key = kwargs.get("api_key", self.api_key)
        
        try:
            # Try to import OpenAI if not already available
            global has_openai
            if not has_openai:
                try:
                    from openai import OpenAI
                    has_openai = True
                    logger.info("Successfully imported OpenAI library for X.AI interface")
                except ImportError:
                    return {"error": "OpenAI library not available. Please install it with: pip install openai>=1.0.0"}
            
            # Create or update client with potentially new API key
            if not self.client or api_key != self.api_key:
                try:
                    self.client = OpenAI(
                        api_key=api_key,
                        base_url="https://api.x.ai/v1"
                    )
                    # Update API key if different
                    if api_key != self.api_key:
                        self.api_key = api_key
                        logger.info("Updated X.AI client with new API key")
                    else:
                        logger.info("Created X.AI client")
                except Exception as e:
                    error_msg = f"Failed to initialize X.AI client: {str(e)}"
                    logger.error(error_msg)
                    return {"error": error_msg}
            
            # Log the request
            logger.info(f"Generating image with X.AI using prompt: {prompt}")
            
            # Validate parameters
            valid_sizes = ["1024x1024", "1024x1792", "1792x1024"]
            if size not in valid_sizes:
                logger.warning(f"Invalid size parameter: {size}. Using default 1024x1024")
                size = "1024x1024"
                
            valid_qualities = ["standard", "hd"]
            if quality not in valid_qualities:
                logger.warning(f"Invalid quality parameter: {quality}. Using default standard")
                quality = "standard"
                
            valid_styles = ["vivid", "natural"]
            if style not in valid_styles:
                logger.warning(f"Invalid style parameter: {style}. Using default vivid")
                style = "vivid"
            
            # Prepare request parameters
            request_params = {
                "model": model,
                "prompt": prompt,
                "n": n,
                "response_format": response_format
            }
            
            # Add optional parameters if provided
            if "seed" in kwargs and isinstance(kwargs["seed"], int):
                request_params["seed"] = kwargs["seed"]
                
            if "hdr" in kwargs and isinstance(kwargs["hdr"], bool):
                request_params["hdr"] = kwargs["hdr"]
                
            # Make the API request
            # X.AI uses a similar API structure to OpenAI
            try:
                response = self.client.images.generate(**request_params)
            except Exception as api_e:
                error_msg = f"X.AI API error: {str(api_e)}"
                logger.error(error_msg)
                # Check for common error types
                if "authentication" in str(api_e).lower() or "auth" in str(api_e).lower():
                    return {"error": "Authentication failed. Please check your X.AI API key."}
                elif "rate limit" in str(api_e).lower():
                    return {"error": "Rate limit exceeded. Please try again later."}
                else:
                    return {"error": error_msg}
            
            # Process response
            result = {
                "created": int(datetime.now().timestamp()),
                "data": [],
                "model": model
            }
            
            # Extract image data
            for img_data in response.data:
                img_info = {}
                if hasattr(img_data, "url") and img_data.url:
                    img_info["url"] = img_data.url
                if hasattr(img_data, "b64_json") and img_data.b64_json:
                    img_info["b64_json"] = img_data.b64_json
                if hasattr(img_data, "revised_prompt") and img_data.revised_prompt:
                    img_info["revised_prompt"] = img_data.revised_prompt
                
                result["data"].append(img_info)
            
            # Return error if no image data was generated
            if not result["data"]:
                return {"error": "No image data was generated by X.AI"}
                
            return result
            
        except Exception as e:
            error_msg = f"Error generating image with X.AI: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg} 