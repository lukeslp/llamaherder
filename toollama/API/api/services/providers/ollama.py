#!/usr/bin/env python
import os
import sys
import tempfile
import io
import json
import requests
import logging
from typing import Generator, List, Dict, Optional, Union, Any
from datetime import datetime
from base64 import b64encode

# Import base provider class
from api.services.providers.base import BaseProvider
from api.config import OLLAMA_HOST

# Configure logging
logger = logging.getLogger(__name__)

# Try to import PIL for image processing
try:
    from PIL import Image
    has_pil = True
    logger.info("Successfully imported PIL.Image")
except ImportError:
    has_pil = False
    logger.warning("PIL not available. Image processing will be disabled.")

class OllamaProvider(BaseProvider):
    """
    Provider implementation for Ollama API.
    Supports chat streaming, vision capabilities, and local model management.
    """
    def __init__(self, api_key: str = None):
        """
        Initialize the Ollama client with the host URL.
        Ollama doesn't require an API key, but we accept it for compatibility.
        
        Args:
            api_key: Not used for Ollama, but required by BaseProvider
        """
        super().__init__(api_key)
        self.host = OLLAMA_HOST
        self.conversation_history = []
        logger.info(f"Initialized Ollama Provider with host: {self.host}")
        
    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get available Ollama models with sorting and pagination.
        
        Args:
            sort_by (str): Field to sort by ('created', 'name', 'family', 'size')
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter by capability ('vision', 'text', etc)
                Note: For alt text generation, we don't filter by capability
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Get list of models
            response = requests.get(f"{self.host}/api/tags")
            if not response.ok:
                logger.error(f"Failed to fetch models: {response.text}")
                return []
            
            models_data = response.json().get('models', [])
            processed_models = []
            
            # Process each model
            for model in models_data:
                try:
                    # Get detailed model info
                    details_response = requests.post(
                        f"{self.host}/api/show",
                        json={"name": model['name']}
                    )
                    if not details_response.ok:
                        continue
                        
                    details = details_response.json()
                    model_details = details.get('details', {})
                    
                    # Determine capabilities based on families
                    capabilities = ["text"]  # All models support text
                    families = model_details.get('families', [])
                    if "clip" in families:
                        capabilities.append("vision")
                    
                    # Don't filter out models for alt text generation
                    # Only filter if requested AND not for alt text generation
                    if capability_filter and capability_filter not in capabilities and "alt_text" not in kwargs.get("purpose", ""):
                        continue
                    
                    # Create enhanced model info
                    model_info = {
                        "id": model['name'],
                        "name": model['name'],
                        "description": f"Ollama {model_details.get('family', '').upper()} model - {model_details.get('parameter_size', 'Unknown')} parameters",
                        "capabilities": capabilities,
                        "capability_count": len(capabilities),
                        "created": model.get('modified_at', ""),
                        "created_at": datetime.fromisoformat(model.get('modified_at', "").replace('Z', '+00:00')).strftime("%Y-%m-%d"),
                        "family": model_details.get('family', ''),
                        "parameter_size": model_details.get('parameter_size', ''),
                        "quantization": model_details.get('quantization_level', ''),
                        "format": model_details.get('format', ''),
                        "owned_by": "ollama",
                        "provider": "ollama"
                    }
                    processed_models.append(model_info)
                except Exception as e:
                    logger.error(f"Error processing model {model['name']}: {e}")
                    continue
            
            # Sort models
            if sort_by == "created":
                processed_models.sort(key=lambda x: x["created"], reverse=True)
            elif sort_by == "family":
                processed_models.sort(key=lambda x: x["family"], reverse=True)
            elif sort_by == "size":
                processed_models.sort(key=lambda x: x["parameter_size"], reverse=True)
            elif sort_by == "capabilities":
                processed_models.sort(key=lambda x: x["capability_count"], reverse=True)
            else:  # sort by name
                processed_models.sort(key=lambda x: x["name"], reverse=True)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            logger.info(f"Retrieved {len(processed_models)} models from Ollama")
            return processed_models[start_idx:end_idx]
            
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []

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
                encoded_data = b64encode(image_file.read()).decode('utf-8')
                logger.info(f"Successfully encoded image from path: {image_path}")
                return encoded_data
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
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

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.
        
        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)
            
        Returns:
            Optional[str]: Base64 encoded image data or None if creation fails
        """
        if not has_pil:
            logger.error("Cannot create test image: PIL not available")
            return None
            
        try:
            img = Image.new('RGB', size, color=color)
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
        model: str = "llava",
        image_data: Optional[str] = None,
        image_path: Optional[str] = None,
        max_tokens: int = -1,
        temperature: float = 0.7,
        use_test_image: bool = False,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Ollama.
        
        Args:
            prompt (str): The user's input message
            model (str): The Ollama model to use (any model can be used, even if not a vision model)
            image_data (Optional[str]): Base64 encoded image data
            image_path (Optional[str]): Path to an image file
            max_tokens (int): Maximum tokens to generate (default: -1 for model default)
            temperature (float): Response temperature (0.0 to 1.0)
            use_test_image (bool): Whether to use a test image
            **kwargs: Additional parameters
            
        Yields:
            str: Chunks of the response text as they arrive
            
        Note:
            Any model can be used with images for alt text generation. The model does not 
            need to have vision capabilities. If a non-vision model is used with an image, 
            it may ignore the image content, but the request will still be processed rather 
            than falling back to a different model.
        """
        try:
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
            
            # Prepare the request data
            data = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": -1  # Always use -1 to let the model determine the appropriate length
                }
            }
            
            # Log that we're using num_predict = -1
            logger.info("Using num_predict = -1 to let the model determine the appropriate response length")
            
            # Add image if provided
            if image_data:
                logger.info(f"Adding image data to request, length={len(image_data)}")
                data["images"] = [image_data]
            
            # Make streaming request
            logger.info(f"Sending request to Ollama API with model: {model}")
            response = requests.post(
                f"{self.host}/api/generate",
                json=data,
                stream=True
            )
            
            if not response.ok:
                error_msg = f"API request failed: {response.text}"
                logger.error(error_msg)
                yield f"Error: {error_msg}"
                return
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error in stream_chat_response: {e}")
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Cleared conversation history")

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
        try:
            # Ollama doesn't have native tool calling, so we'll format the tools as part of the prompt
            tools_str = json.dumps(tools, indent=2)
            enhanced_prompt = f"{prompt}\n\nAvailable tools:\n{tools_str}\n\nPlease use these tools to respond to the user's request."
            
            # Always use num_predict = -1 to let the model determine the appropriate length
            logger.info("Using num_predict = -1 for tool calling")
            
            # Stream the response
            full_response = ""
            for chunk in self.stream_chat_response(
                enhanced_prompt, 
                model=model,
                max_tokens=-1  # Always use -1
            ):
                full_response += chunk
                
            # Return a response without actual tool calls
            # In a real implementation, we would parse the response to extract tool calls
            return {
                "content": full_response,
                "tool_calls": [],
                "model": model,
                "provider": "ollama"
            }
            
        except Exception as e:
            logger.error(f"Error calling tools: {e}")
            return {
                "error": str(e),
                "content": f"Error calling tools: {str(e)}",
                "tool_calls": [],
                "model": model,
                "provider": "ollama"
            } 