# Code Snippets from toollama/API/--storage/processed-cli/mlx_chat.py

File: `toollama/API/--storage/processed-cli/mlx_chat.py`  
Language: Python  
Extracted: 2025-06-07 05:17:33  

## Snippet 1
Lines 1-21

```Python
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
```

## Snippet 2
Lines 25-30

```Python
def __init__(self):
        """Initialize the MLX chat interface."""
        self.conversation_history = []
        self.check_mlx_available()
        logger.info("Initialized MLX Chat interface")
```

## Snippet 3
Lines 32-35

```Python
"""Check if MLX command-line tools are available."""
        try:
            import shutil
            mlx_path = shutil.which("mlx_lm.generate")
```

## Snippet 4
Lines 36-41

```Python
if mlx_path:
                logger.info(f"Found MLX command-line tool at: {mlx_path}")
                return True
            else:
                logger.warning("MLX command-line tool not found in PATH")
                return False
```

## Snippet 5
Lines 46-52

```Python
def list_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available MLX models.

        Returns:
            List[Dict[str, Any]]: List of model information dictionaries
        """
```

## Snippet 6
Lines 53-58

```Python
# Return a predefined list of models optimized for MLX
        models = [
            {
                "id": "mlx-community/Qwen2-7B-Instruct-4bit",
                "name": "qwen:7b",
                "context_length": 8192,
```

## Snippet 7
Lines 60-64

```Python
},
            {
                "id": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
                "name": "mistral:7b",
                "context_length": 8192,
```

## Snippet 8
Lines 66-70

```Python
},
            {
                "id": "mlx-community/Mistral-Nemo-Instruct-2407-4bit",
                "name": "nemo:7b",
                "context_length": 8192,
```

## Snippet 9
Lines 72-76

```Python
},
            {
                "id": "mlx-community/DeepSeek-R1-Distill-Qwen-7B-8bit",
                "name": "deepseek:7b",
                "context_length": 8192,
```

## Snippet 10
Lines 78-82

```Python
},
            {
                "id": "mlx-community/Mistral-Small-24B-Instruct-2501-4bit",
                "name": "mistral-small:24b",
                "context_length": 8192,
```

## Snippet 11
Lines 84-88

```Python
},
            {
                "id": "mlx-community/DeepSeek-R1-Distill-Qwen-32B-4bit",
                "name": "deepseek:32b",
                "context_length": 8192,
```

## Snippet 12
Lines 94-104

```Python
def get_model_id(self, model_name: str) -> str:
        """
        Get the full model ID from a short name.

        Args:
            model_name (str): Short model name (e.g., "qwen:7b")

        Returns:
            str: Full model ID
        """
        # If the model is already a full ID, return it
```

## Snippet 13
Lines 105-108

```Python
if "/" in model_name:
            return model_name

        # If the model is a short name, look it up
```

## Snippet 14
Lines 125-130

```Python
Format the conversation history for the model.

        Returns:
            str: Formatted conversation history
        """
        formatted = ""
```

## Snippet 15
Lines 131-133

```Python
for entry in self.conversation_history:
            role = entry["role"]
            content = entry["content"]
```

## Snippet 16
Lines 140-171

```Python
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
```

## Snippet 17
Lines 172-186

```Python
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
```

## Snippet 18
Lines 187-202

```Python
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
```

## Snippet 19
Lines 210-213

```Python
if chunk:
                    response_text += chunk
                    yield chunk
```

## Snippet 20
Lines 218-229

```Python
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
```

## Snippet 21
Lines 230-236

```Python
except Exception as e:
            logger.error(f"Error generating MLX response: {e}")
            yield f"Error: {str(e)}"
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)
```

## Snippet 22
Lines 237-241

```Python
def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Cleared MLX conversation history")
        return {"status": "success", "message": "Conversation cleared"}
```

## Snippet 23
Lines 256-261

```Python
elif user_input.lower() == "clear":
            mlx_chat.clear_conversation()
            print("Conversation history cleared")
            continue

        print("\nAssistant: ", end="")
```

