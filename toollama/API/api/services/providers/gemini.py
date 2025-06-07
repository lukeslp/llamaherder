#!/usr/bin/env python
import logging
import os
from typing import Generator, List, Dict, Any, Optional, Union
from datetime import datetime
import google.generativeai as genai
from api.services.providers.base import BaseProvider
import base64
from PIL import Image
import io

# Logger for this module
logger = logging.getLogger(__name__)

class GeminiProvider(BaseProvider):
    """
    Provider implementation for Google's Gemini API.
    Supports chat streaming and vision capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Gemini API key (optional, will use environment variable if not provided)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Gemini provider")
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # Hard code the API key from the curl example
            self.api_key = "AIzaSyAXLsdBC6qYhW9djaep-gCWQasszLHfi8U"
            self.logger.info("Using hard-coded API key")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize chat history
        self.chat_history = []
        
        # Initialize available models
        self.models = {
            "gemini-2.0-flash": {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "description": "Fast and efficient Gemini model",
                "capabilities": ["text", "function"],
                "capability_count": 2,
                "context_length": 32768,
                "created": datetime.now().timestamp(),
                "created_at": "2024-02-01",
                "owned_by": "google",
                "provider": "gemini"
            },
            "gemini-1.5-pro": {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "description": "Advanced Gemini model with vision capabilities",
                "capabilities": ["text", "vision", "function"],
                "capability_count": 3,
                "context_length": 128000,
                "created": datetime(2024, 2, 1).timestamp(),
                "created_at": "2024-02-01",
                "owned_by": "google",
                "provider": "gemini"
            },
            "gemini-2.0-flash-exp": {
                "id": "gemini-2.0-flash-exp",
                "name": "Gemini 2.0 Flash Experimental",
                "description": "Experimental Gemini model with advanced capabilities",
                "capabilities": ["text", "vision", "function"],
                "capability_count": 3,
                "context_length": 32768,
                "created": datetime.now().timestamp(),
                "created_at": "2024-03-12",
                "owned_by": "google",
                "provider": "gemini"
            },
            "gemini-2.0-flash-exp-image-generation": {
                "id": "gemini-2.0-flash-exp-image-generation",
                "name": "Gemini 2.0 Flash Experimental Image Generation",
                "description": "Experimental Gemini model with image generation capability",
                "capabilities": ["text", "vision", "function", "image"],
                "capability_count": 4,
                "context_length": 32768,
                "created": datetime.now().timestamp(),
                "created_at": "2024-03-12",
                "owned_by": "google",
                "provider": "gemini"
            }
        }
    
    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 10,
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        List available Gemini models.
        
        Args:
            sort_by: Field to sort by (created/capabilities/id)
            page: Page number for pagination
            page_size: Number of models per page
            capability_filter: Filter by capability
            
        Returns:
            List of available models with their details
        """
        models_list = [
            {
                "id": info["id"],
                "name": info["name"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "capability_count": info["capability_count"],
                "context_length": info["context_length"],
                "created": info["created"],
                "created_at": info["created_at"],
                "owned_by": info["owned_by"],
                "provider": "gemini"
            }
            for info in self.models.values()
        ]
        
        # Apply capability filter if specified
        if capability_filter:
            models_list = [m for m in models_list if capability_filter in m["capabilities"]]
        
        # Sort models
        if sort_by == "created":
            models_list.sort(key=lambda x: x["created"], reverse=True)
        elif sort_by == "capabilities":
            models_list.sort(key=lambda x: x["capability_count"], reverse=True)
        else:
            models_list.sort(key=lambda x: x["id"])
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return models_list[start_idx:end_idx]
    
    def stream_chat_response(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        image_data: Optional[Union[str, List[str]]] = None,
        image_path: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Gemini.
        
        Args:
            prompt: The user's input message
            model: The Gemini model to use
            max_tokens: Maximum tokens to generate
            temperature: Response temperature (0.0 to 1.0)
            image_data: Base64 encoded image data
            image_path: Path to an image file
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the response text as they arrive
        """
        try:
            # Get the appropriate model
            model_id = self.models[model]["id"] if model in self.models else model
            
            # Create model instance
            genai_model = genai.GenerativeModel(model_id)
            
            # Prepare contents list
            contents = [{"role": "user", "parts": [{"text": prompt}]}]
            
            # Add image if provided
            if image_data or image_path:
                if image_path:
                    image_data = self.process_image(image_path)
                
                if image_data:
                    # For the first message only, add image
                    if len(self.chat_history) == 0:
                        contents[0]["parts"].append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        })
            
            # Set generation parameters
            generation_config = {
                "max_output_tokens": max_tokens,
                # "temperature": temperature
            }
            
            # Include history if available
            if self.chat_history:
                # Stream with history
                response = genai_model.generate_content(
                    contents=contents,
                    generation_config=generation_config,
                    stream=True
                )
            else:
                # Stream without history 
                response = genai_model.generate_content(
                    contents=contents,
                    generation_config=generation_config,
                    stream=True
                )
            
            # Process streamed response
            response_text = ""
            for chunk in response:
                if hasattr(chunk, 'text') and chunk.text:
                    response_text += chunk.text
                    yield {"content": chunk.text}  # Yield as dict with content key
                elif hasattr(chunk, 'parts'):
                    for part in chunk.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text
                            yield {"content": part.text}  # Yield as dict with content key
            
            # Update chat history with the complete exchange
            self.chat_history.extend([
                {"role": "user", "parts": [{"text": prompt}]},
                {"role": "model", "parts": [{"text": response_text}]}
            ])
            
        except Exception as e:
            self.logger.error(f"Error in stream_chat_response: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            yield {"error": str(e)}  # Yield error as dict with error key
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.chat_history = []
        self.logger.info("Cleared conversation history")
    
    def generate_image(
        self,
        prompt: str,
        model: str = "gemini-2.0-flash-exp-image-generation",
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        response_format: str = "url",
        **kwargs
    ) -> Dict:
        """
        Generate an image using Gemini's experimental image generation capability.
        
        Args:
            prompt: The text prompt to generate the image from
            model: The Gemini model to use (must be gemini-2.0-flash-exp-image-generation)
            n: Number of images to generate
            size: Size of the generated image
            quality: Quality of the generated image
            style: Style of the generated image
            response_format: Format of the response (url or b64_json)
            **kwargs: Additional parameters including:
                api_key: Optional API key override
            
        Returns:
            Dict containing the generated image data or error information
        """
        # Check for API key override in kwargs
        api_key = kwargs.get("api_key")
        if api_key and api_key != self.api_key:
            self.logger.info("Using provided API key for image generation")
            # Temporarily update our API key configuration
            old_api_key = self.api_key
            self.api_key = api_key
            # Configure the client with the new API key
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
            except Exception as e:
                self.logger.error(f"Error configuring Google Generative AI with new API key: {str(e)}")
                return {"error": f"Failed to configure Gemini with provided API key: {str(e)}"}
        
        try:
            # Check if genai is available
            try:
                import google.generativeai as genai
            except ImportError:
                return {"error": "Google Generative AI library not installed. Please install with: pip install google-generativeai"}
            
            self.logger.info(f"Generating image with prompt: {prompt}")
            
            # Create model instance
            try:
                genai_model = genai.GenerativeModel(model)
            except Exception as e:
                self.logger.error(f"Error creating Gemini model instance: {str(e)}")
                return {"error": f"Failed to create Gemini model instance: {str(e)}"}
            
            # Prepare the prompt to explicitly ask for image generation
            enhanced_prompt = f"Generate an image of {prompt}. Make it high quality and visually appealing."
            
            # Generate content with image using direct dictionary for generation_config
            try:
                response = genai_model.generate_content(
                    contents=enhanced_prompt,
                    generation_config={
                        # Use the response_modalities parameter with correct case
                        "response_modalities": ["TEXT", "IMAGE"]
                    }
                )
            except Exception as e:
                self.logger.error(f"Error during Gemini image generation API call: {str(e)}")
                error_msg = str(e).lower()
                # Check for common error types
                if "permission" in error_msg or "quota" in error_msg:
                    return {"error": "Permission denied or quota exceeded. Please check your API key and usage limits."}
                elif "rate limit" in error_msg:
                    return {"error": "Rate limit exceeded. Please try again later."}
                else:
                    return {"error": f"Gemini API error: {str(e)}"}
            
            # Extract image data from response
            image_data = []
            self.logger.info(f"Response received from Gemini")
            
            # Check if candidates are available
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        parts = getattr(candidate.content, 'parts', [])
                        for part in parts:
                            # Check for inline_data
                            if hasattr(part, 'inline_data') and part.inline_data:
                                mime_type = getattr(part.inline_data, 'mime_type', '')
                                if 'image' in mime_type:
                                    data = getattr(part.inline_data, 'data', b'')
                                    if data:
                                        import base64
                                        # Convert bytes to base64 string if needed
                                        if isinstance(data, bytes):
                                            data = base64.b64encode(data).decode('utf-8')
                                        
                                        image_data.append({
                                            "url": f"data:{mime_type};base64,{data}",
                                            "format": response_format
                                        })
            
            # If image data was found in candidates, return it
            if image_data:
                self.logger.info(f"Successfully generated {len(image_data)} images")
                return {
                    "created": datetime.now().timestamp(),
                    "data": image_data[:n],
                    "model": model
                }
            
            # Try alternative approach if we didn't get image data from candidates
            for part in getattr(response, 'parts', []):
                if hasattr(part, 'is_image') and part.is_image:
                    image_url = getattr(part.image, 'url', None)
                    image_base64 = getattr(part.image, 'base64', None)
                    
                    if image_url or image_base64:
                        image_data.append({
                            "url": image_url if response_format == "url" and image_url else f"data:image/jpeg;base64,{image_base64}",
                            "format": response_format
                        })
            
            # Check if we got any image data
            if image_data:
                return {
                    "created": datetime.now().timestamp(),
                    "data": image_data[:n],
                    "model": model
                }
            else:
                self.logger.error("No image data returned from Gemini API")
                return {"error": "No image data returned from Gemini API"}
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {"error": str(e)}
        finally:
            # Restore original API key if we temporarily changed it
            if api_key and api_key != self.api_key and 'old_api_key' in locals():
                self.api_key = old_api_key
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.api_key)
                except Exception:
                    self.logger.warning("Failed to restore original API key configuration")

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
            # Create model instance
            genai_model = genai.GenerativeModel(model)
            
            # Configure tool calling using direct dictionary
            generation_config = {
                "tools": tools
            }
            
            # Generate response with tool calling
            response = genai_model.generate_content(
                contents=prompt,
                generation_config=generation_config
            )
            
            # Extract tool calls from response
            tool_calls = []
            
            # Check if candidates are available
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and candidate.content:
                        parts = getattr(candidate.content, 'parts', [])
                        for part in parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                tool_calls.append({
                                    "name": getattr(part.function_call, 'name', ''),
                                    "arguments": getattr(part.function_call, 'args', {})
                                })
            
            # Try alternative approach if we didn't get tool calls from candidates
            if not tool_calls and hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        tool_calls.append({
                            "name": getattr(part.function_call, 'name', ''),
                            "arguments": getattr(part.function_call, 'args', {})
                        })
            
            # Get response text
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text
            
            return {
                "content": response_text,
                "tool_calls": tool_calls,
                "model": model,
                "provider": "gemini"
            }
            
        except Exception as e:
            self.logger.error(f"Error calling tools: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "content": f"Error calling tools: {str(e)}",
                "tool_calls": [],
                "model": model,
                "provider": "gemini"
            }

    def process_image(self, file_path: str) -> Optional[str]:
        """
        Process an image for use in multimodal requests.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Encoded image data or None if processing failed
        """
        try:
            self.logger.info(f"Processing image from path: {file_path}")
            
            # Check if the file exists
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
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
                    self.logger.error(f"Unsupported image format: {img_format}.")
                    return None
                    
                if img_format == 'GIF' and getattr(img, 'is_animated', False):
                    self.logger.error("Animated GIFs are not supported.")
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
                    self.logger.error("Image file size exceeds 10MB limit.")
                    return None
                
                # Encode to base64
                encoded_data = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                self.logger.info(f"Successfully processed image, format={img_format}, length={len(encoded_data)}")
                return encoded_data
                
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None

    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 for use with the API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image data or None if encoding failed
        """
        return self.process_image(image_path) 