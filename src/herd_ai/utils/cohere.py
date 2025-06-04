"""
Cohere API Implementation for Herd AI
This module provides integration with the Cohere AI API for the Herd AI system.
Supports sending text prompts, chat completions, and structured output.

References:
- Cohere API Documentation: https://docs.cohere.com/reference/about
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List, Union
from rich.console import Console
import cohere

# Initialize console for rich output
console = Console()

# Default models
DEFAULT_TEXT_MODEL = "command-a-03-2025"

def get_api_key() -> Optional[str]:
    """Get the Cohere API key from environment variables."""
    api_key = os.environ.get("COHERE_API_KEY")
    if not api_key:
        # Try to get from imported config if available
        try:
            from herd_ai.config import COHERE_API_KEY
            api_key = COHERE_API_KEY
        except ImportError:
            pass
    return api_key

def init_cohere_client():
    """Initialize and return Cohere client."""
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        return cohere.ClientV2(api_key=api_key)
    except Exception as e:
        console.print(f"[red]Error initializing Cohere client: {e}[/red]")
        return None

def process_with_cohere(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    documents: Optional[List[Dict[str, str]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    system_message: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a prompt with Cohere AI API.

    Args:
        prompt: The prompt to send to the API
        model: Model name (defaults to command-a-03-2025)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        messages: Optional list of message dictionaries for chat history
        documents: Optional list of documents to provide context
        tools: Optional list of tools for function calling
        system_message: Optional system message for chat
        description: Unused parameter (for compatibility with other providers)

    Returns:
        Dict with text response and metadata
    """
    client = init_cohere_client()
    if not client:
        return {"text": "Error: Cohere API client initialization failed. Check your API key.", "error": True}

    # Select model
    model = model or os.environ.get("COHERE_MODEL", DEFAULT_TEXT_MODEL)

    # Build messages list if not provided
    if messages is None:
        messages = []
        if system_message:
            messages.append({"role": "SYSTEM", "content": system_message})
        messages.append({"role": "USER", "content": prompt})

    # Prepare parameters
    kwargs = {
        "model": model,
        "messages": messages
    }
    
    # Add optional parameters if provided
    if documents:
        kwargs["documents"] = documents
    
    if tools:
        kwargs["tools"] = tools
    
    # Temperature controls sampling randomness (0.0 to 1.0)
    if temperature is not None:
        kwargs["temperature"] = temperature
    
    # Max tokens limits the response length
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    try:
        response = client.chat(**kwargs)
        
        # Extract text from response
        text_response = ""
        if hasattr(response, "message") and hasattr(response.message, "content"):
            if response.message.content:
                if isinstance(response.message.content, list) and len(response.message.content) > 0:
                    text_response = response.message.content[0].text
                elif hasattr(response.message.content, "text"):
                    text_response = response.message.content.text
        else:
            text_response = str(response)
        
        # Return in the expected format
        return {
            "text": text_response,
            "model": model,
            "provider": "cohere",
            "raw": response,
            "error": False
        }
    except Exception as e:
        error_msg = f"Error calling Cohere API: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return {"text": error_msg, "error": True}

def send_prompt_to_cohere(prompt: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a prompt to Cohere AI API.
    This is a wrapper for process_with_cohere with simpler parameters.

    Args:
        prompt: The prompt to send
        description: Optional description (unused, for compatibility)

    Returns:
        Dict with text response and metadata
    """
    return process_with_cohere(prompt=prompt)

def send_chat_to_cohere(
    messages: List[Dict[str, str]],
    system_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a chat conversation to Cohere AI API.

    Args:
        messages: List of message dictionaries
        system_message: Optional system message

    Returns:
        Dict with text response and metadata
    """
    return process_with_cohere(
        prompt="",  # Not used directly with messages parameter
        messages=messages,
        system_message=system_message
    )

def list_cohere_models() -> List[Dict[str, Any]]:
    """
    List available Cohere AI models.

    Returns:
        List of model information dictionaries
    """
    client = init_cohere_client()
    if not client:
        console.print("[yellow]Warning: Cohere API client initialization failed. Check your API key.[/yellow]")
        return [{
            "id": "command-a-03-2025",
            "name": "Command-a-03-2025",
            "created": None,
            "description": "General purpose text generation model",
            "context_length": 128000,
            "capabilities": ["text", "chat"]
        }]

    # Note: Cohere doesn't have a dedicated models list endpoint at this time
    # Return a static list of models instead
    return [
        {
            "id": "command-a-03-2025",
            "name": "Command-a-03-2025",
            "created": None,
            "description": "General purpose text generation model",
            "context_length": 128000,
            "capabilities": ["text", "chat", "function"]
        },
        {
            "id": "command-light-a",
            "name": "Command Light",
            "created": None,
            "description": "Faster and more efficient text generation model",
            "context_length": 32000,
            "capabilities": ["text", "chat"]
        },
        {
            "id": "command-nightly",
            "name": "Command Nightly",
            "created": None,
            "description": "Latest experimental model with new features",
            "context_length": 128000,
            "capabilities": ["text", "chat", "function"]
        }
    ]

if __name__ == "__main__":
    # Quick test if run directly
    if get_api_key():
        console.print("[green]Testing Cohere API connection...[/green]")
        result = send_prompt_to_cohere("Hello, what capabilities do you have?")
        console.print(f"Response: {result['text']}")
    else:
        console.print("[red]COHERE_API_KEY not set. Please set this environment variable to use Cohere API.[/red]") 