# Code Snippets from toollama/API/--storage/processed-cli/mistral_chat.py

File: `toollama/API/--storage/processed-cli/mistral_chat.py`  
Language: Python  
Extracted: 2025-06-07 05:17:35  

## Snippet 1
Lines 3-16

```Python
This module provides a simple interface to the Mistral AI API for streaming chat responses.
Supports model selection, multi-turn conversations, and image analysis with streaming responses.
"""

import os
import sys
import requests
import json
import base64
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from PIL import Image
import io
```

## Snippet 2
Lines 18-31

```Python
def __init__(self, api_key: str):
        """Initialize the Mistral client with the provided API key."""
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Initialize with system message
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 3
Lines 32-62

```Python
def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available Mistral models with pagination.

        Args:
            sort_by (str): Field to sort by ('created', 'id', 'context_length')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('chat', 'function', 'vision')
            category_filter (Optional[str]): Filter models by category ('mistral', 'mixtral', 'pixtral')

        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            response = requests.get(
                f"{self.api_url}/models",
                headers=self.headers
            )
            response.raise_for_status()

            models = []
```

## Snippet 4
Lines 77-81

```Python
elif "pixtral" in model_id:
                    category = "pixtral"
                else:
                    category = "mistral"
```

## Snippet 5
Lines 85-90

```Python
if category_filter and category_filter != category:
                    continue

                models.append({
                    "id": model["id"],
                    "name": model["name"] or model["id"].replace("-", " ").title(),
```

## Snippet 6
Lines 91-98

```Python
"description": model["description"] or f"Mistral {model['id']} model",
                    "context_length": model["max_context_length"],
                    "created_at": datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                    "created": model["created"],
                    "capabilities": capabilities,
                    "category": category,
                    "owned_by": model["owned_by"],
                    "deprecated_at": model.get("deprecation")
```

## Snippet 7
Lines 104-114

```Python
elif sort_by == "context_length":
                models.sort(key=lambda x: x["context_length"], reverse=reverse)
            else:  # sort by id
                models.sort(key=lambda x: x["id"], reverse=reverse)

            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            return models[start_idx:end_idx]
```

## Snippet 8
Lines 121-127

```Python
"description": "Fast and efficient model for simple tasks",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat"],
                "category": "mistral",
                "owned_by": "mistralai"
```

## Snippet 9
Lines 131-137

```Python
"description": "Balanced model for general use",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
```

## Snippet 10
Lines 141-147

```Python
"description": "More capable model for complex tasks",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
```

## Snippet 11
Lines 162-166

```Python
# Apply pagination to fallback models
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return fallback_models[start_idx:end_idx]
```

## Snippet 12
Lines 167-175

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
```

## Snippet 13
Lines 177-187

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

## Snippet 14
Lines 188-196

```Python
def load_image_from_file(self, file_path: str) -> Optional[str]:
        """
        Load an image from a file and return its base64 encoding.
        Supports PNG, JPEG, WEBP, and single-frame GIF formats.

        Args:
            file_path (str): Path to the image file

        Returns:
```

## Snippet 15
Lines 198-201

```Python
"""
        try:
            with Image.open(file_path) as img:
                # Check file format
```

## Snippet 16
Lines 202-206

```Python
if img.format not in ['PNG', 'JPEG', 'WEBP', 'GIF']:
                    print(f"Unsupported image format: {img.format}. Must be PNG, JPEG, WEBP, or single-frame GIF.",
                          file=sys.stderr)
                    return None
```

## Snippet 17
Lines 208-211

```Python
if img.format == 'GIF' and getattr(img, 'is_animated', False):
                    print("Animated GIFs are not supported.", file=sys.stderr)
                    return None
```

## Snippet 18
Lines 213-218

```Python
if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Check file size (max 10MB)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
```

## Snippet 19
Lines 219-222

```Python
if img_byte_arr.tell() > 10 * 1024 * 1024:  # 10MB in bytes
                    print("Image file size exceeds 10MB limit.", file=sys.stderr)
                    return None
```

## Snippet 20
Lines 224-235

```Python
if img.size[0] > 1024 or img.size[1] > 1024:
                    # Calculate new dimensions maintaining aspect ratio
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Convert to base64
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                return base64.b64encode(img_byte_arr).decode('utf-8')
```

## Snippet 21
Lines 236-239

```Python
except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None
```

## Snippet 22
Lines 240-246

```Python
def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """
```

## Snippet 23
Lines 247-254

```Python
Format a message with optional image data for the API.

        Args:
            message (str): The text message
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            is_url (bool): Whether image_data contains URLs

        Returns:
```

## Snippet 24
Lines 257-260

```Python
if not image_data:
            return message

        # Convert single image to list
```

## Snippet 25
Lines 265-270

```Python
if len(image_data) > 8:
            print("Warning: Maximum 8 images per request. Using first 8 images.", file=sys.stderr)
            image_data = image_data[:8]

        content = [{"type": "text", "text": message}]
```

## Snippet 26
Lines 272-282

```Python
if is_url:
                content.append({
                    "type": "image_url",
                    "image_url": img
                })
            else:
                content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{img}"
                })
```

## Snippet 27
Lines 285-290

```Python
def format_message_with_file(
        self,
        message: str,
        file_data: Optional[Union[str, List[str]]] = None
    ) -> Union[str, List[Dict]]:
        """
```

## Snippet 28
Lines 291-297

```Python
Format a message with optional file data for the API.

        Args:
            message (str): The text message
            file_data (Optional[Union[str, List[str]]]): File ID(s) from Mistral API

        Returns:
```

## Snippet 29
Lines 300-303

```Python
if not file_data:
            return message

        # Convert single file ID to list
```

## Snippet 30
Lines 309-316

```Python
for file_id in file_data:
            content.append({
                "type": "file",
                "file_id": file_id
            })

        return content
```

## Snippet 31
Lines 317-347

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = "mistral-tiny",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        safe_prompt: bool = True,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False,
        file_data: Optional[Union[str, List[str]]] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Mistral.

        Args:
            message (str): The user's input message
            model (str): The Mistral model to use
            temperature (float): Response temperature (0.0 to 1.5)
            max_tokens (Optional[int]): Maximum tokens to generate
            top_p (float): Nucleus sampling parameter (0.0 to 1.0)
            safe_prompt (bool): Whether to use safety prompts
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            is_url (bool): Whether image_data contains URLs
            file_data (Optional[Union[str, List[str]]]): File ID(s) from Mistral API

        Yields:
            str: Chunks of the response text as they arrive
        """
        # Format message content based on whether we have images or files
        content = message
```

## Snippet 32
Lines 350-367

```Python
elif file_data:
            content = self.format_message_with_file(message, file_data)

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": content
        })

        payload = {
            "model": model,
            "messages": self.conversation_history,
            "stream": True,
            "temperature": temperature,
            "top_p": top_p,
            "safe_prompt": safe_prompt
        }
```

## Snippet 33
Lines 368-380

```Python
if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()

            full_response = ""
```

## Snippet 34
Lines 386-391

```Python
if line_text == "[DONE]":
                        continue

                    try:
                        data = json.loads(line_text)
                        content = data['choices'][0]['delta'].get('content', '')
```

## Snippet 35
Lines 392-394

```Python
if content:
                            full_response += content
                            yield content
```

## Snippet 36
Lines 395-400

```Python
except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 37
Lines 401-406

```Python
# Add assistant's response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })
```

## Snippet 38
Lines 411-415

```Python
except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            self.conversation_history.pop()
            yield f"Error: {str(e)}"
```

## Snippet 39
Lines 416-422

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 40
Lines 423-430

```Python
def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to Mistral's servers and return the file ID.

        Args:
            file_path (str): Path to the file to upload

        Returns:
```

## Snippet 41
Lines 432-443

```Python
"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                upload_headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.post(f"{self.api_url}/files", headers=upload_headers, files=files)
                response.raise_for_status()
                return response.json().get("id")
        except Exception as e:
            print(f"Error uploading file: {e}", file=sys.stderr)
            return None
```

## Snippet 42
Lines 444-454

```Python
def list_files(self, purpose: Optional[str] = None) -> List[Dict]:
        """
        List files uploaded to Mistral.

        Args:
            purpose (Optional[str]): Filter by purpose ('fine-tune', 'assistants')

        Returns:
            List[Dict]: List of file metadata
        """
        try:
```

## Snippet 43
Lines 455-462

```Python
params = {"purpose": purpose} if purpose else {}
            response = requests.get(
                f"{self.api_url}/files",
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            return response.json()["data"]
```

## Snippet 44
Lines 463-466

```Python
except Exception as e:
            print(f"Error listing files: {e}", file=sys.stderr)
            return []
```

## Snippet 45
Lines 469-487

```Python
Retrieve metadata for a specific file.

        Args:
            file_id (str): ID of the file to retrieve

        Returns:
            Dict: File metadata
        """
        try:
            response = requests.get(
                f"{self.api_url}/files/{file_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving file: {e}", file=sys.stderr)
            return None
```

## Snippet 46
Lines 488-495

```Python
def delete_file(self, file_id: str) -> bool:
        """
        Delete a file.

        Args:
            file_id (str): ID of the file to delete

        Returns:
```

## Snippet 47
Lines 497-508

```Python
"""
        try:
            response = requests.delete(
                f"{self.api_url}/files/{file_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}", file=sys.stderr)
            return False
```

## Snippet 48
Lines 509-516

```Python
def get_file_content(self, file_id: str) -> Optional[bytes]:
        """
        Download a file's content.

        Args:
            file_id (str): ID of the file to download

        Returns:
```

## Snippet 49
Lines 518-529

```Python
"""
        try:
            response = requests.get(
                f"{self.api_url}/files/{file_id}/content",
                headers=self.headers
            )
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}", file=sys.stderr)
            return None
```

## Snippet 50
Lines 530-537

```Python
def get_file_url(self, file_id: str) -> Optional[str]:
        """
        Get a temporary URL to download a file.

        Args:
            file_id (str): ID of the file

        Returns:
```

## Snippet 51
Lines 539-550

```Python
"""
        try:
            response = requests.post(
                f"{self.api_url}/files/{file_id}/download_url",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["download_url"]
        except Exception as e:
            print(f"Error getting file URL: {e}", file=sys.stderr)
            return None
```

## Snippet 52
Lines 551-561

```Python
def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    category_filter: Optional[str] = None,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable Mistral Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
```

## Snippet 53
Lines 564-569

```Python
if capability_filter:
        print(f"Capability: {capability_filter}")
    print("-" * 50)

    # Group models by category
    models_by_category = {}
```

## Snippet 54
Lines 572-575

```Python
if category not in models_by_category:
            models_by_category[category] = []
        models_by_category[category].append(model)
```

## Snippet 55
Lines 588-593

```Python
if model.get("deprecated_at"):
                print(f"   Deprecated: {model['deprecated_at']}")
            print(f"   Owner: {model['owned_by']}")
            print()
            idx += 1
```

## Snippet 56
Lines 598-601

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 57
Lines 604-608

```Python
def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = os.getenv("MISTRAL_API_KEY") or "n8R347515VqP48oDHwBeL9BS6nW1L8zY"
```

## Snippet 58
Lines 609-631

```Python
if not api_key:
        print("Error: MISTRAL_API_KEY environment variable not set")
        sys.exit(1)

    chat = MistralChat(api_key)

    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "created"
    category_filter = None
    capability_filter = None

    # Get initial full list of models
    all_models = chat.list_models(
        sort_by=sort_by,
        page=1,
        page_size=1000,
        category_filter=category_filter,
        capability_filter=capability_filter
    )
    total_pages = (len(all_models) + page_size - 1) // page_size
```

## Snippet 59
Lines 632-658

```Python
while True:
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            category_filter=category_filter,
            capability_filter=capability_filter
        )

        # Display models
        display_models(models, page, total_pages, sort_by, category_filter, capability_filter)

        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (created/context_length/id)")
        print("5. Filter by category (mistral/mixtral/pixtral/none)")
        print("6. Filter by capability (chat/function/vision/none)")
        print("7. Change page size")
        print("8. File Management")
        print("9. Quit")

        choice = get_user_input("Select option", "1")
```

## Snippet 60
Lines 659-662

```Python
if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 61
Lines 677-692

```Python
elif choice == "4":
            # Sort by
            sort_by = get_user_input(
                "Sort by (created/context_length/id)",
                "created"
            )
            # Refresh model list with new sorting
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
```

## Snippet 62
Lines 693-698

```Python
elif choice == "5":
            # Filter by category
            cat_choice = get_user_input(
                "Filter by category (mistral/mixtral/pixtral/none)",
                "none"
            ).lower()
```

## Snippet 63
Lines 699-709

```Python
category_filter = None if cat_choice == "none" else cat_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
```

## Snippet 64
Lines 710-715

```Python
elif choice == "6":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (chat/function/vision/none)",
                "none"
            ).lower()
```

## Snippet 65
Lines 716-726

```Python
capability_filter = None if cap_choice == "none" else cap_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                category_filter=category_filter,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
```

## Snippet 66
Lines 727-730

```Python
elif choice == "7":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
```

## Snippet 67
Lines 731-734

```Python
if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1  # Reset to first page
```

## Snippet 68
Lines 739-749

```Python
while True:
                print("\nFile Management:")
                print("1. Upload File")
                print("2. List Files")
                print("3. Download File")
                print("4. Delete File")
                print("5. Get File URL")
                print("6. Back to Main Menu")

                file_choice = get_user_input("Select option", "1")
```

## Snippet 69
Lines 765-767

```Python
for file in files:
                            print(f"ID: {file['id']}")
                            print(f"Name: {file['filename']}")
```

## Snippet 70
Lines 777-785

```Python
if content:
                        save_path = get_user_input("Enter save path")
                        try:
                            with open(save_path, 'wb') as f:
                                f.write(content)
                            print(f"File saved to {save_path}")
                        except Exception as e:
                            print(f"Error saving file: {e}")
```

## Snippet 71
Lines 788-792

```Python
if chat.delete_file(file_id):
                        print("File deleted successfully.")
                    else:
                        print("Failed to delete file.")
```

## Snippet 72
Lines 796-800

```Python
if url:
                        print(f"Temporary download URL: {url}")
                    else:
                        print("Failed to get file URL.")
```

## Snippet 73
Lines 818-829

```Python
if supports_images:
            print("\nImage options:")
            print("1. No image")
            print("2. Test image (colored square)")
            print("3. Load image from file")
            print("4. Image from URL")
            print("5. Test image via File API")

            image_choice = get_user_input("Select image option", "1")
            image_data = None
            is_url = False
```

## Snippet 74
Lines 830-836

```Python
if image_choice == "2":
                # Create test image with custom color
                color = get_user_input("Enter color (e.g., red, blue, green)", "red")
                size_str = get_user_input("Enter size (width,height)", "100,100")
                try:
                    width, height = map(int, size_str.split(","))
                    image_data = chat.create_test_image(color=color, size=(width, height))
```

## Snippet 75
Lines 839-841

```Python
except ValueError:
                    print("Invalid size format. Using default 100x100...")
                    image_data = chat.create_test_image(color=color)
```

## Snippet 76
Lines 842-845

```Python
elif image_choice == "3":
                # Load image from file
                file_path = get_user_input("Enter image file path")
                image_data = chat.load_image_from_file(file_path)
```

## Snippet 77
Lines 851-853

```Python
if url:
                    image_data = url
                    is_url = True
```

## Snippet 78
Lines 854-861

```Python
elif image_choice == "5":
                # Create and upload test image through File API
                print("\nCreating test image...")
                color = get_user_input("Enter color (e.g., red, blue, green)", "red")
                size_str = get_user_input("Enter size (width,height)", "100,100")
                try:
                    width, height = map(int, size_str.split(","))
                    test_image_data = chat.create_test_image(color=color, size=(width, height))
```

## Snippet 79
Lines 862-871

```Python
if test_image_data:
                        # Save temporary image file
                        temp_path = f"temp_test_image_{color}.png"
                        try:
                            with open(temp_path, 'wb') as f:
                                f.write(base64.b64decode(test_image_data))

                            # Upload to Mistral
                            print("Uploading image to Mistral...")
                            result = chat.upload_file(temp_path)
```

## Snippet 80
Lines 872-876

```Python
if result:
                                print(f"Image uploaded successfully. ID: {result}")

                                # Get file URL
                                url = chat.get_file_url(result)
```

## Snippet 81
Lines 895-899

```Python
else:
            image_data = None
            is_url = False

        # Get message
```

## Snippet 82
Lines 900-908

```Python
default_prompt = "What do you see in this image?" if image_data else "Tell me about yourself and your capabilities"
        message = get_user_input(
            "Enter your message",
            default_prompt
        )

        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
```

## Snippet 83
Lines 909-921

```Python
for chunk in chat.stream_chat_response(
            message,
            selected_model,
            temperature=0.7,
            top_p=1.0,
            safe_prompt=True,
            image_data=image_data,
            is_url=is_url
        ):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 50)

        # Ask to continue
```

## Snippet 84
Lines 922-927

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

