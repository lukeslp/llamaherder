# Code Snippets from toollama/API/--storage/processed-cli/cohere.py

File: `toollama/API/--storage/processed-cli/cohere.py`  
Language: Python  
Extracted: 2025-06-07 05:17:31  

## Snippet 1
Lines 3-16

```Python
This module provides a simple interface to the Cohere API for streaming chat responses.
Supports model selection and multi-turn conversations with streaming responses.
"""

import requests
import json
import sys
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
import os
import base64
import io
from PIL import Image
```

## Snippet 2
Lines 18-28

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
Lines 29-38

```Python
def upload_dataset(self, file_path: str, dataset_name: str, dataset_type: str) -> Optional[str]:
        """
        Upload a dataset to Cohere.

        Args:
            file_path (str): The path to the dataset file.
            dataset_name (str): The name to assign to the dataset.
            dataset_type (str): The type of dataset (e.g., 'chat-finetune-input').

        Returns:
```

## Snippet 4
Lines 40-61

```Python
"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        files = {
            'data': open(file_path, 'rb')
        }
        data = {
            'name': dataset_name,
            'type': dataset_type
        }

        try:
            response = requests.post(self.dataset_url, headers=headers, files=files, data=data)
            response.raise_for_status()
            dataset_id = response.json().get('id')
            print(f"Dataset '{dataset_name}' uploaded successfully with ID: {dataset_id}")
            return dataset_id
        except requests.exceptions.RequestException as e:
            print(f"Failed to upload dataset: {e}", file=sys.stderr)
            return None
```

## Snippet 5
Lines 62-81

```Python
def list_datasets(self) -> List[Dict]:
        """
        List all datasets associated with the API key.

        Returns:
            List[Dict]: A list of datasets with their details.
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }

        try:
            response = requests.get(self.dataset_url, headers=headers)
            response.raise_for_status()
            datasets = response.json().get('datasets', [])
            return datasets
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve datasets: {e}", file=sys.stderr)
            return []
```

## Snippet 6
Lines 82-89

```Python
def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset by its ID.

        Args:
            dataset_id (str): The ID of the dataset to delete.

        Returns:
```

## Snippet 7
Lines 91-105

```Python
"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        delete_url = f"{self.dataset_url}/{dataset_id}"

        try:
            response = requests.delete(delete_url, headers=headers)
            response.raise_for_status()
            print(f"Dataset with ID '{dataset_id}' deleted successfully.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Failed to delete dataset: {e}", file=sys.stderr)
            return False
```

## Snippet 8
Lines 108-113

```Python
Get metadata for a specific dataset.

        Args:
            dataset_id (str): The ID of the dataset.

        Returns:
```

## Snippet 9
Lines 115-128

```Python
"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        metadata_url = f"{self.dataset_url}/{dataset_id}"

        try:
            response = requests.get(metadata_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to get dataset metadata: {e}", file=sys.stderr)
            return None
```

## Snippet 10
Lines 129-137

```Python
def validate_dataset(self, file_path: str, dataset_type: str) -> bool:
        """
        Validate a dataset file before uploading.

        Args:
            file_path (str): Path to the dataset file.
            dataset_type (str): Type of dataset to validate.

        Returns:
```

## Snippet 11
Lines 139-159

```Python
"""
        # Dataset type requirements based on Cohere docs
        requirements = {
            'chat-finetune-input': {
                'min_train': 2,
                'min_eval': 1,
                'format': 'jsonl',
                'fields': ['messages']
            },
            'embed-input': {
                'format': ['csv', 'jsonl'],
                'fields': ['text']
            },
            'reranker-finetune-input': {
                'min_train': 256,
                'min_eval': 64,
                'format': 'jsonl',
                'fields': ['query', 'relevant_passages', 'hard_negatives']
            }
        }
```

## Snippet 12
Lines 160-165

```Python
if dataset_type not in requirements:
            print(f"Unsupported dataset type: {dataset_type}", file=sys.stderr)
            return False

        # Check file format
        file_ext = file_path.split('.')[-1].lower()
```

## Snippet 13
Lines 174-179

```Python
if file_size > 1.5 * 1024 * 1024 * 1024:  # 1.5GB in bytes
            print("File size exceeds 1.5GB limit", file=sys.stderr)
            return False

        try:
            # Validate content based on type
```

## Snippet 14
Lines 180-182

```Python
if file_ext == 'jsonl':
                with open(file_path, 'r') as f:
                    lines = f.readlines()
```

## Snippet 15
Lines 183-189

```Python
if not lines:
                        print("Empty file", file=sys.stderr)
                        return False

                    # Count valid examples
                    train_examples = 0
                    eval_examples = 0
```

## Snippet 16
Lines 190-193

```Python
for line in lines:
                        try:
                            data = json.loads(line)
                            # Check required fields
```

## Snippet 17
Lines 195-198

```Python
if 'split' in data and data['split'] == 'eval':
                                    eval_examples += 1
                                else:
                                    train_examples += 1
```

## Snippet 18
Lines 199-202

```Python
except json.JSONDecodeError:
                            print(f"Invalid JSON line: {line}", file=sys.stderr)
                            return False
```

## Snippet 19
Lines 205-207

```Python
if train_examples < requirements[dataset_type]['min_train']:
                            print(f"Not enough training examples. Need at least {requirements[dataset_type]['min_train']}", file=sys.stderr)
                            return False
```

## Snippet 20
Lines 209-212

```Python
if eval_examples < requirements[dataset_type]['min_eval']:
                            print(f"Not enough evaluation examples. Need at least {requirements[dataset_type]['min_eval']}", file=sys.stderr)
                            return False
```

## Snippet 21
Lines 213-216

```Python
elif file_ext == 'csv':
                import pandas as pd
                df = pd.read_csv(file_path)
                # Check required fields
```

## Snippet 22
Lines 217-220

```Python
if not all(field in df.columns for field in requirements[dataset_type]['fields']):
                    print(f"Missing required fields: {requirements[dataset_type]['fields']}", file=sys.stderr)
                    return False
```

## Snippet 23
Lines 223-226

```Python
except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return False
```

## Snippet 24
Lines 227-239

```Python
def list_models(self) -> List[Dict]:
        """
        Retrieve available Cohere models.

        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
```

## Snippet 25
Lines 240-248

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

## Snippet 26
Lines 249-258

```Python
for model in response.json()["models"]:
                models.append({
                    "id": model["name"],
                    "endpoints": model["endpoints"],
                    "context_length": model.get("context_length", 4096),
                    "is_finetuned": model.get("finetuned", False)
                })

            return sorted(models, key=lambda x: x["context_length"], reverse=True)
```

## Snippet 27
Lines 261-273

```Python
# Fallback to known models if API fails
            return [{
                "id": "command-r-plus-08-2024",
                "endpoints": ["chat"],
                "context_length": 4096,
                "is_finetuned": False
            }, {
                "id": "command-light",
                "endpoints": ["chat"],
                "context_length": 4096,
                "is_finetuned": False
            }]
```

## Snippet 28
Lines 274-279

```Python
def fix_json(self, line_text: str) -> str:
        """Fix JSON formatting issues in streaming response."""
        line_text = line_text.replace('""', '","')
        line_text = line_text.replace('false"', 'false,"')
        return line_text
```

## Snippet 29
Lines 280-335

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

## Snippet 30
Lines 337-339

```Python
if line:
                    try:
                        line_text = line.decode('utf-8')
```

## Snippet 31
Lines 350-355

```Python
except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 32
Lines 356-361

```Python
# Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })
```

## Snippet 33
Lines 371-377

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]
```

## Snippet 34
Lines 378-385

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 35
Lines 387-394

```Python
"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 36
Lines 395-403

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
```

## Snippet 37
Lines 405-415

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

## Snippet 38
Lines 416-420

```Python
def create_test_file(self, content: str = None) -> str:
        """
        Create a test text file and return its base64 encoding.

        Args:
```

## Snippet 39
Lines 423-425

```Python
Returns:
            str: Base64 encoded file content
        """
```

## Snippet 40
Lines 426-429

```Python
if not content:
            content = "This is a test file.\nIt contains multiple lines.\nHello, Cohere!"
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')
```

## Snippet 41
Lines 430-437

```Python
def encode_file(self, file_path: str) -> Optional[str]:
        """
        Encode a file to base64.

        Args:
            file_path (str): Path to the file

        Returns:
```

## Snippet 42
Lines 439-446

```Python
"""
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file: {e}", file=sys.stderr)
            return None
```

## Snippet 43
Lines 447-452

```Python
def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 44
Lines 454-457

```Python
if not image_data:
            return message

        # Convert single image to list
```

## Snippet 45
Lines 464-476

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

## Snippet 46
Lines 479-485

```Python
def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 47
Lines 487-492

```Python
if not image_data and not file_data:
            return message

        content = [{"type": "text", "text": message}]

        # Add images
```

## Snippet 48
Lines 499-511

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

## Snippet 49
Lines 513-520

```Python
if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{base64.b64decode(file_data).decode('utf-8', errors='ignore')}"
            })

        return content
```

## Snippet 50
Lines 521-524

```Python
def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print("\nAvailable Cohere Models:")
    print("-" * 50)
```

## Snippet 51
Lines 536-539

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 52
Lines 542-548

```Python
def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = "8K2VDJ784DPHN57zYauE03mGuslFuaxBW1NUY1LO"

    chat = CohereChat(api_key)
```

## Snippet 53
Lines 549-557

```Python
while True:
        print("\nCohere Chat Interface")
        print("-" * 50)
        print("1. Chat with Model")
        print("2. Dataset Management")
        print("3. Quit")

        choice = get_user_input("Select option", "1")
```

## Snippet 54
Lines 558-563

```Python
if choice == "1":
            # Fetch and display available models
            models = chat.list_models()
            display_models(models)

            # Get model selection
```

## Snippet 55
Lines 564-566

```Python
while True:
                try:
                    selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 56
Lines 575-584

```Python
while True:
                # Get message
                message = get_user_input(
                    "Enter your message",
                    "Tell me about yourself and your capabilities"
                )

                # Stream response
                print("\nStreaming response:")
                print("-" * 50)
```

## Snippet 57
Lines 590-595

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
                    print("\nClearing conversation history and exiting...")
                    chat.clear_conversation()
                    break
                print("\nContinuing conversation...\n")
```

## Snippet 58
Lines 598-607

```Python
while True:
                print("\nDataset Management:")
                print("1. Upload Dataset")
                print("2. List Datasets")
                print("3. Get Dataset Metadata")
                print("4. Delete Dataset")
                print("5. Back to Main Menu")

                dataset_choice = get_user_input("Select option", "1")
```

## Snippet 59
Lines 611-622

```Python
if not os.path.exists(file_path):
                        print("File not found.")
                        continue

                    dataset_name = get_user_input("Enter dataset name")
                    dataset_type = get_user_input(
                        "Enter dataset type (chat-finetune-input/embed-input/reranker-finetune-input)",
                        "chat-finetune-input"
                    )

                    # Validate dataset before uploading
                    print("\nValidating dataset...")
```

## Snippet 60
Lines 634-636

```Python
if datasets:
                        print("\nAvailable Datasets:")
                        print("-" * 50)
```

## Snippet 61
Lines 637-642

```Python
for dataset in datasets:
                            print(f"ID: {dataset['id']}")
                            print(f"Name: {dataset['name']}")
                            print(f"Type: {dataset['type']}")
                            print(f"Created: {dataset['created_at']}")
                            print("-" * 30)
```

## Snippet 62
Lines 650-657

```Python
if metadata:
                        print("\nDataset Metadata:")
                        print("-" * 50)
                        print(f"ID: {metadata['id']}")
                        print(f"Name: {metadata['name']}")
                        print(f"Type: {metadata['type']}")
                        print(f"Created: {metadata['created_at']}")
                        print(f"Status: {metadata['status']}")
```

## Snippet 63
Lines 670-674

```Python
if chat.delete_dataset(dataset_id):
                            print("Dataset deleted successfully.")
                        else:
                            print("Failed to delete dataset.")
```

