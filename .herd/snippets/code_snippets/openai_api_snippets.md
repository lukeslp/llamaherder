# Code Snippets from toollama/API/--storage/processed-cli/openai_api.py

File: `toollama/API/--storage/processed-cli/openai_api.py`  
Language: Python  
Extracted: 2025-06-07 05:17:38  

## Snippet 1
Lines 3-15

```Python
This module provides a simple interface to the OpenAI API for streaming chat responses.
Supports model selection, multi-turn conversations, and image analysis with streaming responses.
"""

from openai import OpenAI
import sys
import base64
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from PIL import Image
import io
import os
```

## Snippet 2
Lines 16-44

```Python
class OpenAIChat:
    # Default models in case API fetch fails
    DEFAULT_MODELS = {
        "gpt-4-vision-preview": {
            "id": "gpt-4-vision-preview",
            "context_length": 128000,
            "description": "GPT-4 Turbo with image understanding",
            "capabilities": ["text", "vision", "function"]
        },
        "gpt-4-0125-preview": {
            "id": "gpt-4-0125-preview",
            "context_length": 128000,
            "description": "Most capable GPT-4 model",
            "capabilities": ["text", "function"]
        },
        "gpt-4": {
            "id": "gpt-4",
            "context_length": 8192,
            "description": "More capable GPT-4 model",
            "capabilities": ["text", "function"]
        },
        "gpt-3.5-turbo-0125": {
            "id": "gpt-3.5-turbo-0125",
            "context_length": 16385,
            "description": "Most capable GPT-3.5 model",
            "capabilities": ["text", "function"]
        }
    }
```

## Snippet 3
Lines 49-54

```Python
def patched_init(self, api_key: str, **kwargs):
                kwargs.pop('proxies', None)
                original_init(self, api_key=api_key, **kwargs)
            OpenAI.__init__ = patched_init
            OpenAI._patched_no_proxies = True
```

## Snippet 4
Lines 55-62

```Python
self.client = OpenAI(api_key=api_key)
        self.models = self._fetch_models()
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
```

## Snippet 5
Lines 63-73

```Python
def _fetch_models(self) -> Dict:
        """
        Fetch available models from OpenAI API.

        Returns:
            Dict: Dictionary of available models with their details
        """
        try:
            models = {}
            response = self.client.models.list()
```

## Snippet 6
Lines 75-78

```Python
for model in response.data:
                model_id = model.id
                created = datetime.fromtimestamp(model.created)
```

## Snippet 7
Lines 95-98

```Python
elif "128k" in model_id or "vision" in model_id:
                        context_length = 128000

                    # Create model description
```

## Snippet 8
Lines 104-107

```Python
if "vision" in model_id:
                        description += " with image understanding"

                    # Determine model generation and version
```

## Snippet 9
Lines 109-123

```Python
version = "preview" if "preview" in model_id else model_id.split('-')[-1] if '-' in model_id else None

                    models[model_id] = {
                        "id": model_id,
                        "context_length": context_length,
                        "description": description,
                        "capabilities": capabilities,
                        "capability_count": len(capabilities),
                        "created": created,
                        "created_str": created.strftime("%Y-%m-%d"),
                        "generation": generation,
                        "version": version,
                        "owned_by": model.owned_by
                    }
```

## Snippet 10
Lines 126-129

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return self.DEFAULT_MODELS
```

## Snippet 11
Lines 130-165

```Python
def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        generation: Optional[str] = None
    ) -> List[Dict]:
        """
        Get available OpenAI models with sorting and pagination.

        Args:
            sort_by (str): Field to sort by ('created', 'context_length', 'id', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            generation (Optional[str]): Filter by model generation ('4', '3.5', '3')

        Returns:
            List[Dict]: List of available models with their details
        """
        # Convert models to list and optionally filter by generation
        models_list = [
            {
                "id": info["id"],
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "capability_count": info["capability_count"],
                "created": info["created"],
                "created_str": info["created_str"],
                "generation": info["generation"],
                "version": info["version"],
                "owned_by": info["owned_by"]
            }
```

## Snippet 12
Lines 175-190

```Python
elif sort_by == "capabilities":
            # Sort by number of capabilities first, then by specific capabilities
            models_list.sort(key=lambda x: (
                x["capability_count"],
                "images" in x["capabilities"],
                "text" in x["capabilities"]
            ), reverse=reverse)
        else:  # sort by id
            models_list.sort(key=lambda x: x["id"], reverse=reverse)

        # Calculate pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return models_list[start_idx:end_idx]
```

## Snippet 13
Lines 191-198

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 14
Lines 200-207

```Python
"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 15
Lines 208-216

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
```

## Snippet 16
Lines 218-228

```Python
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

## Snippet 17
Lines 229-233

```Python
def create_test_file(self, content: str = None) -> str:
        """
        Create a test text file and return its base64 encoding.

        Args:
```

## Snippet 18
Lines 236-238

```Python
Returns:
            str: Base64 encoded file content
        """
```

## Snippet 19
Lines 239-242

```Python
if not content:
            content = "This is a test file.\nIt contains multiple lines.\nHello, GPT!"
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')
```

## Snippet 20
Lines 243-250

```Python
def encode_file(self, file_path: str) -> Optional[str]:
        """
        Encode a file to base64.

        Args:
            file_path (str): Path to the file

        Returns:
```

## Snippet 21
Lines 252-259

```Python
"""
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file: {e}", file=sys.stderr)
            return None
```

## Snippet 22
Lines 260-265

```Python
def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 23
Lines 267-270

```Python
if not image_data:
            return message

        # Convert single image to list
```

## Snippet 24
Lines 277-289

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

## Snippet 25
Lines 292-298

```Python
def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 26
Lines 300-305

```Python
if not image_data and not file_data:
            return message

        content = [{"type": "text", "text": message}]

        # Add images
```

## Snippet 27
Lines 312-324

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

## Snippet 28
Lines 326-333

```Python
if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{base64.b64decode(file_data).decode('utf-8', errors='ignore')}"
            })

        return content
```

## Snippet 29
Lines 334-366

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = "gpt-3.5-turbo-0125",
        temperature: float = 0.7,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from OpenAI.

        Args:
            message (str): The user's input message
            model (str): The OpenAI model to use
            temperature (float): Response temperature (0.0 to 1.0)
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            file_data (Optional[str]): Base64 encoded file data
            is_url (bool): Whether image_data contains URLs

        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Format message content based on whether we have attachments
            content = self.format_message_with_attachments(message, image_data, file_data, is_url)

            # Add user message to history
            self.chat_history.append({
                "role": "user",
                "content": content
            })
```

## Snippet 30
Lines 370-379

```Python
if isinstance(msg["content"], list):
                    # This is a message with attachments, keep as is
                    messages.append(msg)
                else:
                    # Text-only message
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
```

## Snippet 31
Lines 381-390

```Python
model_id = self.models[model]["id"] if model in self.models else model

            stream = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            full_response = ""
```

## Snippet 32
Lines 392-396

```Python
if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield text
```

## Snippet 33
Lines 397-402

```Python
# Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })
```

## Snippet 34
Lines 406-409

```Python
if self.chat_history:
                self.chat_history.pop()
            yield f"Error: {str(e)}"
```

## Snippet 35
Lines 410-416

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
```

## Snippet 36
Lines 417-425

```Python
def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    generation: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable OpenAI Models (Page {current_page}/{total_pages}):")
```

## Snippet 37
Lines 447-450

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 38
Lines 453-466

```Python
def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = "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"

    chat = OpenAIChat(api_key)

    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "created"
    generation = None
    capability_filter = None
```

## Snippet 39
Lines 478-487

```Python
total_pages = (len(all_models) + page_size - 1) // page_size

        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            generation=generation
        )
```

## Snippet 40
Lines 495-510

```Python
# Display models
        display_models(models, page, total_pages, sort_by, generation)

        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (created/context_length/id/capabilities)")
        print("5. Filter by generation (4/3.5/3/none)")
        print("6. Filter by capability (text/function/vision/none)")
        print("7. Change page size")
        print("8. Quit")

        choice = get_user_input("Select option", "1")
```

## Snippet 41
Lines 511-514

```Python
if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 42
Lines 529-535

```Python
elif choice == "4":
            # Sort by
            sort_by = get_user_input(
                "Sort by (created/context_length/id/capabilities)",
                "created"
            )
            page = 1  # Reset to first page
```

## Snippet 43
Lines 536-541

```Python
elif choice == "5":
            # Filter by generation
            gen = get_user_input(
                "Filter by generation (4/3.5/3/none)",
                "none"
            )
```

## Snippet 44
Lines 544-549

```Python
elif choice == "6":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (text/function/vision/none)",
                "none"
            ).lower()
```

## Snippet 45
Lines 552-555

```Python
elif choice == "7":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
```

## Snippet 46
Lines 556-558

```Python
if new_size > 0:
                    page_size = new_size
                    page = 1  # Reset to first page
```

## Snippet 47
Lines 574-589

```Python
if not supports_images:
            print("[Note: Selected model does not support image understanding]")

        print("\nAttachment options:")
        print("1. Text only")
        print("2. Test image (colored square)")
        print("3. Load image from file")
        print("4. Image from URL")
        print("5. Test file (sample text)")
        print("6. Load file from disk")

        input_choice = get_user_input("Select input option", "1")
        image_data = None
        file_data = None
        is_url = False
```

## Snippet 48
Lines 590-596

```Python
if input_choice == "2" and supports_images:
            # Create test image with custom color
            color = get_user_input("Enter color (e.g., red, blue, green)", "red")
            size_str = get_user_input("Enter size (width,height)", "100,100")
            try:
                width, height = map(int, size_str.split(","))
                image_data = chat.create_test_image(color=color, size=(width, height))
```

## Snippet 49
Lines 599-601

```Python
except ValueError:
                print("Invalid size format. Using default 100x100...")
                image_data = chat.create_test_image(color=color)
```

## Snippet 50
Lines 602-605

```Python
elif input_choice == "3" and supports_images:
            # Load image from file
            file_path = get_user_input("Enter image file path")
            image_data = chat.encode_image(file_path)
```

## Snippet 51
Lines 611-613

```Python
if url:
                image_data = url
                is_url = True
```

## Snippet 52
Lines 618-621

```Python
elif input_choice == "6":
            # Load file from disk
            file_path = get_user_input("Enter file path")
            file_data = chat.encode_file(file_path)
```

## Snippet 53
Lines 626-634

```Python
default_prompt = "What do you see in this image?" if image_data else "Please analyze this file" if file_data else "Hello! How can I help you today?"
        message = get_user_input(
            "Enter your message",
            default_prompt
        )

        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
```

## Snippet 54
Lines 635-645

```Python
for chunk in chat.stream_chat_response(
            message,
            selected_model,
            image_data=image_data,
            file_data=file_data,
            is_url=is_url
        ):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 50)

        # Ask to continue
```

## Snippet 55
Lines 646-651

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

