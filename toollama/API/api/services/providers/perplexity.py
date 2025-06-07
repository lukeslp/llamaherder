#!/usr/bin/env python
"""
Perplexity API Provider Implementation
This module provides an interface to the Perplexity API for streaming chat responses.
"""

import os
import sys
import json
import requests
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Hardcoded API key from flask_chat_perplexity.py
PERPLEXITY_API_KEY = "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"

class PerplexityProvider:
    """Provider implementation for Perplexity API."""
    
    # Define available models - updated based on latest Perplexity API documentation
    # Source: https://docs.perplexity.ai/guides/model-cards (as of February 2025)
    MODELS = {
        # Current models (as of February 2025)
        "sonar-deep-research": {
            "id": "sonar-deep-research",
            "context_length": 60000,
            "description": "Specialized model for in-depth research with search capabilities",
            "created": "2025-02-15",
            "capabilities": ["chat", "web_search", "research"]
        },
        "sonar-reasoning-pro": {
            "id": "sonar-reasoning-pro",
            "context_length": 128000,
            "description": "Advanced reasoning model with Chain-of-Thought and 8k output limit",
            "created": "2025-02-15",
            "capabilities": ["chat", "web_search", "reasoning"]
        },
        "sonar-reasoning": {
            "id": "sonar-reasoning",
            "context_length": 128000,
            "description": "Advanced reasoning model with Chain-of-Thought capabilities",
            "created": "2025-01-29",
            "capabilities": ["chat", "web_search", "reasoning"]
        },
        "sonar-pro": {
            "id": "sonar-pro",
            "context_length": 200000,
            "description": "Professional grade completion with 8k output limit",
            "created": "2025-01-29",
            "capabilities": ["chat", "web_search"]
        },
        "sonar": {
            "id": "sonar",
            "context_length": 128000,
            "description": "Standard chat completion model with search capabilities",
            "created": "2025-01-29",
            "capabilities": ["chat", "web_search"]
        },
        "r1-1776": {
            "id": "r1-1776",
            "context_length": 128000,
            "description": "Offline chat model that does not use search subsystem",
            "created": "2025-02-15",
            "capabilities": ["chat"]
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Perplexity client with the provided API key."""
        # Try to get API key from init param, then environment, then use the hardcoded key
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY", PERPLEXITY_API_KEY)
        self.base_url = "https://api.perplexity.ai"
        
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
        
        logger.info("Initialized Perplexity provider")

    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 1000,
        capability_filter: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Retrieve available Perplexity models.
        
        Args:
            sort_by (str): Field to sort by (created/id/capabilities)
            page (int): Page number for pagination
            page_size (int): Number of models per page
            capability_filter (Optional[str]): Filter by capability
            
        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            models = []
            for model_id, info in self.MODELS.items():
                # Get capabilities from model info
                capabilities = info.get("capabilities", ["chat"])
                
                # Check if model is deprecated
                deprecated = info.get("deprecated", False)
                
                # Create model entry
                model_entry = {
                    "id": model_id,
                    "name": model_id,
                    "description": info["description"],
                    "context_length": info["context_length"],
                    "capabilities": capabilities,
                    "created_at": info.get("created", datetime.now().isoformat()),
                    "owned_by": "Perplexity",
                    "deprecated": deprecated
                }
                
                models.append(model_entry)
            
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
            logger.error(f"Error listing models: {e}")
            # Return base models if there's an error
            return [{"id": model_id, "name": model_id} for model_id in self.MODELS.keys()]

    def stream_chat_response(
        self,
        message: str,
        model: str = "sonar",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        return_citations: bool = False,
        search_recency_filter: Optional[str] = None,
        **kwargs
    ) -> Generator[Dict, None, None]:
        """
        Stream a chat response from Perplexity.
        
        Args:
            message (str): The user's input message
            model (str): The Perplexity model to use
            max_tokens (int): Maximum number of tokens in the response
            temperature (float): Response temperature (0.0 to 1.0)
            top_p (float): The nucleus sampling parameter
            return_citations (bool): Whether to return citations for online models
            search_recency_filter (str): Time filter for search results (day, week, month)
            
        Yields:
            Dict: Chunks of the response text as they arrive
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Debug logging
        logger.info(f"Using API key: {self.api_key[:5]}...{self.api_key[-5:]}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Using model: {model}")

        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": message
        })
        
        # Build API request payload
        payload = {
            "model": model,
            "messages": self.chat_history,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        # Add optional parameters
        if return_citations:
            payload["return_citations"] = return_citations
        
        if search_recency_filter:
            payload["search_recency_filter"] = search_recency_filter
            
        full_response = ""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # Remove "data: " prefix
                            
                        if line_text == "[DONE]":
                            break
                            
                        data = json.loads(line_text)
                        if data.get("choices") and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                yield {"content": content}
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
            if len(self.chat_history) > 1:
                self.chat_history.pop()
            yield {"content": f"Error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            # Remove the user message if request failed
            if len(self.chat_history) > 1:
                self.chat_history.pop()
            yield {"content": f"Error: {str(e)}"}

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
        logger.info("Cleared conversation history")
        return {"status": "success", "message": "Conversation cleared"} 