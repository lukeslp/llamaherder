#!/usr/bin/env python
"""
Coze Provider for Camina Chat API
Implements the BaseProvider interface using the Coze API
Based on the implementation from flask_chat_coze.py
"""

import os
import sys
import tempfile
import io
import json
import requests
from typing import Generator, List, Dict, Optional, Union, Any
from datetime import datetime
from base64 import b64encode
import logging
import traceback
from PIL import Image

from api.services.providers.base import BaseProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants imported directly from flask_chat_coze.py
COZE_AUTH_TOKEN = 'pat_x43jhhVkypZ7CrKwnFwLGLdHOAegoEQqnhFO4kIqomnw6a3Zp4EaorAYfn6EMLz4'
COZE_BOT_ID = "7462296933429346310"  # Alt Text Generator bot ID
COZE_TTS_BOT_ID = "7463319430379470854"  # TTS Generator bot ID
COZE_SPACE_ID = "7345427862138912773"
HF_API_KEY = "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"

# Global conversation store
conversation_store = {}

# Import Coze SDK
try:
    from cozepy import Coze, TokenAuth, Message, ChatEventType, MessageObjectString
    if not COZE_AUTH_TOKEN:
        logger.warning("COZE_AUTH_TOKEN not found in environment variables")
        coze_client = None
    else:
        logger.info("Initializing Coze client")
        coze_client = Coze(auth=TokenAuth(token=COZE_AUTH_TOKEN))
except Exception as e:
    logger.error(f"Failed to initialize Coze client: {str(e)}")
    coze_client = None


# Define the stream_chat_with_file function from flask_chat_coze.py
def stream_chat_with_file(message, bot_id, user_id, file_id=None):
    """Stream a chat response from Coze with proper file handling."""
    try:
        # Initialize conversation if needed
        if user_id not in conversation_store:
            conversation_store[user_id] = {}

        if bot_id not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = coze_client.conversations.create(messages=[initial_message])
            conversation_store[user_id][bot_id] = conversation.id

        conversation_id = conversation_store[user_id][bot_id]

        # Build message with optional file attachment
        messages = []
        if file_id:
            messages.append(
                Message.build_user_question_objects([
                    MessageObjectString.build_text(message or "Please describe this image"),
                    MessageObjectString.build_image(file_id=file_id)
                ])
            )
        else:
            messages.append(Message.build_user_question_text(message))

        # Stream response
        total_tokens = 0
        for event in coze_client.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            conversation_id=conversation_id,
            additional_messages=messages
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                total_tokens += len(event.message.content.split())
                yield {
                    'type': 'delta',
                    'content': event.message.content,
                    'tokens': total_tokens
                }
            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                yield {
                    'type': 'complete',
                    'tokens': total_tokens
                }

    except Exception as e:
        logger.error(f"Error in stream_chat_response: {str(e)}")
        yield {'type': 'error', 'message': str(e)}


class CozeProvider(BaseProvider):
    """Coze provider implementation using the exact CozeChat class from flask_chat_coze.py."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Coze provider.
        
        Args:
            api_key: The API key for Coze (will use COZE_AUTH_TOKEN if None)
        """
        self.api_key = api_key or COZE_AUTH_TOKEN
        self.coze_client = coze_client
        self.conversation_store = {}
        logger.info(f"Initialized Coze provider with API key: {'present' if self.api_key else 'missing'}")

    def fetch_coze_bots(self) -> List[Dict[str, Any]]:
        """
        Fetch bots from Coze API using direct HTTP request.
        
        Returns:
            List of bot data dictionaries
        """
        try:
            if not self.api_key:
                logger.warning("No auth token available for fetching Coze bots")
                return []
                
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # Try various possible endpoint patterns
            endpoints = [
                "https://api.coze.com/v1/published_bots",
                "https://api.coze.com/v1/bots",
                "https://api.coze.com/v1/bots/list",
                "https://api.coze.com/v1/bots/published",
                "https://api.coze.com/v1/agents",
                "https://www.coze.com/api/v1/bots",
                "https://www.coze.com/api/v1/published_bots"
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Attempting to fetch bots from: {endpoint}")
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    
                    # Only raise for 4xx/5xx status codes, not for other types of errors
                    response.raise_for_status()
                    
                    # Try to parse the response as JSON
                    data = response.json()
                    
                    # Check common response patterns
                    if isinstance(data, list) and len(data) > 0:
                        logger.info(f"Successfully fetched {len(data)} bots from {endpoint}")
                        return data
                    elif "data" in data and isinstance(data["data"], list):
                        logger.info(f"Successfully fetched {len(data['data'])} bots from {endpoint}")
                        return data["data"]
                    elif "bots" in data and isinstance(data["bots"], list):
                        logger.info(f"Successfully fetched {len(data['bots'])} bots from {endpoint}")
                        return data["bots"]
                    elif "results" in data and isinstance(data["results"], list):
                        logger.info(f"Successfully fetched {len(data['results'])} bots from {endpoint}")
                        return data["results"]
                    else:
                        logger.warning(f"Received unexpected response structure from {endpoint}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request to {endpoint} failed: {str(e)}")
                except ValueError as e:
                    logger.warning(f"Failed to parse JSON from {endpoint}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Unexpected error accessing {endpoint}: {str(e)}")
            
            # If space ID is available, try the space bots endpoints
            if COZE_SPACE_ID:
                space_endpoints = [
                    f"https://api.coze.com/v1/spaces/{COZE_SPACE_ID}/bots",
                    f"https://api.coze.com/v1/spaces/{COZE_SPACE_ID}/agents",
                    f"https://www.coze.com/api/v1/spaces/{COZE_SPACE_ID}/bots"
                ]
                
                for endpoint in space_endpoints:
                    try:
                        logger.info(f"Attempting to fetch bots from space endpoint: {endpoint}")
                        response = requests.get(endpoint, headers=headers, timeout=10)
                        response.raise_for_status()
                        
                        data = response.json()
                        
                        # Check common response patterns
                        if isinstance(data, list) and len(data) > 0:
                            logger.info(f"Successfully fetched {len(data)} space bots from {endpoint}")
                            return data
                        elif "data" in data and isinstance(data["data"], list):
                            logger.info(f"Successfully fetched {len(data['data'])} space bots from {endpoint}")
                            return data["data"]
                        elif "bots" in data and isinstance(data["bots"], list):
                            logger.info(f"Successfully fetched {len(data['bots'])} space bots from {endpoint}")
                            return data["bots"]
                        elif "results" in data and isinstance(data["results"], list):
                            logger.info(f"Successfully fetched {len(data['results'])} space bots from {endpoint}")
                            return data["results"]
                    except Exception as e:
                        logger.warning(f"Failed to fetch space bots from {endpoint}: {str(e)}")
            
            # If all attempts failed, log and return empty list
            logger.warning("Could not fetch bots from any endpoint. The API endpoints may have changed or access might be restricted.")
            logger.info("Falling back to hardcoded models only")
            return []
            
        except Exception as e:
            logger.error(f"Error in fetch_coze_bots: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Return a list of available Coze bots.
        
        Args:
            sort_by: Field to sort by
            page: Page number
            page_size: Number of items per page
            capability_filter: Filter models by capability
            **kwargs: Additional parameters
            
        Returns:
            List of model dictionaries
        """
        try:
            # Always include the hardcoded Alt Text Generator bot
            models = [{
                "id": COZE_BOT_ID,
                "name": "Alt Text Generator",
                "description": "Coze bot for generating alt text",
                "capabilities": ["text", "vision"],
                "capability_count": 2,
                "created": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "owned_by": "coze",
                "provider": "coze"
            }]
            
            # Attempt to fetch additional bots dynamically
            if self.api_key:
                try:
                    # Fetch bots from the API
                    bots = self.fetch_coze_bots()
                    logger.info(f"Fetched {len(bots)} bots from Coze API")
                    
                    # Process each bot and add to the models list
                    for bot in bots:
                        # Skip if the bot data is not a dict
                        if not isinstance(bot, dict):
                            logger.warning(f"Skipping bot with non-dict data: {bot}")
                            continue
                            
                        # Extract bot ID using various potential field names
                        bot_id = None
                        for id_field in ['id', 'botId', 'bot_id', 'uuid', 'identifier']:
                            if id_field in bot:
                                bot_id = bot.get(id_field)
                                break
                                
                        if not bot_id:
                            logger.warning(f"Skipping bot with no identifiable ID: {bot}")
                            continue
                            
                        # Skip the alt text bot since we already have it hardcoded
                        if bot_id == COZE_BOT_ID:
                            continue
                        
                        # Extract bot details using various potential field names
                        bot_name = None
                        for name_field in ['name', 'botName', 'bot_name', 'title', 'displayName']:
                            if name_field in bot:
                                bot_name = bot.get(name_field)
                                if bot_name:
                                    break
                        
                        bot_name = bot_name or f"Bot {bot_id}"
                        
                        bot_desc = None
                        for desc_field in ['description', 'desc', 'about', 'summary', 'info']:
                            if desc_field in bot:
                                bot_desc = bot.get(desc_field)
                                if bot_desc:
                                    break
                                    
                        bot_desc = bot_desc or f"Coze bot {bot_id}"
                        
                        # Determine capabilities by checking common field patterns
                        bot_capabilities = ["text"]  # Assume all bots support text
                        
                        # Check for vision capabilities with various field patterns
                        vision_indicators = [
                            bot.get('has_vision', False),
                            bot.get('hasVision', False),
                            bot.get('vision_enabled', False),
                            bot.get('visionEnabled', False),
                            bot.get('supportsVision', False),
                            bot.get('supports_vision', False),
                            bot.get('supports_images', False),
                            bot.get('supportsImages', False),
                            'vision' in bot.get('capabilities', []),
                            'image' in bot.get('capabilities', [])
                        ]
                        
                        if any(vision_indicators):
                            bot_capabilities.append("vision")
                            
                        # Check for audio capabilities with various field patterns
                        audio_indicators = [
                            bot.get('has_audio', False),
                            bot.get('hasAudio', False),
                            bot.get('audio_enabled', False),
                            bot.get('audioEnabled', False),
                            bot.get('supportsAudio', False),
                            bot.get('supports_audio', False),
                            'audio' in bot.get('capabilities', []),
                            'voice' in bot.get('capabilities', [])
                        ]
                        
                        if any(audio_indicators):
                            bot_capabilities.append("audio")
                        
                        # Extract creation date if available
                        creation_date = datetime.now().strftime("%Y-%m-%d")
                        for date_field in ['created_at', 'createdAt', 'creation_date', 'creationDate', 'created']:
                            if date_field in bot:
                                date_value = bot.get(date_field)
                                if date_value:
                                    try:
                                        # Handle different date formats - string or timestamp
                                        if isinstance(date_value, str):
                                            creation_date = date_value
                                        elif isinstance(date_value, (int, float)):
                                            # Convert timestamp to date string
                                            creation_date = datetime.fromtimestamp(date_value).strftime("%Y-%m-%d")
                                    except Exception as e:
                                        logger.warning(f"Failed to parse creation date: {e}")
                                    break
                        
                        # Extract owner information if available
                        owner = "coze"
                        for owner_field in ['owner', 'owned_by', 'ownedBy', 'creator', 'author']:
                            if owner_field in bot:
                                owner_value = bot.get(owner_field)
                                if owner_value:
                                    owner = owner_value
                                    break
                        
                        # Add bot to models list
                        models.append({
                            "id": bot_id,
                            "name": bot_name,
                            "description": bot_desc,
                            "capabilities": bot_capabilities,
                            "capability_count": len(bot_capabilities),
                            "created": creation_date,
                            "created_at": creation_date,
                            "owned_by": owner,
                            "provider": "coze"
                        })
                        
                    logger.info(f"Added {len(models) - 1} additional Coze bots")
                except Exception as e:
                    logger.error(f"Error processing Coze bots: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Fall back to including the TTS bot if dynamic fetching fails
                    if not any(m["id"] == COZE_TTS_BOT_ID for m in models):
                        models.append({
                            "id": COZE_TTS_BOT_ID,
                            "name": "TTS Generator",
                            "description": "Coze bot for text-to-speech",
                            "capabilities": ["text", "audio"],
                            "capability_count": 2,
                            "created": datetime.now().strftime("%Y-%m-%d"),
                            "created_at": datetime.now().strftime("%Y-%m-%d"),
                            "owned_by": "coze",
                            "provider": "coze"
                        })
            else:
                # If auth token is not available, add the hardcoded TTS bot
                models.append({
                    "id": COZE_TTS_BOT_ID,
                    "name": "TTS Generator",
                    "description": "Coze bot for text-to-speech",
                    "capabilities": ["text", "audio"],
                    "capability_count": 2,
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "owned_by": "coze",
                    "provider": "coze"
                })
            
            # Add command-r model for compatibility with the frontend
            models.append({
                "id": "command-r-plus-08-2024",
                "name": "Command R+ (via Coze)",
                "description": "Command R model through Coze integration",
                "capabilities": ["text", "function"],
                "capability_count": 2,
                "created": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "owned_by": "coze",
                "provider": "coze"
            })
            
            # Apply capability filter
            if capability_filter:
                models = [m for m in models if capability_filter in m["capabilities"]]
                
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
        except Exception as e:
            logger.error(f"Error in list_models: {str(e)}")
            logger.error(traceback.format_exc())
            # Return default models in case of error
            return [{
                "id": COZE_BOT_ID,
                "name": "Alt Text Generator",
                "description": "Coze bot for generating alt text",
                "capabilities": ["text", "vision"],
                "capability_count": 2,
                "created": datetime.now().strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "owned_by": "coze",
                "provider": "coze"
            }]

    def stream_chat_response(
        self,
        prompt: str,
        model: str = COZE_BOT_ID,
        max_tokens: int = 8000,
        image_path: Optional[str] = None,
        file_id: Optional[str] = None,
        **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat response from Coze using the shared implementation.
        
        Args:
            prompt: The user's message
            model: The model/bot ID to use
            max_tokens: Maximum tokens to generate (not used by Coze)
            image_path: Path to an image file (if provided)
            file_id: ID of a previously uploaded file (if available)
            **kwargs: Additional parameters
            
        Returns:
            Generator yielding response chunks
        """
        # Generate a unique user ID if not provided
        user_id = kwargs.get('user_id', f"user_{datetime.now().timestamp()}")
        
        # Process image if provided
        uploaded_file_id = file_id
        if not uploaded_file_id and image_path:
            try:
                uploaded_file_id = self.upload_file(image_path)
                logger.info(f"Uploaded file with ID: {uploaded_file_id}")
            except Exception as e:
                logger.error(f"Error uploading file: {str(e)}")
                yield {"error": f"Error uploading file: {str(e)}"}
                return
        
        # Use global conversation store for compatibility with stream_chat_with_file
        global conversation_store
        
        # Initialize user in global conversation store if needed
        if user_id not in conversation_store:
            conversation_store[user_id] = {}
            
        # Initialize user in local store for compatibility with class methods
        if user_id not in self.conversation_store:
            self.conversation_store[user_id] = {}
            
        # Make sure conversation is initialized in both stores
        if model not in conversation_store.get(user_id, {}):
            try:
                initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
                conversation = self.coze_client.conversations.create(messages=[initial_message])
                conversation_store[user_id][model] = conversation.id
                # Also update local store
                self.conversation_store[user_id][model] = conversation_store[user_id][model]
            except Exception as e:
                logger.error(f"Error initializing conversation: {str(e)}")
                yield {"content": f"Error initializing conversation: {str(e)}"}
                return
        
        # Use the shared implementation
        try:
            chunks_yielded = False
            for chunk in stream_chat_with_file(prompt, model, user_id, uploaded_file_id):
                chunks_yielded = True
                if 'content' in chunk:
                    yield {"content": chunk['content']}
                elif 'error' in chunk:
                    yield {"error": chunk['error']}
                elif 'message' in chunk:
                    yield {"content": chunk['message']}
                else:
                    yield chunk
                    
            # If no chunks were yielded, return an error
            if not chunks_yielded:
                yield {"content": "No response received from Coze API. Please check your connection and API key."}
        except Exception as e:
            logger.error(f"Error in stream_chat_response: {str(e)}")
            yield {"content": f"Error: {str(e)}"}

    def clear_conversation(self, user_id: str = None, model: str = None):
        """
        Clear the conversation history.
        
        Args:
            user_id: The user ID (if None, clear all users)
            model: The model/bot ID (if None, clear all models for the user)
        """
        # Clear from global conversation store
        global conversation_store
        
        if user_id is None:
            # Clear all conversation history
            conversation_store.clear()
            self.conversation_store.clear()
            return
            
        if user_id in conversation_store:
            if model is None:
                # Clear all models for this user
                conversation_store[user_id].clear()
            elif model in conversation_store[user_id]:
                # Clear specific model for this user
                del conversation_store[user_id][model]
            
        # Also clear from local store
        if user_id in self.conversation_store:
            if model is None:
                self.conversation_store[user_id].clear()
            elif model in self.conversation_store[user_id]:
                del self.conversation_store[user_id][model]

    def process_image(self, file_path: str) -> Optional[str]:
        """
        Process an image for use in multimodal requests.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            File ID for the uploaded image or None if processing failed
        """
        try:
            return self.upload_file(file_path)
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to Coze API.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            File ID for the uploaded file or None if upload failed
        """
        try:
            if not self.api_key:
                logger.warning("No auth token available for uploading file")
                return None
                
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                upload_response = requests.post(
                    'https://api.coze.com/v1/files/upload',
                    files=files,
                    headers=headers
                )
                
                if not upload_response.ok:
                    raise Exception(f"Upload failed: {upload_response.text}")
                    
                upload_data = upload_response.json()
                
                # Extract file ID according to documented response format
                # Response format: {"code": 0, "data": {"id": "xxx", ...}, "msg": ""}
                file_id = None
                if upload_data.get('code') == 0:
                    file_id = upload_data.get('data', {}).get('id')
                
                if not file_id:
                    raise Exception("No file_id in response")
                
                logger.info(f"File uploaded successfully, ID: {file_id}")
                return file_id
                
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return None

    def call_tool(
        self,
        prompt: str,
        model: str = COZE_BOT_ID,
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Use the model to call tools based on the prompt.
        
        Args:
            prompt: The user's message
            model: The model/bot ID to use
            tools: List of tool definitions
            max_tokens: Maximum tokens to generate (not used by Coze)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing the response and any tool calls
        """
        try:
            # Coze doesn't support direct tool calls, so we include the tools in the prompt
            if tools:
                tools_str = json.dumps(tools, indent=2)
                enhanced_prompt = f"{prompt}\n\nAvailable tools:\n{tools_str}\n\nPlease use these tools to respond to my request. Return your response in JSON format if appropriate."
            else:
                enhanced_prompt = prompt
                
            # Generate a unique user ID
            user_id = kwargs.get('user_id', f"user_{datetime.now().timestamp()}")
            
            # Stream the response and collect it
            full_response = ""
            for chunk in self.stream_chat_response(enhanced_prompt, model, max_tokens, user_id=user_id):
                if 'content' in chunk:
                    full_response += chunk['content']
                    
            # Try to extract tool calls from the response
            tool_calls = []
            try:
                # Look for JSON blocks in the response
                import re
                json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)```', full_response)
                
                for block in json_blocks:
                    try:
                        data = json.loads(block.strip())
                        if isinstance(data, dict) and ('name' in data or 'function' in data):
                            # Found a function call
                            tool_call = {
                                "id": f"call_{int(datetime.now().timestamp() * 1000)}",
                                "type": "function",
                                "function": {
                                    "name": data.get('name') or data.get('function', {}).get('name', 'unknown_function'),
                                    "arguments": json.dumps(data.get('arguments') or data.get('parameters') or {})
                                }
                            }
                            tool_calls.append(tool_call)
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                logger.warning(f"Failed to extract tool calls: {e}")
                
            return {
                "content": full_response,
                "tool_calls": tool_calls,
                "model": model,
                "provider": "coze"
            }
            
        except Exception as e:
            logger.error(f"Error in call_tool: {str(e)}")
            return {
                "content": f"Error calling tools: {str(e)}",
                "error": str(e),
                "model": model,
                "provider": "coze",
                "tool_calls": []
            }

    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 for API requests.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64-encoded image data or None if encoding failed
        """
        try:
            with open(image_path, "rb") as image_file:
                return b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return None 