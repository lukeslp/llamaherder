# Code Snippets from src/herd_ai/utils/cohere.py

File: `src/herd_ai/utils/cohere.py`  
Language: Python  
Extracted: 2025-06-07 05:09:45  

## Snippet 1
Lines 3-16

```Python
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
```

## Snippet 2
Lines 23-25

```Python
def get_api_key() -> Optional[str]:
    """Get the Cohere API key from environment variables."""
    api_key = os.environ.get("COHERE_API_KEY")
```

## Snippet 3
Lines 27-32

```Python
# Try to get from imported config if available
        try:
            from herd_ai.config import COHERE_API_KEY
            api_key = COHERE_API_KEY
        except ImportError:
            pass
```

## Snippet 4
Lines 35-37

```Python
def init_cohere_client():
    """Initialize and return Cohere client."""
    api_key = get_api_key()
```

## Snippet 5
Lines 38-45

```Python
if not api_key:
        return None
    try:
        return cohere.ClientV2(api_key=api_key)
    except Exception as e:
        console.print(f"[red]Error initializing Cohere client: {e}[/red]")
        return None
```

## Snippet 6
Lines 46-64

```Python
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
```

## Snippet 7
Lines 71-74

```Python
Returns:
        Dict with text response and metadata
    """
    client = init_cohere_client()
```

## Snippet 8
Lines 75-80

```Python
if not client:
        return {"text": "Error: Cohere API client initialization failed. Check your API key.", "error": True}

    # Select model
    model = model or os.environ.get("COHERE_MODEL", DEFAULT_TEXT_MODEL)
```

## Snippet 9
Lines 84-87

```Python
if system_message:
            messages.append({"role": "SYSTEM", "content": system_message})
        messages.append({"role": "USER", "content": prompt})
```

## Snippet 10
Lines 88-93

```Python
# Prepare parameters
    kwargs = {
        "model": model,
        "messages": messages
    }
```

## Snippet 11
Lines 98-101

```Python
if tools:
        kwargs["tools"] = tools

    # Temperature controls sampling randomness (0.0 to 1.0)
```

## Snippet 12
Lines 102-105

```Python
if temperature is not None:
        kwargs["temperature"] = temperature

    # Max tokens limits the response length
```

## Snippet 13
Lines 106-113

```Python
if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens

    try:
        response = client.chat(**kwargs)

        # Extract text from response
        text_response = ""
```

## Snippet 14
Lines 120-130

```Python
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
```

## Snippet 15
Lines 131-135

```Python
except Exception as e:
        error_msg = f"Error calling Cohere API: {str(e)}"
        console.print(f"[red]{error_msg}[/red]")
        return {"text": error_msg, "error": True}
```

## Snippet 16
Lines 136-138

```Python
def send_prompt_to_cohere(prompt: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a prompt to Cohere AI API.
```

## Snippet 17
Lines 139-142

```Python
This is a wrapper for process_with_cohere with simpler parameters.

    Args:
        prompt: The prompt to send
```

## Snippet 18
Lines 145-149

```Python
Returns:
        Dict with text response and metadata
    """
    return process_with_cohere(prompt=prompt)
```

## Snippet 19
Lines 150-169

```Python
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
```

## Snippet 20
Lines 170-177

```Python
def list_cohere_models() -> List[Dict[str, Any]]:
    """
    List available Cohere AI models.

    Returns:
        List of model information dictionaries
    """
    client = init_cohere_client()
```

## Snippet 21
Lines 178-217

```Python
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
```

## Snippet 22
Lines 220-225

```Python
if get_api_key():
        console.print("[green]Testing Cohere API connection...[/green]")
        result = send_prompt_to_cohere("Hello, what capabilities do you have?")
        console.print(f"Response: {result['text']}")
    else:
        console.print("[red]COHERE_API_KEY not set. Please set this environment variable to use Cohere API.[/red]")
```

