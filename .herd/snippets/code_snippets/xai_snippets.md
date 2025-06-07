# Code Snippets from toollama/API/--storage/processed-cli/xai.py

File: `toollama/API/--storage/processed-cli/xai.py`  
Language: Python  
Extracted: 2025-06-07 05:17:41  

## Snippet 1
Lines 1-18

```Python
"""
X.AI API Chat Implementation
This module provides an interface to the X.AI API with support for:
- Interactive model selection
- Response streaming
- Multimodal inputs (text + images)
"""

import os
import sys
from openai import OpenAI
from typing import Generator, List, Dict, Optional
from datetime import datetime
from base64 import b64encode
from PIL import Image
import io
import requests
```

## Snippet 2
Lines 20-32

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
Lines 33-36

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [self.conversation_history[0]]
```

## Snippet 4
Lines 37-49

```Python
def list_models(self) -> List[Dict]:
        """
        Retrieve available X.AI models dynamically.

        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Fetch models from the X.AI API
            response = self.client.models.list()

            # Process and format the models
            models = []
```

## Snippet 5
Lines 50-52

```Python
for model in response.data:
                # Extract capabilities from model metadata
                capabilities = []
```

## Snippet 6
Lines 53-60

```Python
if "vision" in model.id or "image" in model.id:
                    capabilities.append("images")
                capabilities.extend(["text", "code"])  # All models support text and code

                models.append({
                    "id": model.id,
                    "name": model.id.replace("-", " ").title(),
                    "capabilities": capabilities,
```

## Snippet 7
Lines 69-77

```Python
# Fallback to basic Grok model if API fails
            return [{
                "id": "grok-2-latest",
                "name": "Grok 2 Latest",
                "capabilities": ["text", "code", "images"],
                "context_window": 8192,
                "created_at": "2024-02-01"
            }]
```

## Snippet 8
Lines 78-86

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

## Snippet 9
Lines 87-103

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

## Snippet 10
Lines 105-131

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

## Snippet 11
Lines 133-137

```Python
if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    response_text += text
                    yield text
```

## Snippet 12
Lines 138-143

```Python
# Add assistant's response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
```

## Snippet 13
Lines 147-150

```Python
def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print("\nAvailable X.AI Models:")
    print("-" * 50)
```

## Snippet 14
Lines 162-165

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 15
Lines 168-172

```Python
def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = os.getenv("XAI_API_KEY") or "xai-8zAk5VIaL3Vxpu3fO3r2aiWqqeVAZ173X04VK2R1m425uYpWOIOQJM3puq1Q38xJ2sHfbq3mX4PBxJXC"
```

## Snippet 16
Lines 173-183

```Python
if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        sys.exit(1)

    chat = XAIChat(api_key)

    # Fetch and display available models
    models = chat.list_models()
    display_models(models)

    # Get model selection
```

## Snippet 17
Lines 184-186

```Python
while True:
        try:
            selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 18
Lines 201-206

```Python
default_prompt = "What do you see in this image?" if include_image else "Tell me a joke about AI"
        prompt = get_user_input("Enter your prompt", default_prompt)

        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
```

## Snippet 19
Lines 212-217

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

