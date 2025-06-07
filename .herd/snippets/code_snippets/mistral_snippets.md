# Code Snippets from build/lib/herd_ai/utils/mistral.py

File: `build/lib/herd_ai/utils/mistral.py`  
Language: Python  
Extracted: 2025-06-07 05:09:19  

## Snippet 1
Lines 3-20

```Python
This module provides integration with the Mistral AI API for the Herd AI system.
Supports sending text prompts, image processing, and streaming responses.

References:
- Mistral API Documentation: https://docs.mistral.ai/api/
"""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from rich.console import Console
import io
from PIL import Image
```

## Snippet 2
Lines 28-31

```Python
def get_api_key() -> Optional[str]:
    """Get the Mistral API key from environment variables."""
    return os.environ.get("MISTRAL_API_KEY")
```

## Snippet 3
Lines 32-54

```Python
def process_with_mistral(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 1.0,
    safe_prompt: bool = True,
    stream: bool = False,
    messages: Optional[List[Dict[str, str]]] = None,
    system_message: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a prompt with Mistral AI API.

    Args:
        prompt: The prompt to send to the API
        model: Model name (defaults to MISTRAL_TEXT_MODEL env var or mistral-medium)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        top_p: Controls diversity via nucleus sampling
        safe_prompt: Whether to enable Mistral's safety filters
        stream: Whether to stream the response (not used in this function)
```

## Snippet 4
Lines 59-62

```Python
Returns:
        Dict with text response and metadata
    """
    api_key = get_api_key()
```

## Snippet 5
Lines 63-75

```Python
if not api_key:
        return {"text": "Error: MISTRAL_API_KEY environment variable not set", "error": True}

    # Select model
    model = model or os.environ.get("MISTRAL_TEXT_MODEL", DEFAULT_TEXT_MODEL)

    # API URL and headers
    api_url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
```

## Snippet 6
Lines 79-81

```Python
if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
```

## Snippet 7
Lines 82-92

```Python
elif not any(msg.get("role") == "system" for msg in messages) and system_message:
        messages.insert(0, {"role": "system", "content": system_message})

    # Prepare the request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "safe_prompt": safe_prompt
    }
```

## Snippet 8
Lines 93-112

```Python
if max_tokens:
        payload["max_tokens"] = max_tokens

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Extract text from response
        text_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Return in the expected format
        return {
            "text": text_response,
            "model": model,
            "usage": result.get("usage", {}),
            "error": False
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Error calling Mistral API: {str(e)}"
```

## Snippet 9
Lines 113-119

```Python
if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = f"Mistral API error: {error_data.get('error', {}).get('message', str(e))}"
            except:
                pass
        return {"text": error_msg, "error": True}
```

## Snippet 10
Lines 123-145

```Python
def process_image_with_mistral(
    image_path: str,
    prompt: str = "Describe this image in detail",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 1.0
) -> Dict[str, Any]:
    """
    Process an image with Mistral AI API.

    Args:
        image_path: Path to the image file
        prompt: Text prompt to accompany the image
        model: Model name (defaults to MISTRAL_IMAGE_MODEL env var or mistral-medium)
        temperature: Controls randomness (0.0 to 1.0)
        max_tokens: Maximum number of tokens to generate
        top_p: Controls diversity via nucleus sampling

    Returns:
        Dict with text response and metadata
    """
    api_key = get_api_key()
```

## Snippet 11
Lines 146-161

```Python
if not api_key:
        return {"text": "Error: MISTRAL_API_KEY environment variable not set", "error": True}

    # Select model
    model = model or os.environ.get("MISTRAL_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)

    # API URL and headers
    api_url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Load and encode the image
    try:
        image_path = Path(image_path)
```

## Snippet 12
Lines 162-166

```Python
if not image_path.exists():
            return {"text": f"Error: Image file not found: {image_path}", "error": True}

        # Encode image to base64
        with Image.open(image_path) as img:
```

## Snippet 13
Lines 168-172

```Python
if img.width > 1024 or img.height > 1024:
                ratio = min(1024/img.width, 1024/img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
```

## Snippet 14
Lines 174-180

```Python
if img.mode != 'RGB':
                img = img.convert('RGB')

            # Encode to base64
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
```

## Snippet 15
Lines 181-198

```Python
except Exception as e:
        return {"text": f"Error processing image: {str(e)}", "error": True}

    # Prepare the content with image
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
    ]

    # Prepare the request payload
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": content}
        ],
        "temperature": temperature,
        "top_p": top_p
    }
```

## Snippet 16
Lines 199-211

```Python
if max_tokens:
        payload["max_tokens"] = max_tokens

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Extract text from response
        text_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Process the response into components
        try:
```

## Snippet 17
Lines 216-225

```Python
# Return structured data if it contains expected fields
                return {
                    "text": text_response,
                    "alt_text": json_data.get("alt_text", ""),
                    "description": json_data.get("description", ""),
                    "categories": json_data.get("categories", []),
                    "suggested_filename": json_data.get("suggested_filename", ""),
                    "model": model,
                    "error": False
                }
```

## Snippet 18
Lines 226-232

```Python
except:
            # If not JSON or missing fields, return the raw text
            pass

        # Default return format with entire text
        return {
            "text": text_response,
```

## Snippet 19
Lines 233-238

```Python
"alt_text": text_response.split("\n")[0] if "\n" in text_response else text_response[:100],
            "description": text_response,
            "categories": [],
            "suggested_filename": "",
            "model": model,
            "error": False
```

## Snippet 20
Lines 242-248

```Python
if hasattr(e, "response") and e.response is not None:
            try:
                error_data = e.response.json()
                error_msg = f"Mistral API error: {error_data.get('error', {}).get('message', str(e))}"
            except:
                pass
        return {"text": error_msg, "error": True}
```

## Snippet 21
Lines 252-254

```Python
def send_prompt_to_mistral(prompt: str, description: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a prompt to Mistral AI API.
```

## Snippet 22
Lines 255-258

```Python
This is a wrapper for process_with_mistral with simpler parameters.

    Args:
        prompt: The prompt to send
```

## Snippet 23
Lines 261-265

```Python
Returns:
        Dict with text response and metadata
    """
    return process_with_mistral(prompt=prompt)
```

## Snippet 24
Lines 266-272

```Python
def send_image_prompt_to_mistral(
    image_path: str,
    prompt: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an image prompt to Mistral AI API.
```

## Snippet 25
Lines 273-277

```Python
This is a wrapper for process_image_with_mistral with simpler parameters.

    Args:
        image_path: Path to the image file
        prompt: Text prompt to accompany the image
```

## Snippet 26
Lines 280-284

```Python
Returns:
        Dict with text response and metadata
    """
    return process_image_with_mistral(image_path=image_path, prompt=prompt)
```

## Snippet 27
Lines 285-304

```Python
def send_chat_to_mistral(
    messages: List[Dict[str, str]],
    system_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a chat conversation to Mistral AI API.

    Args:
        messages: List of message dictionaries
        system_message: Optional system message

    Returns:
        Dict with text response and metadata
    """
    return process_with_mistral(
        prompt="",  # Not used directly with messages parameter
        messages=messages,
        system_message=system_message
    )
```

## Snippet 28
Lines 305-312

```Python
def list_mistral_models() -> List[Dict[str, Any]]:
    """
    List available Mistral AI models.

    Returns:
        List of model information dictionaries
    """
    api_key = get_api_key()
```

## Snippet 29
Lines 313-328

```Python
if not api_key:
        console.print("[yellow]Warning: MISTRAL_API_KEY environment variable not set[/yellow]")
        return []

    api_url = "https://api.mistral.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        models = []
```

## Snippet 30
Lines 329-342

```Python
for model in data.get("data", []):
            models.append({
                "id": model["id"],
                "name": model.get("name", model["id"]),
                "created": model.get("created"),
                "description": model.get("description", ""),
                "context_length": model.get("max_context_length", 0),
                "capabilities": {
                    "chat": model.get("capabilities", {}).get("completion_chat", False),
                    "vision": model.get("capabilities", {}).get("vision", False),
                    "function_calling": model.get("capabilities", {}).get("function_calling", False)
                }
            })
        return models
```

## Snippet 31
Lines 343-346

```Python
except Exception as e:
        console.print(f"[red]Error listing Mistral models: {e}[/red]")
        return []
```

## Snippet 32
Lines 349-354

```Python
if get_api_key():
        console.print("[green]Testing Mistral API connection...[/green]")
        result = send_prompt_to_mistral("Hello, what capabilities do you have?")
        console.print(f"Response: {result['text']}")
    else:
        console.print("[red]MISTRAL_API_KEY not set. Please set this environment variable to use Mistral API.[/red]")
```

