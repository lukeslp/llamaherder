# Code Snippets from toollama/API/--storage/processed-cli/ollama_local-and-cloud.py

File: `toollama/API/--storage/processed-cli/ollama_local-and-cloud.py`  
Language: Python  
Extracted: 2025-06-07 05:17:30  

## Snippet 1
Lines 3-18

```Python
This module provides a simple interface to the Ollama API for streaming chat responses.
Supports model selection, multi-turn conversations, image analysis, and file handling with streaming responses.
Supports both local and cloud Ollama instances.
"""

import requests
import sys
import base64
import json
import mimetypes
from typing import Generator, List, Dict, Optional, Union, Tuple
from datetime import datetime
from PIL import Image
import io
import os
```

## Snippet 2
Lines 19-25

```Python
class OllamaChat:
    # Define Ollama endpoints
    ENDPOINTS = {
        'local': 'http://localhost:11434',
        'cloud': 'https://ai.assisted.space'
    }
```

## Snippet 3
Lines 26-32

```Python
def __init__(self, endpoint_type: str = 'local'):
        """
        Initialize the Ollama client with the specified endpoint.

        Args:
            endpoint_type (str): Type of endpoint to use ('local' or 'cloud')
        """
```

## Snippet 4
Lines 33-53

```Python
if endpoint_type not in self.ENDPOINTS:
            raise ValueError(f"Invalid endpoint type. Must be one of: {', '.join(self.ENDPOINTS.keys())}")

        self.endpoint_type = endpoint_type
        self.base_url = self.ENDPOINTS[endpoint_type]
        # Fetch models—mark each model's ownership based on the endpoint
        self.models = self._fetch_models()
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]

        # Define supported file types
        self.supported_image_types = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        self.supported_file_types = {
            'txt', 'md', 'markdown', 'rst', 'csv', 'json', 'yaml', 'yml',
            'py', 'js', 'html', 'css', 'xml', 'sql', 'sh', 'bash',
            'pdf', 'doc', 'docx', 'rtf'
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
```

## Snippet 5
Lines 54-65

```Python
def _fetch_models(self) -> Dict:
        """
        Fetch available models from Ollama API.

        Returns:
            Dict: Dictionary of available models with their details
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()

            models = {}
```

## Snippet 6
Lines 78-84

```Python
elif "70b" in model_id or "70B" in model_id:
                    context_length = 16384

                models[model_id] = {
                    "id": model_id,
                    "name": model_id,
                    "context_length": context_length,
```

## Snippet 7
Lines 85-89

```Python
"description": f"Ollama {model_id} model",
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": datetime.now(),
                    "created_str": datetime.now().strftime("%Y-%m-%d"),
```

## Snippet 8
Lines 95-98

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return {}
```

## Snippet 9
Lines 99-120

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
        Get available Ollama models with sorting and pagination.

        Args:
            sort_by (str): Field to sort by ('id', 'context_length', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter by capability ('text', 'vision')

        Returns:
            List[Dict]: List of available models with their details
        """
        models_list = [
```

## Snippet 10
Lines 127-136

```Python
elif sort_by == "capabilities":
            models_list.sort(key=lambda x: x["capability_count"], reverse=reverse)
        else:  # sort by id
            models_list.sort(key=lambda x: x["id"], reverse=reverse)

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return models_list[start_idx:end_idx]
```

## Snippet 11
Lines 137-148

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """Create a test image and return its base64 encoding."""
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

## Snippet 12
Lines 149-156

```Python
def encode_file(self, file_path: str) -> Optional[Tuple[str, str]]:
        """
        Encode a file to base64 and determine its type.

        Args:
            file_path (str): Path to the file

        Returns:
```

## Snippet 13
Lines 166-170

```Python
if ext not in self.supported_file_types and ext not in self.supported_image_types:
                raise ValueError(f"Unsupported file type: {ext}")

            # Get mime type
            mime_type, _ = mimetypes.guess_type(file_path)
```

## Snippet 14
Lines 171-177

```Python
if not mime_type:
                mime_type = 'application/octet-stream'

            # Read and encode file
            with open(file_path, "rb") as file:
                file_data = file.read()
                return base64.b64encode(file_data).decode('utf-8'), mime_type
```

## Snippet 15
Lines 178-181

```Python
except Exception as e:
            print(f"Error encoding file: {e}", file=sys.stderr)
            return None
```

## Snippet 16
Lines 182-189

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64 with proper preprocessing.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 17
Lines 191-194

```Python
"""
        try:
            with Image.open(image_path) as img:
                # Check format
```

## Snippet 18
Lines 203-209

```Python
if img.size[0] > 2048 or img.size[1] > 2048:
                    ratio = min(2048/img.size[0], 2048/img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Save to bytes with original format
                img_byte_arr = io.BytesIO()
```

## Snippet 19
Lines 214-217

```Python
if len(img_byte_arr) > self.max_file_size:
                    raise ValueError(f"Image size exceeds {self.max_file_size / 1024 / 1024}MB limit")

                return base64.b64encode(img_byte_arr).decode('utf-8')
```

## Snippet 20
Lines 218-221

```Python
except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 21
Lines 222-229

```Python
def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[str] = None,
        file_data: Optional[Tuple[str, str]] = None,
        is_url: bool = False
    ) -> Union[str, Dict]:
        """
```

## Snippet 22
Lines 230-238

```Python
Format a message with optional image and file data for the Ollama API.

        Args:
            message (str): The text message
            image_data (Optional[str]): Base64 encoded image data or URL
            file_data (Optional[Tuple[str, str]]): Tuple of (base64 data, mime type)
            is_url (bool): Whether image_data is a URL

        Returns:
```

## Snippet 23
Lines 241-245

```Python
if not image_data and not file_data:
            return message

        content = message
```

## Snippet 24
Lines 248-252

```Python
if is_url:
                content += f"\n[Image]({image_data})"
            else:
                content += f"\n<image>data:image/png;base64,{image_data}</image>"
```

## Snippet 25
Lines 256-267

```Python
if 'text' in mime_type or mime_type in ('application/json', 'application/xml'):
                # For text-based files, decode and include content
                try:
                    decoded_content = base64.b64decode(base64_data).decode('utf-8', errors='ignore')
                    content += f"\n\nFile content:\n```\n{decoded_content}\n```"
                except Exception as e:
                    print(f"Error decoding file content: {e}", file=sys.stderr)
                    content += f"\n[File attachment: {mime_type}]"
            else:
                # For binary files, just note the attachment
                content += f"\n[File attachment: {mime_type}]"
```

## Snippet 26
Lines 270-302

```Python
def stream_chat_response(
        self,
        message: str,
        model: str,
        temperature: float = 0.7,
        image_data: Optional[str] = None,
        file_data: Optional[Tuple[str, str]] = None,
        is_url: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Ollama.

        Args:
            message (str): The user's input message
            model (str): The model to use
            temperature (float): Response temperature (0.0 to 1.0)
            image_data (Optional[str]): Base64 encoded image data or URL
            file_data (Optional[Tuple[str, str]]): Tuple of (base64 data, mime type)
            is_url (bool): Whether image_data is a URL

        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Format message with attachments
            content = self.format_message_with_attachments(
                message,
                image_data,
                file_data,
                is_url
            )

            # Prepare request payload based on endpoint type
```

## Snippet 27
Lines 303-334

```Python
if self.endpoint_type == 'cloud':
                endpoint = f"{self.base_url}/api/generate"
                payload = {
                    "model": model,
                    "prompt": content,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "top_p": 0.9
                    }
                }
            else:  # local
                endpoint = f"{self.base_url}/api/chat"
                payload = {
                    "model": model,
                    "messages": self.chat_history + [{"role": "user", "content": content}],
                    "stream": True,
                    "options": {
                        "temperature": temperature
                    }
                }

            # Send streaming request with appropriate timeout
            response = requests.post(
                endpoint,
                json=payload,
                stream=True,
                timeout=60  # 60 second timeout
            )
            response.raise_for_status()

            accumulated_message = ""
```

## Snippet 28
Lines 336-338

```Python
if line:
                    try:
                        chunk = line.decode('utf-8')
```

## Snippet 29
Lines 345-349

```Python
if self.endpoint_type == 'cloud':
                            message_content = chunk_data.get('response', '')
                        else:
                            message_content = chunk_data.get('message', {}).get('content', '')
```

## Snippet 30
Lines 350-353

```Python
if message_content:
                            yield message_content
                            accumulated_message += message_content
```

## Snippet 31
Lines 354-360

```Python
except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse chunk: {e}", file=sys.stderr)
                        continue
                    except Exception as e:
                        print(f"Warning: Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 32
Lines 362-367

```Python
if accumulated_message:
                self.chat_history.append({
                    "role": "assistant",
                    "content": accumulated_message
                })
```

## Snippet 33
Lines 369-371

```Python
error_msg = f"Error: Request timed out when connecting to {self.endpoint_type} Ollama instance"
            print(error_msg, file=sys.stderr)
            yield error_msg
```

## Snippet 34
Lines 373-375

```Python
error_msg = f"Error: Could not connect to {self.endpoint_type} Ollama instance"
            print(error_msg, file=sys.stderr)
            yield error_msg
```

## Snippet 35
Lines 376-380

```Python
except Exception as e:
            error_msg = f"Error in stream_chat_response: {str(e)}"
            print(error_msg, file=sys.stderr)
            yield error_msg
```

## Snippet 36
Lines 381-387

```Python
def clear_conversation(self):
        """Clear the conversation history."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
```

## Snippet 37
Lines 388-397

```Python
def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable Ollama Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
```

## Snippet 38
Lines 398-401

```Python
if capability_filter:
        print(f"Filtering by capability: {capability_filter}")
    print("-" * 50)
```

## Snippet 39
Lines 413-416

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 40
Lines 419-425

```Python
def main():
    """Main CLI interface."""
    # Choose endpoint
    print("\nChoose Ollama endpoint:")
    print("1. Local (http://localhost:11434)")
    print("2. Cloud (https://ai.assisted.space)")
```

## Snippet 41
Lines 431-436

```Python
elif choice == "2":
            endpoint_type = "cloud"
            break
        else:
            print("Invalid choice. Please select 1 or 2.")
```

## Snippet 42
Lines 437-439

```Python
try:
        chat = OllamaChat(endpoint_type)
    except Exception as e:
```

## Snippet 43
Lines 443-450

```Python
print(f"\nConnected to {endpoint_type.title()} Ollama instance at {chat.base_url}")

    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "id"
    capability_filter = None
```

## Snippet 44
Lines 451-459

```Python
while True:
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            capability_filter=capability_filter
        )
```

## Snippet 45
Lines 464-488

```Python
# Calculate total pages
        all_models = chat.list_models(
            sort_by=sort_by,
            capability_filter=capability_filter,
            page=1,
            page_size=1000
        )
        total_pages = (len(all_models) + page_size - 1) // page_size

        # Display models
        display_models(models, page, total_pages, sort_by, capability_filter)

        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (id/context_length/capabilities)")
        print("5. Filter by capability (text/vision/none)")
        print("6. Change page size")
        print("7. Switch endpoint")
        print("8. Quit")

        choice = get_user_input("Select option", "1")
```

## Snippet 46
Lines 489-491

```Python
if choice == "1":
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 47
Lines 502-506

```Python
elif choice == "4":
            sort_by = get_user_input(
                "Sort by (id/context_length/capabilities)",
                "id"
            )
```

## Snippet 48
Lines 507-511

```Python
elif choice == "5":
            cap_choice = get_user_input(
                "Filter by capability (text/vision/none)",
                "none"
            ).lower()
```

## Snippet 49
Lines 513-515

```Python
elif choice == "6":
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
```

## Snippet 50
Lines 520-524

```Python
elif choice == "7":
            # Restart program to switch endpoint
            print("\nRestarting to switch endpoint...")
            python = sys.executable
            os.execl(python, python, *sys.argv)
```

## Snippet 51
Lines 537-553

```Python
if not supports_images:
            print("[Note: Selected model does not support image understanding]")

        print("\nAttachment options:")
        print("1. Text only")
        print("2. Test image (colored square)")
        print("3. Load image from file")
        print("4. Image from URL")
        print("5. Load file")
        print("6. Switch endpoint")
        print("7. Quit")

        input_choice = get_user_input("Select input option", "1")
        image_data = None
        file_data = None
        is_url = False
```

## Snippet 52
Lines 554-559

```Python
if input_choice == "2" and supports_images:
            color = get_user_input("Enter color (e.g., red, blue, green)", "red")
            size_str = get_user_input("Enter size (width,height)", "100,100")
            try:
                width, height = map(int, size_str.split(","))
                image_data = chat.create_test_image(color=color, size=(width, height))
```

## Snippet 53
Lines 562-564

```Python
except ValueError:
                print("Invalid size format. Using default 100x100...")
                image_data = chat.create_test_image(color=color)
```

## Snippet 54
Lines 565-567

```Python
elif input_choice == "3" and supports_images:
            file_path = get_user_input("Enter image file path")
            image_data = chat.encode_image(file_path)
```

## Snippet 55
Lines 572-574

```Python
if url:
                image_data = url
                is_url = True
```

## Snippet 56
Lines 583-587

```Python
elif input_choice == "6":
            # Restart program to switch endpoint
            print("\nRestarting to switch endpoint...")
            python = sys.executable
            os.execl(python, python, *sys.argv)
```

## Snippet 57
Lines 588-593

```Python
elif input_choice == "7":
            print("Exiting...")
            sys.exit(0)

        # Get message
        default_prompt = (
```

## Snippet 58
Lines 597-604

```Python
)
        message = get_user_input("Enter your message", default_prompt)

        # Stream response
        print("\nStreaming response:")
        print("-" * 50)

        try:
```

## Snippet 59
Lines 605-611

```Python
for chunk in chat.stream_chat_response(
                message,
                selected_model,
                image_data=image_data,
                file_data=file_data,
                is_url=is_url
            ):
```

## Snippet 60
Lines 615-618

```Python
except KeyboardInterrupt:
            print("\nResponse streaming interrupted by user.")
            print("-" * 50)
```

## Snippet 61
Lines 619-624

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

