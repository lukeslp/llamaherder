#!/usr/bin/env python
import logging
import requests
import json
from typing import Generator, List, Dict, Any, Optional
from api.services.providers.base import BaseProvider

# Logger for this module
logger = logging.getLogger(__name__)

class LMStudioProvider(BaseProvider):
    """Provider implementation for LM Studio local server."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LM Studio provider.
        
        Args:
            api_key: Not used for LM Studio, kept for interface compatibility
        """
        self.base_url = "http://192.168.0.32:8001"
        self.conversation_history = []
        logger.info("Initialized LM Studio provider")
    
    def list_models(self, **kwargs) -> List[Dict[str, Any]]:
        """
        List available models from LM Studio.
        
        Returns:
            List of model objects
        """
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                return [{
                    "id": model.get("id", ""),
                    "name": model.get("id", ""),
                    "provider": "lmstudio"
                } for model in models]
            else:
                logger.error(f"Error listing LM Studio models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing LM Studio models: {str(e)}")
            return []
    
    def stream_chat_response(self, prompt: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a chat response from LM Studio.
        
        Args:
            prompt: The user's message
            **kwargs: Additional parameters like model, max_tokens, etc.
            
        Yields:
            Response chunks as they become available
        """
        model = kwargs.get("model", "mistral-7b-instruct")
        max_tokens = kwargs.get("max_tokens", 1024)
        
        try:
            # Format messages array
            messages = []
            
            # Check if there's history to include
            if self.conversation_history:
                messages.extend(self.conversation_history)
            
            # Add the current message
            messages.append({"role": "user", "content": prompt})
            
            # Prepare the request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            # Make streaming request to LM Studio
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                complete_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            if line_text.startswith('data: '):
                                data_str = line_text[6:]  # Remove 'data: ' prefix
                                if data_str == '[DONE]':
                                    continue
                                
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        choice = data['choices'][0]
                                        if 'delta' in choice and 'content' in choice['delta']:
                                            content = choice['delta']['content']
                                            if content:
                                                complete_response += content
                                                yield {"content": content}
                                except json.JSONDecodeError:
                                    logger.warning(f"Invalid JSON in stream: {data_str}")
                        except Exception as e:
                            logger.error(f"Error processing chunk: {str(e)}")
                            continue
                
                # Store the complete response in history
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": complete_response})
            else:
                error_msg = f"LM Studio API error: {response.status_code}"
                logger.error(error_msg)
                yield {"content": error_msg}
                
        except Exception as e:
            error_msg = f"Error in LM Studio chat: {str(e)}"
            logger.error(error_msg)
            yield {"content": error_msg}
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def process_image(self, file_path: str) -> Optional[str]:
        """
        Process an image for use in multimodal requests.
        Not supported by LM Studio.
        
        Returns:
            None as LM Studio doesn't support images
        """
        return None
    
    def call_tool(self, prompt: str, model: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Use the model to call tools based on the prompt.
        Not supported by LM Studio.
        
        Returns:
            Dict with error message
        """
        return {"error": "Tool calling not supported by LM Studio"}
    
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 or other format required by the provider.
        Not supported by LM Studio.
        
        Returns:
            None as LM Studio doesn't support images
        """
        return None 