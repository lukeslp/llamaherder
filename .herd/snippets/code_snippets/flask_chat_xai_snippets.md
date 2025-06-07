# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_chat_xai.py

File: `toollama/API/--storage/processed-flask-chat/flask_chat_xai.py`  
Language: Python  
Extracted: 2025-06-07 05:17:45  

## Snippet 1
Lines 3-20

```Python
X.AI API Chat Implementation for Flask
This module provides a Flask interface to the X.AI API with support for:
- Interactive model selection
- Response streaming
- Multimodal inputs (text + images)
"""

import os
import sys
import tempfile
import io
import json
from openai import OpenAI
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image
```

## Snippet 2
Lines 22-34

```Python
def __init__(self, api_key: str):
        """Initialize the X.AI client with the provided API key."""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
            }
        ]
```

## Snippet 3
Lines 35-38

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [self.conversation_history[0]]
```

## Snippet 4
Lines 39-50

```Python
def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 1000,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available X.AI models dynamically.

        Args:
            sort_by (str): Field to sort by (created/capabilities/id)
```

## Snippet 5
Lines 55-63

```Python
Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Fetch models from the X.AI API
            response = self.client.models.list()

            # Process and format the models
            models = []
```

## Snippet 6
Lines 64-66

```Python
for model in response.data:
                # Extract capabilities from model metadata
                capabilities = []
```

## Snippet 7
Lines 67-73

```Python
if "vision" in model.id or "image" in model.id:
                    capabilities.append("images")
                capabilities.extend(["text", "code"])  # All models support text and code

                model_data = {
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
```

## Snippet 8
Lines 81-85

```Python
if capability_filter and capability_filter not in capabilities:
                    continue

                models.append(model_data)
```

## Snippet 9
Lines 89-98

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
Lines 101-110

```Python
# Fallback to basic Grok model if API fails
            return [{
                "id": "grok-2-latest",
                "name": "Grok 2 Latest",
                "description": "X.AI Grok 2 base model",
                "capabilities": ["text", "code", "images"],
                "context_window": 8192,
                "created_at": "2024-02-01"
            }]
```

## Snippet 11
Lines 111-118

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 12
Lines 120-127

```Python
"""
        try:
            with open(image_path, "rb") as image_file:
                return b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 13
Lines 128-136

```Python
def create_test_image(self) -> str:
        """Create a simple test image and return its base64 encoding."""
        # Create a 100x100 red square image
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return b64encode(img_byte_arr).decode('utf-8')
```

## Snippet 14
Lines 137-153

```Python
def stream_chat_response(
        self,
        prompt: str,
        model: str,
        image: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from X.AI.

        Args:
            prompt (str): The user's input message
            model (str): The X.AI model to use
            image (Optional[str]): Base64 encoded image data

        Yields:
            str: Chunks of the response text as they arrive
        """
```

## Snippet 15
Lines 155-181

```Python
if image:
            message_content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image}"
                    }
                }
            ]
        else:
            message_content = prompt

        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": message_content
        })

        try:
            stream = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                stream=True
            )

            response_text = ""
```

## Snippet 16
Lines 183-187

```Python
if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    yield text
```

## Snippet 17
Lines 188-193

```Python
# Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
```

