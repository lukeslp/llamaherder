# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_chat_cohere.py

File: `toollama/API/--storage/processed-flask-chat/flask_chat_cohere.py`  
Language: Python  
Extracted: 2025-06-07 05:17:43  

## Snippet 1
Lines 4-18

```Python
This module provides a Flask interface to the Cohere API for streaming chat responses.
Supports model selection and multi-turn conversations with streaming responses.
"""

import os
import sys
import tempfile
import io
import json
import requests
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image
```

## Snippet 2
Lines 20-30

```Python
def __init__(self, api_key: str):
        """Initialize the Cohere client with the provided API key."""
        self.api_key = api_key
        self.base_url = 'https://api.cohere.com/v2'
        self.dataset_url = 'https://api.cohere.com/v1/datasets'
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
```

## Snippet 3
Lines 31-42

```Python
def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 1000,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available Cohere models.

        Args:
            sort_by (str): Field to sort by (created/id/capabilities)
```

## Snippet 4
Lines 47-55

```Python
Returns:
            List[Dict]: List of available models with their details
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
```

## Snippet 5
Lines 56-64

```Python
# Get models filtered for chat endpoint
            response = requests.get(
                "https://api.cohere.com/v1/models",  # Models endpoint still v1
                headers=headers,
                params={"endpoint": "chat"}
            )
            response.raise_for_status()

            models = []
```

## Snippet 6
Lines 65-67

```Python
for model in response.json()["models"]:
                # Extract capabilities from model info
                capabilities = []
```

## Snippet 7
Lines 70-75

```Python
if model.get("finetuned"):
                    capabilities.append("finetuned")

                models.append({
                    "id": model["name"],
                    "name": model["name"],
```

## Snippet 8
Lines 76-82

```Python
"description": f"Cohere {model['name']} model",
                    "endpoints": model["endpoints"],
                    "context_length": model.get("context_length", 4096),
                    "is_finetuned": model.get("finetuned", False),
                    "capabilities": capabilities,
                    "created_at": datetime.now().isoformat(),
                    "owned_by": "Cohere"
```

## Snippet 9
Lines 92-101

```Python
elif sort_by == "capabilities":
                models.sort(key=lambda x: len(x["capabilities"]), reverse=True)
            else:  # sort by id
                models.sort(key=lambda x: x["id"])

            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
```

## Snippet 10
Lines 104-126

```Python
# Fallback to known models if API fails
            return [{
                "id": "command-r-plus-08-2024",
                "name": "command-r-plus-08-2024",
                "description": "Cohere Command-R Plus model",
                "endpoints": ["chat"],
                "context_length": 4096,
                "is_finetuned": False,
                "capabilities": ["chat"],
                "created_at": datetime.now().isoformat(),
                "owned_by": "Cohere"
            }, {
                "id": "command-light",
                "name": "command-light",
                "description": "Cohere Command Light model",
                "endpoints": ["chat"],
                "context_length": 4096,
                "is_finetuned": False,
                "capabilities": ["chat"],
                "created_at": datetime.now().isoformat(),
                "owned_by": "Cohere"
            }]
```

## Snippet 11
Lines 127-182

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = "command-r-plus-08-2024",
        temperature: float = 0.3,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Cohere.

        Args:
            message (str): The user's input message
            model (str): The Cohere model to use
            temperature (float): Response temperature (0.0 to 1.0)
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            file_data (Optional[str]): Base64 encoded file data
            is_url (bool): Whether image_data contains URLs

        Yields:
            str: Chunks of the response text as they arrive
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Format message content based on whether we have attachments
        content = self.format_message_with_attachments(message, image_data, file_data, is_url)

        # Add user message to history
        self.chat_history.append({
            "role": "user",
            "content": content
        })

        payload = {
            "model": model,
            "messages": self.chat_history,
            "temperature": temperature,
            "stream": True,
            "connectors": [{"id":"web-search"}]
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()

            full_response = ""
```

## Snippet 12
Lines 184-186

```Python
if line:
                    try:
                        line_text = line.decode('utf-8')
```

## Snippet 13
Lines 197-202

```Python
except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 14
Lines 203-208

```Python
# Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })
```

## Snippet 15
Lines 220-226

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
```

## Snippet 16
Lines 227-234

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 17
Lines 236-243

```Python
"""
        try:
            with open(image_path, "rb") as image_file:
                return b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 18
Lines 244-252

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
```

## Snippet 19
Lines 254-264

```Python
"""
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None
```

## Snippet 20
Lines 265-271

```Python
def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 21
Lines 273-278

```Python
if not image_data and not file_data:
            return message

        content = [{"type": "text", "text": message}]

        # Add images
```

## Snippet 22
Lines 285-297

```Python
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
```

## Snippet 23
Lines 299-305

```Python
if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{base64.b64decode(file_data).decode('utf-8', errors='ignore')}"
            })

        return content
```

