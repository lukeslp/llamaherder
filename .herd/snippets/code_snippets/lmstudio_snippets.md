# Code Snippets from toollama/API/dev/lmstudio.py

File: `toollama/API/dev/lmstudio.py`  
Language: Python  
Extracted: 2025-06-07 05:17:05  

## Snippet 1
Lines 3-16

```Python
This module provides a simple interface to the LM Studio API for chat, text completion, and embeddings.
Supports streaming responses and multiple model types.
"""

import requests
import sys
import json
import os
import base64
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from PIL import Image
import io
```

## Snippet 2
Lines 18-25

```Python
def __init__(self, base_url: str = "https://api.assisted.space/v1"):
        """Initialize the LM Studio client with the base API URL."""
        self.base_url = base_url.rstrip('/')  # Keep /v1 in the endpoint calls
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
```

## Snippet 3
Lines 26-52

```Python
def list_models(
        self,
        sort_by: str = "id",
        reverse: bool = False,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Fetch available models from LM Studio API with pagination and filtering.

        Args:
            sort_by (str): Field to sort by ('id', 'type', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('chat', 'function', 'vision')

        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            response = requests.get(f"{self.base_url}/models")
            response.raise_for_status()

            # Process and enhance model data
            models = []
```

## Snippet 4
Lines 53-60

```Python
for model_data in response.json()["data"]:
                # Extract model ID and capabilities
                model_id = model_data["id"]

                # Determine model capabilities
                capabilities = ["chat"]  # All models support chat

                # Infer additional capabilities from model properties and ID
```

## Snippet 5
Lines 71-75

```Python
if capability_filter and capability_filter not in capabilities:
                    continue

                # Determine model type
                model_type = "chat"
```

## Snippet 6
Lines 78-90

```Python
elif any(x in model_id.lower() for x in ["llama", "mistral", "mixtral"]):
                    model_type = "llm"

                models.append({
                    "id": model_id,
                    "name": model_data.get("name", model_id).replace("-", " ").title(),
                    "type": model_type,
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": model_data.get("created", datetime.now().timestamp()),
                    "owned_by": model_data.get("owned_by", "local")
                })
```

## Snippet 7
Lines 94-104

```Python
elif sort_by == "capabilities":
                models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by id
                models.sort(key=lambda x: x["id"], reverse=reverse)

            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            return models[start_idx:end_idx]
```

## Snippet 8
Lines 105-108

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []
```

## Snippet 9
Lines 109-116

```Python
def get_model_info(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific model.

        Args:
            model_id (str): The ID of the model to query

        Returns:
```

## Snippet 10
Lines 118-126

```Python
"""
        try:
            response = requests.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()

            model_data = response.json()
            capabilities = ["chat"]  # Base capability

            # Infer additional capabilities
```

## Snippet 11
Lines 140-150

```Python
elif any(x in model_id.lower() for x in ["llama", "mistral", "mixtral"]):
                model_type = "llm"

            return {
                "id": model_id,
                "name": model_data.get("name", model_id).replace("-", " ").title(),
                "type": model_type,
                "capabilities": capabilities,
                "created": model_data.get("created", datetime.now().timestamp()),
                "owned_by": model_data.get("owned_by", "local")
            }
```

## Snippet 12
Lines 151-154

```Python
except Exception as e:
            print(f"Error fetching model info: {e}", file=sys.stderr)
            return None
```

## Snippet 13
Lines 155-165

```Python
def stream_chat_response(
        self,
        message: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = -1,
        image_data: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from LM Studio. Supports optional image data.
```

## Snippet 14
Lines 166-173

```Python
For vision-capable models, if image_data is provided the image is sent as a separate
        parameter with its base64 encoding prefixed (e.g., "data:image/png;base64,").
        Otherwise, the image is included using the standard message formatting.

        Args:
            message (str): The user's input message.
            model (str): The model to use.
            temperature (float): Response temperature (0.0 to 1.0).
```

## Snippet 15
Lines 177-180

```Python
Yields:
            str: Chunks of the response text as they arrive.
        """
        try:
```

## Snippet 16
Lines 182-197

```Python
if image_data and any(keyword in model.lower() for keyword in ['vision', 'image', 'multimodal']):
                # For vision models, attach the image as a separate key.
                self.chat_history.append({
                    "role": "user",
                    "content": message
                })
                payload = {
                    "model": model,
                    "messages": self.chat_history,
                    "image": f"data:image/png;base64,{image_data}",
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
            else:
                # For non-vision models or when no image data is provided,
```

## Snippet 17
Lines 198-211

```Python
# include the image (if any) as part of the message.
                content = self.format_message_with_image(message, image_data)
                self.chat_history.append({
                    "role": "user",
                    "content": content
                })
                payload = {
                    "model": model,
                    "messages": self.chat_history,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True
                }
```

## Snippet 18
Lines 212-221

```Python
response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                stream=True
            )
            response.raise_for_status()

            full_response = ""
            buffer = ""
```

## Snippet 19
Lines 223-226

```Python
if not line:
                    continue

                buffer += line.decode('utf-8') + "\n"
```

## Snippet 20
Lines 230-233

```Python
if "data: " in buffer:
                    chunks = buffer.split("data: ")
                    buffer = chunks[-1]  # retain the last incomplete chunk
```

## Snippet 21
Lines 236-240

```Python
if not chunk or chunk == "[DONE]":
                            continue

                        try:
                            data = json.loads(chunk)
```

## Snippet 22
Lines 243-246

```Python
if "content" in delta:
                                    content_chunk = delta["content"]
                                    full_response += content_chunk
                                    yield content_chunk
```

## Snippet 23
Lines 247-250

```Python
except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}", file=sys.stderr)
                            continue
```

## Snippet 24
Lines 251-256

```Python
if full_response:
                self.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })
```

## Snippet 25
Lines 259-262

```Python
if self.chat_history:
                self.chat_history.pop()  # Remove the latest user message on error
            yield f"Error: {str(e)}"
```

## Snippet 26
Lines 263-288

```Python
def text_completion(
        self,
        prompt: str,
        model: str = "pixtral-12b",
        temperature: float = 0.7,
        max_tokens: int = 10,
        stop: Optional[str] = "\n",
        file_path: Optional[str] = None
    ) -> str:
        """
        Generate a text completion. Supports optional file attachments (e.g., images).

        Args:
            prompt (str): The input prompt
            model (str): The model to use
            temperature (float): Response temperature (0.0 to 1.0)
            max_tokens (int): Maximum tokens in response
            stop (Optional[str]): Stop sequence
            file_path (Optional[str]): Path to a file (e.g., an image) to attach

        Returns:
            str: The generated completion
        """
        try:
            # Prepare the prompt content
            content = prompt
```

## Snippet 27
Lines 289-315

```Python
if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    base64_data = base64.b64encode(file_data).decode('utf-8')
                    content = [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{os.path.splitext(file_path)[1][1:]};base64,{base64_data}"
                            }
                        }
                    ]

            response = requests.post(
                f"{self.base_url}/v1/completions",
                json={
                    "model": model,
                    "prompt": content,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                    "stop": stop
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["text"]
```

## Snippet 28
Lines 316-319

```Python
except Exception as e:
            print(f"Error in text_completion: {e}", file=sys.stderr)
            return str(e)
```

## Snippet 29
Lines 320-325

```Python
def get_embeddings(
        self,
        text: str,
        model: str = "text-embedding-nomic-embed-text-v1.5"
    ) -> List[float]:
        """
```

## Snippet 30
Lines 326-348

```Python
Generate embeddings for input text.

        Args:
            text (str): The input text to embed
            model (str): The embedding model to use

        Returns:
            List[float]: The generated embedding vector
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                json={
                    "model": model,
                    "input": text
                }
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Error in get_embeddings: {e}", file=sys.stderr)
            return []
```

## Snippet 31
Lines 349-355

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
```

## Snippet 32
Lines 356-376

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> str:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
            str: Base64 encoded image data
        """
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None
```

## Snippet 33
Lines 377-384

```Python
def load_image_from_file(self, file_path: str) -> Optional[str]:
        """
        Load an image from a file and return its base64 encoding.

        Args:
            file_path (str): Path to the image file

        Returns:
```

## Snippet 34
Lines 386-388

```Python
"""
        try:
            with Image.open(file_path) as img:
```

## Snippet 35
Lines 393-399

```Python
if img.size[0] > 2048 or img.size[1] > 2048:
                    img.thumbnail((2048, 2048))
                # Save to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                return base64.b64encode(img_byte_arr).decode('utf-8')
```

## Snippet 36
Lines 400-403

```Python
except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None
```

## Snippet 37
Lines 404-408

```Python
def format_message_with_image(
        self,
        message: str,
        image_data: Optional[str] = None
    ) -> Union[str, List[Dict]]:
```

## Snippet 38
Lines 410-425

```Python
if not image_data:
            return message

        return [
            {
                "type": "text",
                "text": message
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_data}"
                }
            }
        ]
```

## Snippet 39
Lines 426-435

```Python
def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable LM Studio Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
```

## Snippet 40
Lines 436-439

```Python
if capability_filter:
        print(f"Filtering by capability: {capability_filter}")
    print("-" * 50)
```

## Snippet 41
Lines 440-447

```Python
for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Type: {model['type']}")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        print(f"   Owner: {model.get('owned_by', 'local')}")
        print()
```

## Snippet 42
Lines 452-455

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 43
Lines 458-474

```Python
def main():
    """Main CLI interface."""
    chat = LMStudioChat()

    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "id"
    capability_filter = None

    # Get initial full list of models
    all_models = chat.list_models(
        sort_by=sort_by,
        page=1,
        page_size=1000,
        capability_filter=capability_filter
    )
```

## Snippet 44
Lines 481-504

```Python
while True:
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            capability_filter=capability_filter
        )

        # Display models
        display_models(models, page, total_pages, sort_by, capability_filter)

        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (id/type/capabilities)")
        print("5. Filter by capability (chat/function/vision/completion/embeddings/none)")
        print("6. Change page size")
        print("7. Quit")

        choice = get_user_input("Select option", "1")
```

## Snippet 45
Lines 505-508

```Python
if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 46
Lines 523-537

```Python
elif choice == "4":
            # Sort by
            sort_by = get_user_input(
                "Sort by (id/type/capabilities)",
                "id"
            )
            # Refresh model list with new sorting
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
```

## Snippet 47
Lines 538-543

```Python
elif choice == "5":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (chat/function/vision/completion/embeddings/none)",
                "none"
            ).lower()
```

## Snippet 48
Lines 544-553

```Python
capability_filter = None if cap_choice == "none" else cap_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
```

## Snippet 49
Lines 554-557

```Python
elif choice == "6":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
```

## Snippet 50
Lines 558-561

```Python
if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1  # Reset to first page
```

## Snippet 51
Lines 577-585

```Python
if not supports_images:
            print("[Note: Selected model does not support image understanding]")
        print("1. No image")
        print("2. Test image (colored square)")
        print("3. Load image from file")

        image_choice = get_user_input("Select image option", "1")
        test_image = None
```

## Snippet 52
Lines 586-595

```Python
if image_choice == "2":
            # Create test image with custom color
            color = get_user_input("Enter color (e.g., red, blue, green)", "red")
            size_str = get_user_input("Enter size (width,height)", "100,100")
            try:
                width, height = map(int, size_str.split(","))
                test_image = chat.create_test_image(color=color, size=(width, height))
            except ValueError:
                print("Invalid size format. Using default 100x100...")
                test_image = chat.create_test_image(color=color)
```

## Snippet 53
Lines 596-599

```Python
elif image_choice == "3":
            # Load image from file
            file_path = get_user_input("Enter image file path")
            test_image = chat.load_image_from_file(file_path)
```

## Snippet 54
Lines 604-612

```Python
default_prompt = "What do you see in this image?" if test_image else "Tell me about yourself"
        message = get_user_input(
            "Enter your message",
            default_prompt
        )

        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
```

## Snippet 55
Lines 618-623

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

