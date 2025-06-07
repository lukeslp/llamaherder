# Code Snippets from src/herd_ai/utils/ollama.py

File: `src/herd_ai/utils/ollama.py`  
Language: Python  
Extracted: 2025-06-07 05:10:00  

## Snippet 1
Lines 5-46

```Python
This module provides utilities for interacting with the Ollama API,
checking available models, system resources, and making model recommendations.
"""

import os
import json
import logging
import platform
import subprocess
import psutil
import requests
from typing import Dict, List, Optional, Tuple, Union, Any

logger = logging.getLogger(__name__)

# Default Ollama API endpoint
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")

# Model resource requirements (approximate)
MODEL_REQUIREMENTS = {
    # Format: "model": (min_ram_gb, recommended_ram_gb, min_gpu_vram_gb)
    "llama2": (8, 16, 12),
    "llama3": (8, 16, 16),
    "llama3:70b": (32, 48, 40),
    "llama3:8b": (8, 16, 8),
    "mistral": (8, 16, 12),
    "mixtral": (24, 32, 24),
    "phi3": (6, 8, 6),
    "gemma": (8, 16, 8),
    "codellama": (8, 16, 16),
    "wizardcoder": (8, 16, 12),
    "dolphin": (8, 16, 12),
    "orca": (8, 16, 12),
    "nous-hermes": (8, 16, 12),
    "stable-diffusion": (8, 16, 8),
    "qwen": (8, 16, 12),
    "qwen:14b": (16, 24, 16),
    "falcon": (8, 16, 12),
    "yi": (8, 16, 12),
    "openchat": (8, 16, 12),
}
```

## Snippet 2
Lines 47-50

```Python
def get_ollama_url() -> str:
    """Get the configured Ollama API URL."""
    return OLLAMA_API_URL
```

## Snippet 3
Lines 52-58

```Python
"""Check if Ollama is running by pinging the API endpoint."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False
```

## Snippet 4
Lines 59-67

```Python
def get_available_models() -> List[Dict[str, Any]]:
    """
    Get list of models available from Ollama.

    Returns:
        List of dictionaries containing model information
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
```

## Snippet 5
Lines 68-73

```Python
if response.status_code == 200:
            data = response.json()
            return data.get("models", [])
        else:
            logger.warning(f"Failed to get models from Ollama: {response.status_code}")
            return []
```

## Snippet 6
Lines 74-77

```Python
except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return []
```

## Snippet 7
Lines 78-85

```Python
def get_model_details(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific model.

    Args:
        model_name: Name of the model to query

    Returns:
```

## Snippet 8
Lines 87-94

```Python
"""
    try:
        payload = {"name": model_name}
        response = requests.post(
            f"{OLLAMA_API_URL}/api/show",
            json=payload,
            timeout=5
        )
```

## Snippet 9
Lines 95-97

```Python
if response.status_code == 200:
            return response.json()
        else:
```

## Snippet 10
Lines 100-103

```Python
except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return None
```

## Snippet 11
Lines 104-118

```Python
def send_prompt_to_ollama(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    n: int = 1,
    stream: bool = False,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a prompt to the Ollama API and get a response.

    Args:
        prompt: The user prompt to send to the model
```

## Snippet 12
Lines 119-121

```Python
model: The name of the model to use (if None, uses default from config)
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
```

## Snippet 13
Lines 122-124

```Python
system_prompt: Optional system instructions for the model
        n: Number of completions to generate
        stream: Whether to stream the response
```

## Snippet 14
Lines 127-129

```Python
Returns:
        Dictionary with model response data
    """
```

## Snippet 15
Lines 131-147

```Python
if model is None:
        model = os.environ.get("OLLAMA_MODEL", "gemma")

    try:
        # Prepare the API request payload
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
```

## Snippet 16
Lines 149-155

```Python
if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})

        # Send request to Ollama API
        response = requests.post(
            f"{OLLAMA_API_URL}/api/chat",
            json=payload,
```

## Snippet 17
Lines 164-168

```Python
if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
```

## Snippet 18
Lines 172-183

```Python
if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("message", {}).get("content", ""),
                "model": model,
                "finish_reason": result.get("done", False),
                "usage": result.get("usage", {})
            }
        else:
            logger.warning(f"Ollama API request failed: {response.status_code}")
            return {"text": f"Error: API request failed with status {response.status_code}", "error": True}
```

## Snippet 19
Lines 184-190

```Python
except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return {"text": f"Error connecting to Ollama API: {str(e)}", "error": True}
    except Exception as e:
        logger.error(f"Unexpected error in Ollama API request: {e}")
        return {"text": f"Unexpected error: {str(e)}", "error": True}
```

## Snippet 20
Lines 191-204

```Python
def send_image_prompt_to_ollama(
    image_path: str,
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an image and prompt to Ollama API and get a response.

    Args:
        image_path: Path to the image file
        prompt: The user prompt to send to the model
```

## Snippet 21
Lines 205-207

```Python
model: The name of the model to use (if None, uses default from config)
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
```

## Snippet 22
Lines 210-212

```Python
Returns:
        Dictionary with model response data
    """
```

## Snippet 23
Lines 223-249

```Python
if not os.path.exists(image_path):
            return {"text": f"Error: Image file not found: {image_path}", "error": True, "as_text": True}

        # Read the image file and encode it as base64
        import base64
        try:
            with open(image_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error reading image file: {e}")
            return {"text": f"Error reading image file: {str(e)}", "error": True, "as_text": True}

        # First try using the chat endpoint with the proper format (recommended in Ollama docs)
        try:
            # Format according to Ollama chat API documentation
            chat_payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt, "images": [base64_image]}
                ],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
```

## Snippet 24
Lines 251-261

```Python
if system_prompt:
                chat_payload["messages"].insert(0, {"role": "system", "content": system_prompt})

            logger.info(f"Sending image to Ollama via chat API: {model}")
            response = requests.post(
                f"{OLLAMA_API_URL}/api/chat",
                json=chat_payload,
                timeout=90  # Images may take longer to process
            )

            # If successful, return the response
```

## Snippet 25
Lines 262-274

```Python
if response.status_code == 200:
                result = response.json()
                return {
                    "text": result.get("message", {}).get("content", ""),
                    "model": model,
                    "finish_reason": result.get("done", False),
                    "usage": result.get("usage", {})
                }

            # If chat API fails, log the error
            logger.warning(f"Ollama chat API failed with status {response.status_code}, trying generate API...")
            logger.debug(f"Response: {response.text}")
```

## Snippet 26
Lines 278-290

```Python
# Fall back to the generate endpoint if chat endpoint fails
        # Format according to Ollama generate API documentation
        generate_payload = {
            "model": model,
            "prompt": prompt,
            "images": [base64_image],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
```

## Snippet 27
Lines 292-302

```Python
if system_prompt:
            generate_payload["system"] = system_prompt

        logger.info(f"Sending image to Ollama via generate API: {model}")
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=generate_payload,
            timeout=90  # Images may take longer to process
        )

        # Handle response
```

## Snippet 28
Lines 303-315

```Python
if response.status_code == 200:
            result = response.json()
            return {
                "text": result.get("response", ""),
                "model": model,
                "finish_reason": result.get("done", False),
                "usage": result.get("usage", {})
            }
        else:
            logger.warning(f"Ollama API image request failed: {response.status_code}")
            error_msg = f"Error: API request failed with status {response.status_code}"
            try:
                error_data = response.json()
```

## Snippet 29
Lines 318-321

```Python
except:
                pass
            return {"text": error_msg, "error": True, "as_text": True}
```

## Snippet 30
Lines 322-328

```Python
except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return {"text": f"Error connecting to Ollama API: {str(e)}", "error": True, "as_text": True}
    except Exception as e:
        logger.error(f"Unexpected error in Ollama API image request: {e}")
        return {"text": f"Unexpected error: {str(e)}", "error": True, "as_text": True}
```

## Snippet 31
Lines 329-346

```Python
def get_system_resources() -> Dict[str, Any]:
    """
    Get information about available system resources.

    Returns:
        Dictionary with system resource information
    """
    resources = {
        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_threads": psutil.cpu_count(logical=True),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 1),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "gpu_info": get_gpu_info(),
    }
    return resources
```

## Snippet 32
Lines 347-357

```Python
def get_gpu_info() -> List[Dict[str, Any]]:
    """
    Get information about available GPUs.

    Returns:
        List of dictionaries with GPU information
    """
    gpus = []

    # Try to detect NVIDIA GPUs using nvidia-smi
    try:
```

## Snippet 33
Lines 358-363

```Python
if platform.system() == "Windows":
            nvidia_smi = "nvidia-smi"
        else:
            nvidia_smi = "nvidia-smi"

        nvidia_output = subprocess.check_output([nvidia_smi, "--query-gpu=name,memory.total,memory.free,driver_version", "--format=csv,noheader,nounits"])
```

## Snippet 34
Lines 366-372

```Python
if len(parts) >= 3:
                name, total_memory, free_memory = parts[0], float(parts[1]), float(parts[2])
                gpus.append({
                    "name": name,
                    "type": "NVIDIA",
                    "vram_total_gb": round(total_memory/1024, 1),
                    "vram_free_gb": round(free_memory/1024, 1),
```

## Snippet 35
Lines 379-398

```Python
if platform.system() == "Darwin" and platform.machine() == "arm64":
        try:
            memory_cmd = "system_profiler SPMemoryDataType"
            memory_output = subprocess.check_output(memory_cmd.split(), text=True)

            # Apple Silicon shares RAM with GPU, so we estimate GPU memory
            # as a portion of system memory
            total_memory = psutil.virtual_memory().total / (1024**3)
            gpus.append({
                "name": "Apple Silicon",
                "type": "Apple",
                "vram_total_gb": round(total_memory * 0.5, 1),  # Estimate as half of system RAM
                "vram_free_gb": round(psutil.virtual_memory().available / (1024**3) * 0.5, 1),
                "shared_memory": True
            })
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    return gpus
```

## Snippet 36
Lines 401-410

```Python
Check if a model is compatible with the system's resources.

    Args:
        model_name: Name of the model to check
        system_resources: Dictionary with system resource information

    Returns:
        Dictionary with compatibility information
    """
    # Extract base model name
```

## Snippet 37
Lines 416-418

```Python
elif base_model in MODEL_REQUIREMENTS:
        requirements = MODEL_REQUIREMENTS[base_model]
    else:
```

## Snippet 38
Lines 429-433

```Python
if gpu["vram_free_gb"] >= min_gpu:
            has_compatible_gpu = True
            gpu_vram = gpu["vram_free_gb"]
            break
```

## Snippet 39
Lines 441-455

```Python
else:
        compatibility = "insufficient_resources"

    return {
        "model": model_name,
        "compatibility": compatibility,
        "min_ram_gb": min_ram,
        "recommended_ram_gb": rec_ram,
        "min_gpu_vram_gb": min_gpu,
        "available_ram_gb": available_ram,
        "available_gpu_vram_gb": gpu_vram,
        "can_run": compatibility != "insufficient_resources",
        "message": get_compatibility_message(compatibility, model_name, min_ram, available_ram, min_gpu, gpu_vram)
    }
```

## Snippet 40
Lines 456-459

```Python
def get_compatibility_message(compatibility: str, model: str, min_ram: float,
                              available_ram: float, min_gpu: float,
                              available_gpu: float) -> str:
    """Generate a user-friendly compatibility message."""
```

## Snippet 41
Lines 475-487

```Python
def get_recommended_models(system_resources: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get a list of recommended models based on system resources.

    Args:
        system_resources: Dictionary with system resource information

    Returns:
        List of dictionaries with recommended model information
    """
    available_models = get_available_models()
    recommended = []
```

## Snippet 42
Lines 488-492

```Python
for model in available_models:
        model_name = model.get("name", "")
        compatibility = check_model_compatibility(model_name, system_resources)
        model["compatibility"] = compatibility
```

## Snippet 43
Lines 498-501

```Python
for model in available_models:
            model_name = model.get("name", "")
            compatibility = check_model_compatibility(model_name, system_resources)
```

## Snippet 44
Lines 513-516

```Python
elif comp == "cpu_only":
            return 2
        return 3
```

## Snippet 45
Lines 527-531

```Python
for model in models:
            print(f"- {model.get('name')}")

        resources = get_system_resources()
        print("\nSystem Resources:")
```

