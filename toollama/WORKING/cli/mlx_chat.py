"""
MLX Chat Implementation
This module provides a simple interface to MLX models for local chat responses.
Supports model selection and multi-turn conversations.
"""

from mlx_lm import load, generate
import sys
from typing import Generator, List, Dict, Optional
from datetime import datetime

class MLXChat:
    MODELS = {
        "qwen:7b": {
            "id": "mlx-community/Qwen2-7B-Instruct-4bit",
            "context_length": 8192,
            "description": "Qwen2 7B optimized for Apple Silicon"
        },
        "mistral:7b": {
            "id": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "context_length": 8192,
            "description": "Mistral 7B optimized for instruction following"
        },
        "nemo:7b": {
            "id": "mlx-community/Mistral-Nemo-Instruct-2407-4bit",
            "context_length": 8192,
            "description": "Mistral Nemo optimized for instruction following"
        },
        "deepseek:7b": {
            "id": "mlx-community/DeepSeek-R1-Distill-Qwen-7B-8bit",
            "context_length": 8192,
            "description": "DeepSeek R1 optimized for reasoning"
        },
        "mistral-small:24b": {
            "id": "mlx-community/Mistral-Small-24B-Instruct-2501-4bit",
            "context_length": 8192,
            "description": "Mistral Small 24B optimized for instruction following"
        },
        "deepseek:32b": {
            "id": "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit",
            "context_length": 8192,
            "description": "DeepSeek R1 optimized for reasoning"
        }
    }

    def __init__(self):
        """Initialize the MLX chat interface."""
        self.model = None
        self.tokenizer = None
        self.current_model_id = None
        self.chat_history = []
        self.model_cache = {}
    
    def list_models(self) -> List[Dict]:
        """
        Get available MLX models.
        
        Returns:
            List[Dict]: List of available models with their details
        """
        return [
            {
                "id": info["id"],
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"]
            }
            for model_id, info in self.MODELS.items()
        ]

    def load_model(self, model_id: str) -> bool:
        """
        Load a specific MLX model.
        
        Args:
            model_id (str): The model identifier to load
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            if model_id not in self.MODELS:
                print(f"Unknown model: {model_id}", file=sys.stderr)
                return False

            model_path = self.MODELS[model_id]["id"]
            
            # Check if model is already loaded
            if self.current_model_id == model_id:
                return True
            
            # Check if model is in cache
            if model_path in self.model_cache:
                self.model, self.tokenizer = self.model_cache[model_path]
            else:
                print(f"\nLoading {model_id} ({model_path})...")
                self.model, self.tokenizer = load(model_path)
                self.model_cache[model_path] = (self.model, self.tokenizer)
            
            self.current_model_id = model_id
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}", file=sys.stderr)
            return False

    def format_conversation(self) -> str:
        """Format the conversation history for the model."""
        formatted = ""
        for entry in self.chat_history:
            role = entry["role"]
            content = entry["content"]
            if role == "user":
                formatted += f"User: {content}\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n"
        return formatted

    def chat_response(
        self,
        message: str,
        model_id: str = "qwen",
    ) -> Generator[str, None, None]:
        """
        Get a chat response from the MLX model.
        
        Args:
            message (str): The user's input message
            model_id (str): The MLX model to use
            
        Yields:
            str: The response text
        """
        try:
            # Load model if needed
            if not self.load_model(model_id):
                yield "Error: Failed to load model"
                return

            # Add user message to history
            self.chat_history.append({
                "role": "user",
                "content": message
            })
            
            # Format conversation context
            prompt = self.format_conversation()
            
            # Generate response
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                verbose=True
            )
            
            # Clean up response (remove any "Assistant:" prefix)
            response = response.replace("Assistant:", "").strip()
            
            # Add to history and yield
            self.chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            yield response

        except Exception as e:
            print(f"Error generating response: {e}", file=sys.stderr)
            # Remove the user message if generation failed
            if self.chat_history:
                self.chat_history.pop()
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history."""
        self.chat_history = []

def display_models(models: List[Dict]) -> None:
    """Display available models in a formatted way."""
    print("\nAvailable MLX Models:")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Context Length: {model['context_length']} tokens")
        print(f"   Description: {model['description']}")
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
    chat = MLXChat()
    
    # Fetch and display available models
    models = chat.list_models()
    display_models(models)
    
    # Get model selection
    while True:
        try:
            selection = int(get_user_input("Select a model number", "1")) - 1  # Default to qwen
            if 0 <= selection < len(models):
                selected_model = models[selection]["name"]
                if chat.load_model(selected_model):
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
        
        # Get and display response
        print("\nGenerating response:")
        print("-" * 50)
        for response in chat.chat_response(message, selected_model):
            print(response)
        print("-" * 50)
        
        # Ask to continue
        if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")

if __name__ == "__main__":
    main()
