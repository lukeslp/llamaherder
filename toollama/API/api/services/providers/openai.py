#!/usr/bin/env python
import base64
import io
import os
import sys
import logging
import tempfile
import mimetypes
import time
from datetime import datetime
from typing import Dict, Generator, List, Optional, Union
import uuid

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logging.warning("PIL not found. Image processing features will be unavailable.")

# Patched import to avoid proxy issues with OpenAI library
OpenAI = None
HAS_OPENAI = False
try:
    # Direct import to handle any errors
    from openai import OpenAI
    HAS_OPENAI = True
    logging.info("Successfully imported OpenAI library")
except ImportError as e:
    logging.warning(f"OpenAI library not found: {e}. Install with: pip install openai")

from .base import BaseProvider

# Initialize mimetypes
mimetypes.init()

def convert_to_bool(value):
    """Convert a value to boolean, supporting both string and boolean inputs."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)

class OpenAIProvider(BaseProvider):
    """
    OpenAI provider for the Camina Chat API.
    Provides access to GPT models including vision capabilities.
    """
    
    # Default models in case API fetch fails
    DEFAULT_MODELS = {
        "gpt-4o-2024-11-20": {
            "id": "gpt-4o-2024-11-20",
            "name": "GPT-4 Omega (gpt-4o-2024-11-20)",
            "context_length": 128000,
            "description": "GPT-4 Omega model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created_str": "2024-11-20",
            "owned_by": "OpenAI"
        },
        "gpt-4-vision-preview": {
            "id": "gpt-4-vision-preview",
            "name": "GPT-4 Vision (gpt-4-vision-preview)",
            "context_length": 128000,
            "description": "GPT-4 model with vision capabilities",
            "capabilities": ["text", "vision", "function"],
            "capability_count": 3,
            "created_str": "2023-10-30",
            "owned_by": "OpenAI"
        },
        "gpt-4-0125-preview": {
            "id": "gpt-4-0125-preview",
            "name": "GPT-4 Turbo (gpt-4-0125-preview)",
            "context_length": 128000,
            "description": "GPT-4 preview model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created_str": "2024-01-25",
            "owned_by": "OpenAI"
        },
        "gpt-4": {
            "id": "gpt-4",
            "name": "GPT-4 (gpt-4)",
            "context_length": 8192,
            "description": "GPT-4 base model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created_str": "2023-03-15",
            "owned_by": "OpenAI"
        },
        "gpt-3.5-turbo-0125": {
            "id": "gpt-3.5-turbo-0125",
            "name": "GPT-3.5 Turbo (gpt-3.5-turbo-0125)",
            "context_length": 16385,
            "description": "GPT-3.5 Turbo model",
            "capabilities": ["text", "function"],
            "capability_count": 2,
            "created_str": "2024-01-25",
            "owned_by": "OpenAI"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (optional, will use environment variable if not provided)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing OpenAI provider")
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Hard-coded API key as fallback
            self.api_key = "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"
            self.logger.info("Using hard-coded API key")
            
        # Always initialize with default models first
        self.models = self.DEFAULT_MODELS
        self.client = None
            
        if not HAS_OPENAI:
            self.logger.warning("OpenAI library not available. Using fallback models only.")
        else:
            self.logger.info("Initializing OpenAI client with API key")
            try:
                # Using global OpenAI instance to avoid scope issues
                global OpenAI
                
                # Check if the API key looks valid (basic format check)
                if not self.api_key or not (self.api_key.startswith('sk-') and len(self.api_key) > 20):
                    self.logger.warning("API key appears to be invalid or malformed")
                
                # Create the client with our API key
                self.client = OpenAI(api_key=self.api_key)
                
                # Test the client with a simple API call
                try:
                    # Just fetch one model to test connectivity
                    self.client.models.retrieve("gpt-3.5-turbo")
                    self.logger.info("Successfully validated OpenAI client connection")
                    
                    # Now fetch all models
                    models = self._fetch_models()
                    if models:
                        self.models = models
                        self.logger.info(f"Fetched {len(self.models)} models from OpenAI API")
                    else:
                        self.logger.warning("No models fetched from OpenAI API, using defaults")
                except Exception as e:
                    self.logger.warning(f"API test call failed, but client was created: {str(e)}")
                    # We'll keep the client initialized anyway, as some endpoints might still work
            except Exception as e:
                self.logger.error(f"Error initializing OpenAI client: {str(e)}")
                self.client = None
        
        # Initialize conversation history
        self.clear_conversation()
    
    def _fetch_models(self) -> Dict:
        """
        Fetch available models from OpenAI API.
        
        Returns:
            Dict: Dictionary of available models with their details
        """
        try:
            if not self.client or not HAS_OPENAI:
                self.logger.info("Using default models because OpenAI client is not available")
                return self.DEFAULT_MODELS
            
            models = {}
            response = self.client.models.list()
            
            # Process all models without filtering
            for model in response.data:
                model_id = model.id
                created = datetime.fromtimestamp(model.created)
                
                # Default capabilities - assume text capability for all models
                capabilities = ["text"]
                
                # Determine capabilities based on model ID
                if "vision" in model_id.lower():
                    capabilities.append("vision")
                
                # Most chat models support function calling except for these types
                if not any(x in model_id.lower() for x in ["instruct", "base", "embedding"]):
                    capabilities.append("function")
                
                # Handle audio models
                if "audio" in model_id.lower() or "whisper" in model_id.lower() or "tts" in model_id.lower():
                    if "audio" not in capabilities:
                        capabilities.append("audio")
                
                # Determine context length
                context_length = 8192  # Default
                if "32k" in model_id:
                    context_length = 32768
                elif "16k" in model_id:
                    context_length = 16385
                elif "128k" in model_id or "vision" in model_id or "o" in model_id:
                    context_length = 128000
                
                # Set name to just the model ID as requested by user
                name = model_id
                
                # Create model description based on type
                if "o1" in model_id:
                    description = "GPT-O1 model"
                elif "o3" in model_id:
                    description = "GPT-O3 model"
                elif "o2" in model_id:
                    description = "GPT-O2 model"
                elif "4o" in model_id:
                    description = "GPT-4 Omega model"
                elif "4-vision" in model_id:
                    description = "GPT-4 model with vision capabilities"
                elif "4-0125" in model_id:
                    description = "GPT-4 Turbo preview model"
                elif "4" in model_id:
                    description = "GPT-4 base model"
                elif "3.5" in model_id:
                    description = "GPT-3.5 Turbo model"
                elif "whisper" in model_id:
                    description = "Whisper speech-to-text model"
                elif "tts" in model_id:
                    description = "Text-to-speech model"
                elif "embedding" in model_id:
                    description = "Embedding model"
                elif "dall-e" in model_id:
                    description = "DALL-E image generation model"
                    capabilities = ["image-generation"]
                else:
                    description = f"OpenAI {model_id} model"
                
                # Add additional capability descriptions
                if "vision" in model_id:
                    description += " with vision capabilities"
                elif "32k" in model_id:
                    description += " with 32k context"
                elif "16k" in model_id:
                    description += " with 16k context"
                
                # Determine model generation for categorization
                generation = "other"
                if "4" in model_id:
                    generation = "4"
                elif "3.5" in model_id:
                    generation = "3.5"
                elif "3" in model_id:
                    generation = "3"
                elif "o1" in model_id:
                    generation = "o1"
                elif "o2" in model_id:
                    generation = "o2"
                elif "o3" in model_id:
                    generation = "o3"
                
                version = "preview" if "preview" in model_id else model_id.split('-')[-1] if '-' in model_id else None
                
                models[model_id] = {
                    "id": model_id,
                    "name": name,
                    "context_length": context_length,
                    "description": description,
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": created,
                    "created_str": created.strftime("%Y-%m-%d"),
                    "generation": generation,
                    "version": version,
                    "owned_by": model.owned_by,
                    "provider": "openai"
                }
            
            self.logger.info(f"Fetched {len(models)} models from OpenAI API")
            return models if models else self.DEFAULT_MODELS
            
        except Exception as e:
            self.logger.error(f"Error fetching models: {str(e)}")
            return self.DEFAULT_MODELS
    
    def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        generation: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Get available OpenAI models with sorting and pagination.
        
        Args:
            sort_by: Field to sort by ('created', 'context_length', 'id', 'capabilities')
            reverse: Whether to reverse sort order
            page: Page number (1-based)
            page_size: Number of items per page
            generation: Filter by model generation ('4', '3.5', '3')
            
        Returns:
            List of available models with their details
        """
        models_list = [
            {
                "id": info["id"],
                "name": info["name"],
                "context_length": info["context_length"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "capability_count": info["capability_count"],
                "created": info.get("created_str", ""),
                "created_at": info.get("created_str", ""),
                "owned_by": info.get("owned_by", "OpenAI"),
                "provider": "openai"
            }
            for model_id, info in self.models.items()
            if not generation or info["generation"] == generation
        ]
        
        if sort_by == "created":
            # Sort by created_at or created_str date
            models_list.sort(key=lambda x: x.get("created_at", x.get("created", "")), reverse=reverse)
        elif sort_by == "context_length":
            models_list.sort(key=lambda x: x["context_length"], reverse=reverse)
        elif sort_by == "capabilities":
            models_list.sort(key=lambda x: (
                x["capability_count"],
                "vision" in x["capabilities"],
                "text" in x["capabilities"]
            ), reverse=reverse)
        else:
            models_list.sort(key=lambda x: x["id"], reverse=reverse)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return models_list[start_idx:end_idx]
    
    def _get_mime_type(self, file_path: str) -> str:
        """
        Determine the MIME type of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type of the file
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Default to application/octet-stream if type can't be determined
            mime_type = "application/octet-stream"
        self.logger.info(f"Detected MIME type {mime_type} for file {file_path}")
        return mime_type
    
    def process_file(self, file_path: str) -> Optional[Dict]:
        """
        Process any file type and prepare it for API submission.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Formatted file data for API or None if processing failed
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return None
                
            mime_type = self._get_mime_type(file_path)
            
            # Check if it's a PDF - these need special handling via Files API
            if mime_type == "application/pdf":
                self.logger.info(f"PDF file detected: {file_path}. This requires special handling via Files API.")
                return {
                    "type": "pdf",
                    "path": file_path,
                    "mime_type": mime_type
                }
            
            # Check if it's an image file that should be processed with PIL
            if mime_type.startswith('image/') and HAS_PIL:
                return self.process_image(file_path)
            
            # For non-image files or if PIL is not available
            with open(file_path, "rb") as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
                
            self.logger.info(f"Successfully processed file {file_path}, data length: {len(file_data)}")
            
            return {
                "type": "file",
                "file_data": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": file_data
                }
            }
        except Exception as e:
            self.logger.error(f"Error processing file: {e}")
            return None
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to OpenAI's file storage and return the file ID.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            str: The file ID if successful, None otherwise
        """
        try:
            if not self.client:
                self.logger.error("OpenAI client not initialized")
                return None
                
            with open(file_path, "rb") as file:
                response = self.client.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            file_id = response.id
            self.logger.info(f"Successfully uploaded file to OpenAI: {file_id}")
            return file_id
        except Exception as e:
            self.logger.error(f"Error uploading file to OpenAI: {e}")
            return None
    
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image data or None if encoding fails
        """
        try:
            self.logger.info(f"Processing image from path: {image_path}")
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                self.logger.info(f"Successfully processed image from path, data length: {len(encoded)}")
                return encoded
        except Exception as e:
            self.logger.error(f"Error encoding image: {str(e)}")
            return None
    
    def process_image(self, file_path: str) -> Optional[Dict]:
        """
        Process an image for use in multimodal requests.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Formatted image data for API or None if processing failed
        """
        try:
            self.logger.info(f"Processing image from path: {file_path}")
            encoded_image = self.encode_image(file_path)
            if not encoded_image:
                return None
                
            mime_type = self._get_mime_type(file_path)
            
            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{encoded_image}"
                }
            }
        except Exception as e:
            self.logger.error(f"Error processing image: {e}")
            return None
    
    def format_message_with_attachments(
        self,
        message: str,
        attachments: Optional[List[Dict]] = None,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """
        Format a message with optional attachments for the API.
        
        Args:
            message: The text message
            attachments: List of formatted attachments (files, images, etc.)
            image_data: Legacy support for base64 encoded image data or image URLs
            is_url: Whether image_data contains URLs
            
        Returns:
            Formatted message with attachments
        """
        content = [{"type": "text", "text": message}]
        
        # Add attachments if provided
        if attachments:
            content.extend(attachments)
            self.logger.info(f"Added {len(attachments)} attachments to message")
        
        # Legacy support for image_data
        if image_data:
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
            
            self.logger.info(f"Added {len(image_data)} images via legacy image_data parameter")
        
        return content
    
    def stream_chat_response(
        self,
        message: str,
        model: str = "gpt-3.5-turbo-0125",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        image_data: Optional[Union[str, List[str]]] = None,
        image_path: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        is_url: bool = False,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from OpenAI.
        
        Args:
            message: The user's input message
            model: The OpenAI model to use
            max_tokens: Maximum tokens to generate
            temperature: Response temperature (0.0 to 1.0)
            image_data: Image data or URLs (legacy support)
            image_path: Path to an image file (legacy support)
            file_paths: List of paths to files to attach
            is_url: Whether image_data contains URLs
            
        Yields:
            Chunks of the response text as they arrive
        """
        try:
            if not HAS_OPENAI:
                self.logger.error("OpenAI library not installed")
                yield "Error: OpenAI library not installed. Please install with: pip install openai"
                return
                
            if not self.client:
                self.logger.error("OpenAI client not initialized")
                yield f"Error: OpenAI client not initialized. Model {model} is unavailable."
                return
            
            # Process attachments
            attachments = []
            
            # Process image if path is provided (legacy)
            if image_path and not image_data:
                image_attachment = self.process_image(image_path)
                if image_attachment:
                    attachments.append(image_attachment)
                    self.logger.info("Successfully added image from path")
                else:
                    yield f"Error: Failed to process image from {image_path}"
                    return
            
            # Process files if paths are provided - ONLY HANDLE IMAGES FOR THIS ENDPOINT
            if file_paths:
                for file_path in file_paths:
                    # Skip PDF files
                    mime_type = self._get_mime_type(file_path)
                    if mime_type == "application/pdf":
                        self.logger.info(f"Skipping PDF file in chat endpoint: {file_path}. Please use /responses endpoint for PDF processing.")
                        continue

                    # Process image files only
                    if mime_type.startswith('image/'):
                        file_attachment = self.process_image(file_path)
                        if file_attachment:
                            attachments.append(file_attachment)
                            self.logger.info(f"Successfully added image from path: {file_path}")
                        else:
                            yield f"Error: Failed to process image from {file_path}"
                            return
                    else:
                        self.logger.info(f"Skipping non-image file: {file_path}. Please use /responses endpoint for document processing.")
            
            content = self.format_message_with_attachments(message, attachments, image_data, is_url)
            
            self.chat_history.append({
                "role": "user",
                "content": content
            })
            
            messages = []
            for msg in self.chat_history:
                if isinstance(msg["content"], list):
                    messages.append(msg)
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            model_id = self.models[model]["id"] if model in self.models else model
            
            self.logger.info(f"Sending request to OpenAI API with model: {model_id}")
            if attachments:
                self.logger.info(f"Request includes {len(attachments)} attachments")
            
            # Create streaming completion
            stream_args = {
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }
                
            stream = self.client.chat.completions.create(**stream_args)
            
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield text  # Yield plain text directly
            
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            self.logger.error(f"Error in stream_chat_response: {str(e)}")
            if len(self.chat_history) > 0 and self.chat_history[-1]["role"] == "user":
                self.chat_history.pop()
            yield f"Error: {str(e)}\nPlease check your API key and network connection."
    
    def create_response(
        self,
        document_paths: List[str],
        prompt: str,
        model: str = "gpt-4o-2024-11-20",
        temperature: float = 0.7,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        web_search: bool = False,
        file_search: bool = False,
        computer_use: bool = False,
        debug_mode: bool = False,
        tool_choice: str = "auto",
        **kwargs
    ) -> Union[Dict, Generator[str, None, None]]:
        """
        Create a response from the OpenAI Responses API.
        
        Args:
            document_paths: List of paths to documents (PDFs, text files, etc.)
            prompt: The user's prompt
            model: The OpenAI model to use
            temperature: Response temperature (0.0 to 1.0)
            stream: Whether to stream the response
            tools: List of tool definitions for function calling
            web_search: Whether to enable web search capability
            file_search: Whether to enable file search capability
            computer_use: Whether to enable computer use capability
            debug_mode: Whether to return a mock response for debugging
            tool_choice: How to handle tool choice ("auto", "none", or a specific tool config)
            
        Returns:
            Dict with response content or Generator yielding response chunks
        """
        try:
            # Check if OpenAI client is initialized
            if not self.client:
                self.logger.error("OpenAI client not initialized")
                return {"error": "OpenAI client not initialized", "status": "error"}
            
            # If debug_mode is enabled, return a mock response
            if debug_mode:
                self.logger.info("DEBUG MODE ENABLED - Returning mock response")
                
                # Return a mock response for immediate testing
                mock_response_id = f"debug_mock_{int(time.time())}"
                
                # Create debug info about what parameters were received
                debug_info = (
                    f"DEBUG INFO:\n\n"
                    f"- Prompt: {prompt}\n"
                    f"- Model: {model}\n"
                    f"- Documents: {len(document_paths)}\n"
                    f"- Document paths: {document_paths}\n"
                    f"- Web search: {web_search}\n"
                    f"- File search: {file_search}\n"
                    f"- Computer use: {computer_use}\n"
                    f"- Streaming: {stream}\n"
                    f"- Tools: {tools}\n"
                    f"- Tool choice: {tool_choice}\n"
                )
                
                if stream:
                    def generate_debug_response():
                        # Send initial status update
                        yield {"type": "status", "status": "processing"}
                        yield {"type": "delta", "content": debug_info}
                        
                        # Simulate processing delay
                        time.sleep(1)
                        
                        # Send content in chunks
                        for chunk in "This is a debug mode response from the OpenAI provider. Your parameters were successfully received, but we're bypassing the actual API call for testing.".split():
                            yield {"type": "delta", "content": chunk + " "}
                            time.sleep(0.1)
                        
                        # Final status update
                        yield {"type": "status", "status": "completed"}
                    
                    return generate_debug_response()
                else:
                    self.logger.info(f"Returning mock response ID: {mock_response_id}")
                    return {
                        "status": "completed",
                        "response_id": mock_response_id,
                        "model": model,
                        "content": f"{debug_info}\n\nThis is a debug mode response. Your parameters were successfully received, but we're bypassing the actual API call for testing.",
                        "usage": {
                            "prompt_tokens": 100,
                            "completion_tokens": 50,
                            "total_tokens": 150
                        }
                    }
            
            # Set up the request parameters
            responses_params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],  # Format as messages array
                "temperature": temperature,
                "stream": stream  # Add stream parameter
            }
            
            # Add tools if provided
            if tools:
                responses_params["tools"] = tools
                if tool_choice:
                    responses_params["tool_choice"] = tool_choice
            else:
                # Enable web search if requested
                if web_search:
                    responses_params["tools"] = [{"type": "web_search_preview"}]
                    self.logger.info("Enabled web search capability")
            
            # Log the request parameters
            self.logger.info(f"Sending request to OpenAI API with parameters: {responses_params}")
            
            # Make the API call
            try:
                if stream:
                    # For streaming responses
                    def generate_stream():
                        try:
                            self.logger.info("Starting streaming response generation...")
                            # Send start event
                            self.logger.info("Yielding start event")
                            yield {"type": "start", "content": ""}
                            
                            # Create streaming response
                            self.logger.info("Creating streaming response from OpenAI API...")
                            response_stream = self.client.chat.completions.create(**responses_params)
                            self.logger.info("Got response stream from OpenAI API")
                            
                            # Process each chunk
                            for chunk in response_stream:
                                if chunk.choices[0].delta.content:
                                    text = chunk.choices[0].delta.content
                                    yield {"type": "delta", "content": text}
                                elif hasattr(chunk.choices[0].delta, 'tool_calls'):
                                    tool_calls = chunk.choices[0].delta.tool_calls
                                    for tool_call in tool_calls:
                                        yield {
                                            "type": "tool_call",
                                            "tool_call": {
                                                "id": tool_call.id,
                                                "type": tool_call.type,
                                                "function": {
                                                    "name": tool_call.function.name,
                                                    "arguments": tool_call.function.arguments
                                                }
                                            }
                                        }
                            
                            # Send completion event
                            self.logger.info("Yielding completion event")
                            yield {"type": "complete", "tokens": "N/A"}
                            
                        except Exception as e:
                            self.logger.error(f"Error in streaming response: {str(e)}", exc_info=True)
                            self.logger.error(f"Error type: {type(e)}")
                            self.logger.error(f"Error args: {e.args}")
                            yield {"type": "error", "content": str(e)}
                    
                    return generate_stream()
                    
                else:
                    # For non-streaming responses
                    self.logger.info("Making non-streaming API call...")
                    response = self.client.chat.completions.create(**responses_params)
                    self.logger.info(f"Received response from OpenAI: {response}")
                    
                    # Extract content and tool calls
                    content = None
                    tool_calls = []
                    
                    if response.choices:
                        choice = response.choices[0]
                        if choice.message.content:
                            content = choice.message.content
                        if choice.message.tool_calls:
                            for tool_call in choice.message.tool_calls:
                                tool_calls.append({
                                    "id": tool_call.id,
                                    "type": tool_call.type,
                                    "function": {
                                        "name": tool_call.function.name,
                                        "arguments": tool_call.function.arguments
                                    }
                                })
                    
                    if not content and not tool_calls:
                        self.logger.error("Could not extract content or tool calls from response")
                        return {"error": "Could not extract content from response", "status": "error"}
                    
                    # Return the response
                    result = {
                        "status": "completed",
                        "response_id": str(uuid.uuid4()),  # Generate a response ID
                        "model": model,
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens,
                            "completion_tokens": response.usage.completion_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                    }
                    
                    if content:
                        result["content"] = content
                    if tool_calls:
                        result["tool_calls"] = tool_calls
                    
                    return result
                
            except Exception as e:
                self.logger.error(f"Error making OpenAI API call: {str(e)}", exc_info=True)
                return {"error": str(e), "status": "error"}
                
        except Exception as e:
            self.logger.error(f"Error in create_response: {str(e)}", exc_info=True)
            return {"error": str(e), "status": "error"}
    
    def retrieve_response(self, response_id: str) -> Dict:
        """
        Retrieve a previously created response.
        
        Args:
            response_id: The ID of the response to retrieve
            
        Returns:
            Dict with response content
        """
        try:
            # Handle mock responses for testing
            if response_id.startswith("mock_resp_"):
                self.logger.info(f"Generating mock response data for mock ID: {response_id}")
                # Return a mock completed response
                return {
                    "status": "completed",
                    "response_id": response_id,
                    "content": f"This is a mock response for testing with ID: {response_id}.\n\nDocument analysis would typically appear here, including key points, summaries, and extracted information.",
                    "model": "gpt-4o-2024-11-20",
                }
                
            if not HAS_OPENAI:
                return {"error": "OpenAI library not installed. Please install with: pip install openai"}
                    
            if not self.client:
                return {"error": "OpenAI client not initialized. Please check your API key."}
            
            self.logger.info(f"Retrieving response with ID: {response_id}")
            try:
                response = self.client.responses.retrieve(response_id=response_id)
                self.logger.debug(f"Response structure: {dir(response)}")
                
                status = response.status
                self.logger.info(f"Response status: {status}")
                
                # Build the result with common fields
                result = {
                    "status": status,
                    "response_id": response_id
                }
                
                # Add model if available
                if hasattr(response, 'model'):
                    result["model"] = response.model
                
                if status == "completed":
                    # Extract content with fallbacks for different response formats
                    content_extracted = False
                    
                    # Try the standard output.content path
                    if hasattr(response, 'output') and hasattr(response.output, 'content') and response.output.content:
                        self.logger.debug("Extracting content from output.content")
                        try:
                            result["content"] = response.output.content[0].text
                            content_extracted = True
                            
                            # Add usage information if available
                            if hasattr(response, 'usage'):
                                result["usage"] = {
                                    "prompt_tokens": response.usage.prompt_tokens,
                                    "completion_tokens": response.usage.completion_tokens,
                                    "total_tokens": response.usage.total_tokens
                                }
                        except Exception as e:
                            self.logger.error(f"Error extracting content from output.content: {str(e)}")
                    
                    # Try direct content attribute as fallback
                    if not content_extracted and hasattr(response, 'content'):
                        self.logger.debug("Extracting content from direct content attribute")
                        try:
                            result["content"] = response.content
                            content_extracted = True
                        except Exception as e:
                            self.logger.error(f"Error extracting content from direct attribute: {str(e)}")
                    
                    # If we still don't have content, check for response.choices
                    if not content_extracted and hasattr(response, 'choices') and len(response.choices) > 0:
                        self.logger.debug("Extracting content from choices[0]")
                        try:
                            choice = response.choices[0]
                            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                                result["content"] = choice.message.content
                                content_extracted = True
                        except Exception as e:
                            self.logger.error(f"Error extracting content from choices: {str(e)}")
                    
                    # Log raw response for debugging if content extraction failed
                    if not content_extracted:
                        self.logger.error(f"Failed to extract content from response: {response}")
                        result["error"] = "Response processing completed but no content was found."
                        
                elif status == "error":
                    # Extract error details
                    if hasattr(response, 'error'):
                        result["error"] = f"Error processing documents: {response.error}"
                    else:
                        result["error"] = "An error occurred, but no error details were provided."
                else:
                    # Handle in-progress status
                    result["message"] = f"Response is still processing. Status: {status}"
                    
                    # Add progress information if available
                    if hasattr(response, 'progress'):
                        result["progress"] = response.progress
                    
                    # Add step_description if available
                    if hasattr(response, 'step_description'):
                        result["step_description"] = response.step_description
                
                return result
                
            except Exception as e:
                error_msg = f"Error retrieving response from OpenAI API: {str(e)}"
                self.logger.error(error_msg)
                return {
                    "status": "error",
                    "response_id": response_id,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"Error in retrieve_response method: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    def call_tool(
        self,
        prompt: str,
        model: str,
        tools: List[Dict],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict:
        """
        Call a tool using the OpenAI API.
        
        Args:
            prompt: The prompt to send to the model
            model: The model to use
            tools: The tools available to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter
            
        Returns:
            The model's response
        """
        try:
            if not self.client:
                return {"error": "OpenAI client not initialized. Please check your API key."}
            
            model_id = self.models[model]["id"] if model in self.models else model
            self.logger.info(f"Calling tool with model: {model_id}")
            
            self.chat_history.append({
                "role": "user",
                "content": prompt
            })
            
            messages = []
            for msg in self.chat_history:
                if isinstance(msg["content"], list):
                    messages.append(msg)
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                tools=tools
            )
            
            result = {
                "content": response.choices[0].message.content or "",
                "model": model,
                "provider": "openai"
            }
            
            # Add tool calls if present
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                tool_calls = []
                for tool_call in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
                result["tool_calls"] = tool_calls
            
            # Update chat history
            self.chat_history.append({
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calling tool: {str(e)}")
            return {"error": str(e)}
    
    def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        response_format: str = "url",
        **kwargs
    ) -> Dict:
        """
        Generate an image using OpenAI's DALL-E models.
        
        Args:
            prompt: The text prompt to generate the image from
            model: The DALL-E model to use (dall-e-2 or dall-e-3)
            n: Number of images to generate
            size: Size of the generated image
            quality: Quality of the generated image
            style: Style of the generated image
            response_format: Format of the response (url or b64_json)
            
        Returns:
            Dict containing the generated image data
        """
        try:
            # Check if OpenAI library is available
            if not HAS_OPENAI:
                self.logger.error("OpenAI library not installed")
                return {"error": "OpenAI library not installed. Please install with: pip install openai"}
            
            # Initialize client with custom API key if provided in kwargs
            client = self.client
            if 'api_key' in kwargs and kwargs['api_key']:
                self.logger.info("Using custom API key provided in request")
                client = OpenAI(api_key=kwargs['api_key'])
            
            if not client:
                # Try to initialize on-demand with our stored API key
                try:
                    self.logger.info("Initializing OpenAI client on-demand")
                    client = OpenAI(api_key=self.api_key)
                except Exception as e:
                    self.logger.error(f"Failed to initialize client on-demand: {str(e)}")
                    return {"error": "OpenAI client not initialized and could not be created on-demand"}
            
            # Validate input parameters
            valid_sizes = ["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"]
            if size not in valid_sizes:
                self.logger.warning(f"Invalid size {size}, using default 1024x1024")
                size = "1024x1024"
                
            valid_qualities = ["standard", "hd"]
            if quality not in valid_qualities:
                self.logger.warning(f"Invalid quality {quality}, using default standard")
                quality = "standard"
                
            valid_styles = ["vivid", "natural"]
            if style not in valid_styles:
                self.logger.warning(f"Invalid style {style}, using default vivid")
                style = "vivid"
                
            valid_response_formats = ["url", "b64_json"]
            if response_format not in valid_response_formats:
                self.logger.warning(f"Invalid response_format {response_format}, using default url")
                response_format = "url"
            
            model_id = self.models[model]["id"] if model in self.models else model
            self.logger.info(f"Generating image with model: {model_id}, prompt: {prompt[:50]}...")
            
            # Configure generation parameters
            generation_params = {
                "model": model_id,
                "prompt": prompt,
                "n": n,
                "size": size,
                "quality": quality,
                "style": style,
                "response_format": response_format
            }
            
            # Generate the image
            response = client.images.generate(**generation_params)
            
            # Format the response
            result = {
                "created": int(time.time()) if not hasattr(response, 'created') else response.created,
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
            
            self.logger.info(f"Successfully generated {len(result['data'])} images")
            return result
            
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    def create_speech(
        self,
        text: str,
        model: str = "tts-1",
        voice: str = "alloy",
        speed: float = 1.0,
        **kwargs
    ) -> Optional[bytes]:
        """
        Generate speech from text using OpenAI's text-to-speech models.
        
        Args:
            text: The text to convert to speech
            model: The TTS model to use (tts-1 or tts-1-hd)
            voice: The voice to use (alloy, echo, fable, onyx, nova, or shimmer)
            speed: The speed of the speech (0.25 to 4.0)
            
        Returns:
            Bytes of the audio file if successful, None otherwise
        """
        try:
            if not self.client:
                self.logger.error("OpenAI client not initialized")
                return None
            
            model_id = self.models[model]["id"] if model in self.models else model
            self.logger.info(f"Generating speech with model: {model_id}")
            
            response = self.client.audio.speech.create(
                model=model_id,
                voice=voice,
                input=text,
                speed=speed
            )
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error generating speech: {str(e)}")
            return None
    
    def edit_image(
        self,
        image_path: str,
        prompt: str,
        mask_path: Optional[str] = None,
        model: str = "dall-e-2",
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url"
    ) -> Dict:
        """
        Edit an existing image using OpenAI's DALL-E models.
        
        Args:
            image_path: Path to the image to edit
            prompt: A text description of the desired edits
            mask_path: Path to the mask image (optional)
            model: The model to use (currently only dall-e-2 supports editing)
            n: The number of images to generate
            size: Size of the generated images
            response_format: Format of the response (url or b64_json)
            
        Returns:
            Dict containing the edited image data
        """
        try:
            if not HAS_OPENAI:
                self.logger.warning("OpenAI library not installed. Using mock response for testing.")
                # Return a mock response for testing
                return {
                    "created": int(time.time()),
                    "data": [
                        {
                            "url": "https://example.com/mock-edited-image.png"
                        } for _ in range(n)
                    ],
                    "model": model
                }
                
            if not self.client:
                return {"error": "OpenAI client not initialized. Please check your API key."}
            
            # Currently only DALL-E 2 supports image editing
            if model != "dall-e-2":
                self.logger.warning(f"Only DALL-E 2 supports image editing. Using dall-e-2 instead of {model}.")
                model = "dall-e-2"
            
            # Check that the image file exists
            if not os.path.isfile(image_path):
                return {"error": f"Image file not found: {image_path}"}
            
            # Check mask file if provided
            if mask_path and not os.path.isfile(mask_path):
                return {"error": f"Mask file not found: {mask_path}"}
            
            # Validate image format (must be PNG for editing)
            if not image_path.lower().endswith(".png"):
                # If it's not a PNG, we should convert it
                if not HAS_PIL:
                    return {"error": "PIL (Pillow) is required to convert images to PNG format"}
                
                try:
                    # Open the image and convert to PNG in a temporary file
                    img = Image.open(image_path)
                    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    img.save(temp_file.name, format="PNG")
                    temp_file.close()
                    image_path = temp_file.name
                    self.logger.info(f"Converted image to PNG format: {image_path}")
                except Exception as e:
                    return {"error": f"Failed to convert image to PNG: {str(e)}"}
            
            # Prepare parameters
            with open(image_path, "rb") as img_file:
                # For DALL-E 2 image edits
                params = {
                    "model": model,
                    "image": img_file,
                    "prompt": prompt,
                    "n": n,
                    "size": size,
                    "response_format": response_format
                }
                
                # Add mask if provided
                if mask_path:
                    with open(mask_path, "rb") as mask_file:
                        params["mask"] = mask_file
                        response = self.client.images.edit(**params)
                else:
                    response = self.client.images.edit(**params)
            
            # Process and return the response
            result = {
                "created": int(time.time()),
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
                
                result["data"].append(img_info)
            
            return result
            
        except Exception as e:
            error_msg = f"Error editing image: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    def create_image_variation(
        self,
        image_path: str,
        model: str = "dall-e-2",
        n: int = 1,
        size: str = "1024x1024",
        response_format: str = "url"
    ) -> Dict:
        """
        Create variations of an existing image using OpenAI's DALL-E models.
        
        Args:
            image_path: Path to the image to use as the basis for variations
            model: The model to use (currently only dall-e-2 supports variations)
            n: The number of variations to generate
            size: Size of the generated variations
            response_format: Format of the response (url or b64_json)
            
        Returns:
            Dict containing the image variation data
        """
        try:
            if not HAS_OPENAI:
                self.logger.warning("OpenAI library not installed. Using mock response for testing.")
                # Return a mock response for testing
                return {
                    "created": int(time.time()),
                    "data": [
                        {
                            "url": f"https://example.com/mock-variation-{i}.png"
                        } for i in range(n)
                    ],
                    "model": model
                }
                
            if not self.client:
                return {"error": "OpenAI client not initialized. Please check your API key."}
            
            # Currently only DALL-E 2 supports image variations
            if model != "dall-e-2":
                self.logger.warning(f"Only DALL-E 2 supports image variations. Using dall-e-2 instead of {model}.")
                model = "dall-e-2"
            
            # Check that the image file exists
            if not os.path.isfile(image_path):
                return {"error": f"Image file not found: {image_path}"}
            
            # Validate image format (must be PNG or JPEG)
            img_ext = os.path.splitext(image_path)[1].lower()
            if img_ext not in [".png", ".jpg", ".jpeg"]:
                # If it's not a supported format, we should convert it
                if not HAS_PIL:
                    return {"error": "PIL (Pillow) is required to convert images to PNG format"}
                
                try:
                    # Open the image and convert to PNG in a temporary file
                    img = Image.open(image_path)
                    temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    img.save(temp_file.name, format="PNG")
                    temp_file.close()
                    image_path = temp_file.name
                    self.logger.info(f"Converted image to PNG format: {image_path}")
                except Exception as e:
                    return {"error": f"Failed to convert image to PNG: {str(e)}"}
            
            # Prepare parameters
            with open(image_path, "rb") as img_file:
                # For DALL-E 2 image variations
                params = {
                    "model": model,
                    "image": img_file,
                    "n": n,
                    "size": size,
                    "response_format": response_format
                }
                
                response = self.client.images.create_variation(**params)
            
            # Process and return the response
            result = {
                "created": int(time.time()),
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
                
                result["data"].append(img_info)
            
            return result
            
        except Exception as e:
            error_msg = f"Error creating image variation: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
        self.logger.info("Cleared conversation history") 