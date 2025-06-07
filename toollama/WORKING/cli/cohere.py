"""
Cohere API Chat Implementation
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

class CohereChat:
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

    def upload_dataset(self, file_path: str, dataset_name: str, dataset_type: str) -> Optional[str]:
        """
        Upload a dataset to Cohere.

        Args:
            file_path (str): The path to the dataset file.
            dataset_name (str): The name to assign to the dataset.
            dataset_type (str): The type of dataset (e.g., 'chat-finetune-input').

        Returns:
            Optional[str]: The ID of the uploaded dataset, or None if upload failed.
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

    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset by its ID.

        Args:
            dataset_id (str): The ID of the dataset to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
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

    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict]:
        """
        Get metadata for a specific dataset.

        Args:
            dataset_id (str): The ID of the dataset.

        Returns:
            Optional[Dict]: Dataset metadata if successful, None otherwise.
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

    def validate_dataset(self, file_path: str, dataset_type: str) -> bool:
        """
        Validate a dataset file before uploading.

        Args:
            file_path (str): Path to the dataset file.
            dataset_type (str): Type of dataset to validate.

        Returns:
            bool: True if validation passes, False otherwise.
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

        if dataset_type not in requirements:
            print(f"Unsupported dataset type: {dataset_type}", file=sys.stderr)
            return False

        # Check file format
        file_ext = file_path.split('.')[-1].lower()
        if file_ext not in (requirements[dataset_type]['format'] 
                          if isinstance(requirements[dataset_type]['format'], list) 
                          else [requirements[dataset_type]['format']]):
            print(f"Invalid file format. Expected: {requirements[dataset_type]['format']}", file=sys.stderr)
            return False

        # Check file size (max 1.5GB)
        file_size = os.path.getsize(file_path)
        if file_size > 1.5 * 1024 * 1024 * 1024:  # 1.5GB in bytes
            print("File size exceeds 1.5GB limit", file=sys.stderr)
            return False

        try:
            # Validate content based on type
            if file_ext == 'jsonl':
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if not lines:
                        print("Empty file", file=sys.stderr)
                        return False

                    # Count valid examples
                    train_examples = 0
                    eval_examples = 0
                    for line in lines:
                        try:
                            data = json.loads(line)
                            # Check required fields
                            if all(field in data for field in requirements[dataset_type]['fields']):
                                if 'split' in data and data['split'] == 'eval':
                                    eval_examples += 1
                                else:
                                    train_examples += 1
                        except json.JSONDecodeError:
                            print(f"Invalid JSON line: {line}", file=sys.stderr)
                            return False

                    # Check minimum examples
                    if 'min_train' in requirements[dataset_type]:
                        if train_examples < requirements[dataset_type]['min_train']:
                            print(f"Not enough training examples. Need at least {requirements[dataset_type]['min_train']}", file=sys.stderr)
                            return False
                    if 'min_eval' in requirements[dataset_type]:
                        if eval_examples < requirements[dataset_type]['min_eval']:
                            print(f"Not enough evaluation examples. Need at least {requirements[dataset_type]['min_eval']}", file=sys.stderr)
                            return False

            elif file_ext == 'csv':
                import pandas as pd
                df = pd.read_csv(file_path)
                # Check required fields
                if not all(field in df.columns for field in requirements[dataset_type]['fields']):
                    print(f"Missing required fields: {requirements[dataset_type]['fields']}", file=sys.stderr)
                    return False

            return True

        except Exception as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return False

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
            
            # Get models filtered for chat endpoint
            response = requests.get(
                "https://api.cohere.com/v1/models",  # Models endpoint still v1
                headers=headers,
                params={"endpoint": "chat"}
            )
            response.raise_for_status()
            
            models = []
            for model in response.json()["models"]:
                models.append({
                    "id": model["name"],
                    "endpoints": model["endpoints"],
                    "context_length": model.get("context_length", 4096),
                    "is_finetuned": model.get("finetuned", False)
                })
            
            return sorted(models, key=lambda x: x["context_length"], reverse=True)
            
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
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

    def fix_json(self, line_text: str) -> str:
        """Fix JSON formatting issues in streaming response."""
        line_text = line_text.replace('""', '","')
        line_text = line_text.replace('false"', 'false,"')
        return line_text

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
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # Remove "data: " prefix
                        data = json.loads(line_text)
                        
                        # Handle different event types
                        if data["type"] == "content-delta":
                            text = data["delta"]["message"]["content"]["text"]
                            full_response += text
                            yield text
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
            
            # Add assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            # Remove the user message if request failed
            self.chat_history.pop()
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            # Remove the user message if request failed
            self.chat_history.pop()

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant."
        }]

    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.
        
        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)
            
        Returns:
            Optional[str]: Base64 encoded image data or None if creation fails
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

    def create_test_file(self, content: str = None) -> str:
        """
        Create a test text file and return its base64 encoding.
        
        Args:
            content (str): Optional content for the test file
            
        Returns:
            str: Base64 encoded file content
        """
        if not content:
            content = "This is a test file.\nIt contains multiple lines.\nHello, Cohere!"
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')

    def encode_file(self, file_path: str) -> Optional[str]:
        """
        Encode a file to base64.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            Optional[str]: Base64 encoded file data or None if encoding fails
        """
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file: {e}", file=sys.stderr)
            return None

    def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """Format a message with optional image data for the API."""
        if not image_data:
            return message
        
        # Convert single image to list
        if isinstance(image_data, str):
            image_data = [image_data]
        
        content = [{"type": "text", "text": message}]
        
        for img in image_data:
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
        
        return content

    def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
        """Format a message with optional image and file data for the API."""
        if not image_data and not file_data:
            return message
        
        content = [{"type": "text", "text": message}]
        
        # Add images
        if image_data:
            # Convert single image to list
            if isinstance(image_data, str):
                image_data = [image_data]
            
            for img in image_data:
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
        
        # Add file if provided
        if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{base64.b64decode(file_data).decode('utf-8', errors='ignore')}"
            })
        
        return content

def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print("\nAvailable Cohere Models:")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['id']}")
        print(f"   Endpoints: {', '.join(model['endpoints'])}")
        print(f"   Context Length: {model['context_length']} tokens")
        print(f"   Fine-tuned: {'Yes' if model['is_finetuned'] else 'No'}")
        print()

def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with an optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(prompt).strip()
    return response if response else default

def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = "8K2VDJ784DPHN57zYauE03mGuslFuaxBW1NUY1LO"
    
    chat = CohereChat(api_key)
    
    while True:
        print("\nCohere Chat Interface")
        print("-" * 50)
        print("1. Chat with Model")
        print("2. Dataset Management")
        print("3. Quit")
        
        choice = get_user_input("Select option", "1")
        
        if choice == "1":
            # Fetch and display available models
            models = chat.list_models()
            display_models(models)
            
            # Get model selection
            while True:
                try:
                    selection = int(get_user_input("Select a model number", "1")) - 1
                    if 0 <= selection < len(models):
                        selected_model = models[selection]["id"]
                        break
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Start conversation loop
            while True:
                # Get message
                message = get_user_input(
                    "Enter your message",
                    "Tell me about yourself and your capabilities"
                )
                
                # Stream response
                print("\nStreaming response:")
                print("-" * 50)
                for chunk in chat.stream_chat_response(message, selected_model):
                    print(chunk, end="", flush=True)
                print("\n" + "-" * 50)
                
                # Ask to continue
                if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
                    print("\nClearing conversation history and exiting...")
                    chat.clear_conversation()
                    break
                print("\nContinuing conversation...\n")
        
        elif choice == "2":
            # Dataset Management Menu
            while True:
                print("\nDataset Management:")
                print("1. Upload Dataset")
                print("2. List Datasets")
                print("3. Get Dataset Metadata")
                print("4. Delete Dataset")
                print("5. Back to Main Menu")
                
                dataset_choice = get_user_input("Select option", "1")
                
                if dataset_choice == "1":
                    # Upload dataset
                    file_path = get_user_input("Enter dataset file path")
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
                    if chat.validate_dataset(file_path, dataset_type):
                        print("Dataset validation passed. Uploading...")
                        result = chat.upload_dataset(file_path, dataset_name, dataset_type)
                        if result:
                            print(f"Dataset uploaded successfully. ID: {result}")
                    else:
                        print("Dataset validation failed. Please check the requirements and try again.")
                
                elif dataset_choice == "2":
                    # List datasets
                    datasets = chat.list_datasets()
                    if datasets:
                        print("\nAvailable Datasets:")
                        print("-" * 50)
                        for dataset in datasets:
                            print(f"ID: {dataset['id']}")
                            print(f"Name: {dataset['name']}")
                            print(f"Type: {dataset['type']}")
                            print(f"Created: {dataset['created_at']}")
                            print("-" * 30)
                    else:
                        print("No datasets found.")
                
                elif dataset_choice == "3":
                    # Get dataset metadata
                    dataset_id = get_user_input("Enter dataset ID")
                    metadata = chat.get_dataset_metadata(dataset_id)
                    if metadata:
                        print("\nDataset Metadata:")
                        print("-" * 50)
                        print(f"ID: {metadata['id']}")
                        print(f"Name: {metadata['name']}")
                        print(f"Type: {metadata['type']}")
                        print(f"Created: {metadata['created_at']}")
                        print(f"Status: {metadata['status']}")
                        if 'metrics' in metadata:
                            print("\nMetrics:")
                            for key, value in metadata['metrics'].items():
                                print(f"  {key}: {value}")
                        print("-" * 50)
                    else:
                        print("Failed to retrieve dataset metadata.")
                
                elif dataset_choice == "4":
                    # Delete dataset
                    dataset_id = get_user_input("Enter dataset ID")
                    if get_user_input(f"Are you sure you want to delete dataset {dataset_id}? (y/n)", "n").lower() == 'y':
                        if chat.delete_dataset(dataset_id):
                            print("Dataset deleted successfully.")
                        else:
                            print("Failed to delete dataset.")
                
                elif dataset_choice == "5":
                    break
                
                print()  # Add spacing between operations
        
        elif choice == "3":
            print("Exiting...")
            break
        
        print()  # Add spacing between iterations

if __name__ == "__main__":
    main()

