#!/usr/bin/env python
"""
MLX Chat Integration
This module provides an interface to MLX models running locally on Apple Silicon devices.
"""

import os
import sys
import json
import subprocess
import tempfile
import logging
from typing import Generator, List, Dict, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLXChat:
    """Interface for MLX models running locally on Apple Silicon."""
    
    def __init__(self):
        """Initialize the MLX chat interface."""
        self.conversation_history = []
        self.check_mlx_available()
        logger.info("Initialized MLX Chat interface")
    
    def check_mlx_available(self) -> bool:
        """Check if MLX command-line tools are available."""
        try:
            import shutil
            mlx_path = shutil.which("mlx_lm.generate")
            if mlx_path:
                logger.info(f"Found MLX command-line tool at: {mlx_path}")
                return True
            else:
                logger.warning("MLX command-line tool not found in PATH")
                return False
        except Exception as e:
            logger.warning(f"Error checking for MLX availability: {e}")
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available MLX models.
        
        Returns:
            List[Dict[str, Any]]: List of model information dictionaries
        """
        # Return a predefined list of models optimized for MLX
        models = [
            {
                "id": "mlx-community/Qwen2-7B-Instruct-4bit",
                "name": "qwen:7b",
                "context_length": 8192,
                "description": "Qwen2 7B optimized for Apple Silicon"
            },
            {
                "id": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
                "name": "mistral:7b",
                "context_length": 8192,
                "description": "Mistral 7B optimized for instruction following"
            },
            {
                "id": "mlx-community/Mistral-Nemo-Instruct-2407-4bit",
                "name": "nemo:7b",
                "context_length": 8192,
                "description": "Mistral Nemo optimized for instruction following"
            },
            {
                "id": "mlx-community/DeepSeek-R1-Distill-Qwen-7B-8bit",
                "name": "deepseek:7b",
                "context_length": 8192,
                "description": "DeepSeek R1 optimized for reasoning"
            },
            {
                "id": "mlx-community/Mistral-Small-24B-Instruct-2501-4bit",
                "name": "mistral-small:24b",
                "context_length": 8192,
                "description": "Mistral Small 24B optimized for instruction following"
            },
            {
                "id": "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit",
                "name": "deepseek:32b",
                "context_length": 8192,
                "description": "DeepSeek R1 optimized for reasoning"
            }
        ]
        return models
    
    def get_model_id(self, model_name: str) -> str:
        """
        Get the full model ID from a short name.
        
        Args:
            model_name (str): Short model name (e.g., "qwen:7b")
            
        Returns:
            str: Full model ID
        """
        # If the model is already a full ID, return it
        if "/" in model_name:
            return model_name
        
        # If the model is a short name, look it up
        for model in self.list_models():
            if model["name"] == model_name:
                return model["id"]
        
        # If the model is a short name without the provider prefix, try to match it
        for model in self.list_models():
            name_parts = model["name"].split(":")
            if len(name_parts) > 1 and name_parts[0] == model_name:
                return model["id"]
        
        # Default to the first model if no match is found
        logger.warning(f"Model {model_name} not found, using default model")
        return self.list_models()[0]["id"]
    
    def format_conversation(self) -> str:
        """
        Format the conversation history for the model.
        
        Returns:
            str: Formatted conversation history
        """
        formatted = ""
        for entry in self.conversation_history:
            role = entry["role"]
            content = entry["content"]
            if role == "user":
                formatted += f"User: {content}\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n"
        return formatted
    
    def chat_response(
        self,
        prompt: str,
        model: str = "qwen:7b",
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate a chat response from an MLX model.
        
        Args:
            prompt (str): The user's message
            model (str): The model name to use
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Controls randomness (0.0-1.0)
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Format conversation context
        formatted_prompt = self.format_conversation()
        
        # Get the model ID from the model name
        model_id = self.get_model_id(model)
        
        # Create a temporary file for the prompt
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(formatted_prompt)
            temp_file_path = temp_file.name
        
        try:
            # Run mlx_lm.generate command
            cmd = [
                "mlx_lm.generate",
                "--model", model_id,
                "--prompt", temp_file_path,
                "--max-tokens", str(max_tokens),
                "--verbose", "True"
            ]
            
            if temperature != 0.7:
                cmd.extend(["--temp", str(temperature)])
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            # Run the command and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Process output line by line
            response_text = ""
            for line in process.stdout:
                # Skip lines that are not part of the response
                if line.startswith("Loading") or line.startswith("Tokenizing"):
                    continue
                
                # Clean up the line
                chunk = line.strip()
                if chunk:
                    response_text += chunk
                    yield chunk
            
            # Wait for the process to complete
            process.wait()
            
            # Check for errors
            if process.returncode != 0:
                error_output = process.stderr.read()
                logger.error(f"Error running MLX command: {error_output}")
                yield f"Error: {error_output}"
                return
            
            # Add assistant message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
        except Exception as e:
            logger.error(f"Error generating MLX response: {e}")
            yield f"Error: {str(e)}"
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Cleared MLX conversation history")
        return {"status": "success", "message": "Conversation cleared"}


if __name__ == "__main__":
    # Simple CLI for testing
    mlx_chat = MLXChat()
    
    print("MLX Chat Interface")
    print("Type 'exit' to quit, 'clear' to clear conversation history")
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "clear":
            mlx_chat.clear_conversation()
            print("Conversation history cleared")
            continue
        
        print("\nAssistant: ", end="")
        for chunk in mlx_chat.chat_response(user_input):
            print(chunk, end="")
        print()
