#!/usr/bin/env python
"""
MLX Provider for Camina Chat API
This module integrates MLX models running locally on Apple Silicon devices.
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Generator, Optional, Any
from api.services.providers.base import BaseProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if mlx_lm command-line tools are available
def is_mlx_available():
    """Check if mlx_lm is available in the system."""
    try:
        # Check for mlx_lm.generate command
        mlx_path = shutil.which("mlx_lm.generate")
        if mlx_path:
            logger.info(f"Found MLX command-line tool at: {mlx_path}")
            return True
        else:
            logger.warning("MLX command-line tool not found in PATH")
            return False
    except Exception as e:
        logger.warning(f"Error checking MLX availability: {e}")
        return False

# Get available MLX models
def get_available_models():
    """Get a list of available MLX models."""
    models = [
        {
            "id": "mlx-community/Llama-3.2-3B-Instruct-4bit",
            "name": "mlx-community/Llama-3.2-3B-Instruct-4bit",
            "context_length": 8192,
            "description": "Llama 3.2 3B optimized for instruction following"
        },
        {
            "id": "mlx-community/Qwen2-7B-Instruct-4bit",
            "name": "mlx-community/Qwen2-7B-Instruct-4bit",
            "context_length": 8192,
            "description": "Qwen2 7B optimized for Apple Silicon"
        },
        {
            "id": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "name": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "context_length": 8192,
            "description": "Mistral 7B optimized for instruction following"
        }
    ]
    return models

class MLXProvider(BaseProvider):
    """Provider implementation for MLX-LM."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the MLX provider.
        
        Args:
            api_key: Not used for MLX, kept for interface compatibility
        """
        self.conversation_history = []
        self.is_available = is_mlx_available()
        logger.info("Initialized MLX provider")
    
    def list_models(self, **kwargs) -> List[Dict[str, Any]]:
        """
        List available models for MLX.
        
        Returns:
            List of model objects
        """
        if self.is_available:
            models = get_available_models()
            for model in models:
                model["provider"] = "mlx"
            return models
        return []
    
    def stream_chat_response(self, prompt: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Stream response for the given prompt.
        
        Args:
            prompt: The prompt to send
            **kwargs: Optional arguments
                - model: Model to use
                - max_tokens: Maximum tokens to generate
                - messages: Array of message objects, if provided
                
        Yields:
            Generated text chunks
        """
        temp_file_path = None
        try:
            # Get model and parameters
            model = kwargs.get("model", "mlx-community/Llama-3.2-3B-Instruct-4bit")
            max_tokens = kwargs.get("max_tokens", 4096)
            
            # Add the current message to history
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": prompt})
            
            # First, try to use a simplified response method if MLX tools aren't fully functional
            if not self.is_available:
                logger.warning("MLX command-line tools not available, using fallback response")
                fallback_response = self._generate_fallback_response(prompt)
                yield {"content": fallback_response}
                return
                
            # Format conversation for command line
            formatted_prompt = ""
            for message in messages:
                if message["role"] == "user":
                    formatted_prompt += f"User: {message['content']}\n"
                elif message["role"] == "assistant":
                    formatted_prompt += f"Assistant: {message['content']}\n"
                else:
                    formatted_prompt += f"{message['role'].capitalize()}: {message['content']}\n"
            
            # Add the final prompt prefix
            formatted_prompt += "Assistant: "
            
            # Write the prompt to a temporary file
            temp_fd, temp_file_path = tempfile.mkstemp(text=True)
            os.close(temp_fd)
            
            with open(temp_file_path, "w") as f:
                f.write(formatted_prompt)
            
            logger.info(f"Running MLX command with model: {model}")
            
            # Run the MLX command
            cmd = [
                "mlx_lm.generate",
                "--model", model,
                "--prompt", f"@{temp_file_path}",
                "--max-tokens", str(max_tokens)
            ]
            
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            try:
                # Run the command and capture output
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait for the process to complete
                stdout, stderr = process.communicate(timeout=30)
                
                # Check for errors
                if process.returncode != 0:
                    error_msg = f"Error running MLX command: {stderr}"
                    logger.error(error_msg)
                    yield {"error": "MLX command failed. Server is experiencing technical difficulties."}
                    return
                
                # Process response
                response_text = ""
                for line in stdout.split('\n'):
                    # Skip lines that are not part of the response
                    if any(skip in line for skip in ["Loading", "Tokenizing", "Prompt:", "Generation:", "Peak memory", "mx.metal", "tokens-per-sec", "Fetching", "=========="]):
                        continue
                    
                    # Clean up the line
                    cleaned_line = line.strip()
                    if cleaned_line:
                        response_text += cleaned_line + " "
                
                # Trim whitespace
                response_text = response_text.strip()
                
                # Log the response for debugging
                logger.info(f"MLX command-line response: {response_text[:100]}...")
                
                # If we got an empty response, use the fallback
                if not response_text:
                    logger.warning("Empty response from MLX command, using fallback")
                    fallback_response = self._generate_fallback_response(prompt)
                    yield {"content": fallback_response}
                    return
                
                # Add conversation history (only if we have a valid response)
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": response_text})
                
                # Return the response
                yield {"content": response_text}
                
            except subprocess.TimeoutExpired:
                logger.error("MLX command timed out after 30 seconds")
                process.kill()
                fallback_response = self._generate_fallback_response(prompt)
                yield {"content": fallback_response}
                return
                
        except Exception as e:
            error_msg = f"Error in MLX-LM chat: {str(e)}"
            logger.error(error_msg)
            
            # Use fallback response for any errors
            fallback_response = self._generate_fallback_response(prompt)
            yield {"content": fallback_response}
            
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.error(f"Error removing temp file: {e}")
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a fallback response when MLX is not available."""
        if "hello" in prompt.lower() or "hi" in prompt.lower():
            return "Hello! I'm a simulated MLX response since the MLX service is currently experiencing technical difficulties. How can I assist you today?"
        
        if any(q in prompt.lower() for q in ["how are you", "how're you", "how do you feel"]):
            return "I'm just a simulated response since the MLX service is having some technical issues. But I'm here to help as best I can!"
        
        if "?" in prompt:
            return ("I apologize, but I can't provide a complete answer right now because the MLX service "
                   "is experiencing technical difficulties. The system is having dependency issues with the transformers library. "
                   "This is being addressed by the team. In the meantime, you might want to try one of the other available models.")
        
        return ("I apologize, but the MLX model is currently unavailable due to technical issues. "
               "The system is experiencing dependency conflicts with the transformers library. "
               "The team is working to resolve this issue. In the meantime, please try one of the other available models like Mistral or Perplexity.")
    
    def _get_model_id(self, model: str) -> str:
        """Get the model ID from the model name."""
        # If the model is already a full ID, return it
        if "/" in model:
            return model
        
        # Map short names to full IDs
        model_map = {
            "llama3.2:3b": "mlx-community/Llama-3.2-3B-Instruct-4bit",
            "qwen:7b": "mlx-community/Qwen2-7B-Instruct-4bit",
            "mistral:7b": "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
        }
        
        # If the model is a short name, look it up in the map
        if model in model_map:
            return model_map[model]
        
        # Default to the first model if no match is found
        logger.warning(f"Model {model} not found, using default model")
        return get_available_models()[0]["id"]
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def process_image(self, file_path: str) -> Optional[str]:
        """
        Process an image for use in multimodal requests.
        Not supported by MLX-LM.
        
        Returns:
            None as MLX-LM doesn't support images
        """
        return None
    
    def call_tool(self, prompt: str, model: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Use the model to call tools based on the prompt.
        Not supported by MLX-LM.
        
        Returns:
            Dict with error message
        """
        return {"error": "Tool calling not supported by MLX-LM"}
    
    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image to base64 or other format required by the provider.
        Not supported by MLX-LM.
        
        Returns:
            None as MLX-LM doesn't support images
        """
        return None 