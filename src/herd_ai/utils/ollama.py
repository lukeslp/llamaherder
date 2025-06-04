#!/usr/bin/env python3
"""
Ollama API Integration for Herd AI

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

def get_ollama_url() -> str:
    """Get the configured Ollama API URL."""
    return OLLAMA_API_URL

def check_ollama_running() -> bool:
    """Check if Ollama is running by pinging the API endpoint."""
    try:
        response = requests.get(f"{OLLAMA_API_URL}", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_available_models() -> List[Dict[str, Any]]:
    """
    Get list of models available from Ollama.
    
    Returns:
        List of dictionaries containing model information
    """
    try:
        response = requests.get(f"{OLLAMA_API_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("models", [])
        else:
            logger.warning(f"Failed to get models from Ollama: {response.status_code}")
            return []
    except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return []

def get_model_details(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific model.
    
    Args:
        model_name: Name of the model to query
        
    Returns:
        Dictionary with model details or None if unavailable
    """
    try:
        payload = {"name": model_name}
        response = requests.post(
            f"{OLLAMA_API_URL}/api/show", 
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Failed to get details for model {model_name}: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return None

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
        model: The name of the model to use (if None, uses default from config)
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        system_prompt: Optional system instructions for the model
        n: Number of completions to generate
        stream: Whether to stream the response
        description: Optional description of the prompt (for logging/tracking)
        
    Returns:
        Dictionary with model response data
    """
    # Use environment variable or config if model not specified
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
        
        # Add system prompt if provided
        if system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": system_prompt})
            
        # Send request to Ollama API
        response = requests.post(
            f"{OLLAMA_API_URL}/api/chat", 
            json=payload,
            timeout=60 if not stream else None,
            stream=stream
        )
        
        # Handle streaming response
        if stream:
            def response_stream():
                for line in response.iter_lines():
                    if line:
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
            return {"stream": response_stream()}
        
        # Handle regular response
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
            
    except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return {"text": f"Error connecting to Ollama API: {str(e)}", "error": True}
    except Exception as e:
        logger.error(f"Unexpected error in Ollama API request: {e}")
        return {"text": f"Unexpected error: {str(e)}", "error": True}

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
        model: The name of the model to use (if None, uses default from config)
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        system_prompt: Optional system instructions for the model
        
    Returns:
        Dictionary with model response data
    """
    # Use environment variable or config if model not specified
    if model is None:
        model = os.environ.get("OLLAMA_MODEL", "llava")
    
    # Default to llava if no model specified (common multimodal model)
    if not model or model == "gemma":  # gemma isn't multimodal
        model = "llava"
        
    try:
        # Check if image exists
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
            
            # Add system prompt if provided
            if system_prompt:
                chat_payload["messages"].insert(0, {"role": "system", "content": system_prompt})
            
            logger.info(f"Sending image to Ollama via chat API: {model}")
            response = requests.post(
                f"{OLLAMA_API_URL}/api/chat", 
                json=chat_payload,
                timeout=90  # Images may take longer to process
            )
            
            # If successful, return the response
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
            
        except requests.RequestException as e:
            logger.error(f"Error connecting to Ollama chat API: {e}")
        
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
        
        # Add system prompt if provided
        if system_prompt:
            generate_payload["system"] = system_prompt
            
        logger.info(f"Sending image to Ollama via generate API: {model}")
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate", 
            json=generate_payload,
            timeout=90  # Images may take longer to process
        )
        
        # Handle response
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
                if "error" in error_data:
                    error_msg += f": {error_data['error']}"
            except:
                pass
            return {"text": error_msg, "error": True, "as_text": True}
            
    except requests.RequestException as e:
        logger.error(f"Error connecting to Ollama API: {e}")
        return {"text": f"Error connecting to Ollama API: {str(e)}", "error": True, "as_text": True}
    except Exception as e:
        logger.error(f"Unexpected error in Ollama API image request: {e}")
        return {"text": f"Unexpected error: {str(e)}", "error": True, "as_text": True}

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

def get_gpu_info() -> List[Dict[str, Any]]:
    """
    Get information about available GPUs.
    
    Returns:
        List of dictionaries with GPU information
    """
    gpus = []
    
    # Try to detect NVIDIA GPUs using nvidia-smi
    try:
        if platform.system() == "Windows":
            nvidia_smi = "nvidia-smi"
        else:
            nvidia_smi = "nvidia-smi"
            
        nvidia_output = subprocess.check_output([nvidia_smi, "--query-gpu=name,memory.total,memory.free,driver_version", "--format=csv,noheader,nounits"])
        for line in nvidia_output.decode("utf-8").strip().split("\n"):
            parts = line.split(", ")
            if len(parts) >= 3:
                name, total_memory, free_memory = parts[0], float(parts[1]), float(parts[2])
                gpus.append({
                    "name": name,
                    "type": "NVIDIA",
                    "vram_total_gb": round(total_memory/1024, 1),
                    "vram_free_gb": round(free_memory/1024, 1),
                    "driver_version": parts[3] if len(parts) > 3 else "Unknown"
                })
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Try to detect Apple Silicon GPU
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

def check_model_compatibility(model_name: str, system_resources: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if a model is compatible with the system's resources.
    
    Args:
        model_name: Name of the model to check
        system_resources: Dictionary with system resource information
        
    Returns:
        Dictionary with compatibility information
    """
    # Extract base model name
    base_model = model_name.split(":")[0].lower() if ":" in model_name else model_name.lower()
    
    # Get specific variant or base model requirements
    if model_name in MODEL_REQUIREMENTS:
        requirements = MODEL_REQUIREMENTS[model_name]
    elif base_model in MODEL_REQUIREMENTS:
        requirements = MODEL_REQUIREMENTS[base_model]
    else:
        # Default requirements if not in our database
        requirements = (8, 16, 8)
    
    min_ram, rec_ram, min_gpu = requirements
    available_ram = system_resources["ram_available_gb"]
    
    has_compatible_gpu = False
    gpu_vram = 0
    
    for gpu in system_resources["gpu_info"]:
        if gpu["vram_free_gb"] >= min_gpu:
            has_compatible_gpu = True
            gpu_vram = gpu["vram_free_gb"]
            break
    
    # Determine compatibility level
    if available_ram >= rec_ram and has_compatible_gpu:
        compatibility = "optimal"
    elif available_ram >= min_ram:
        compatibility = "compatible"
        if not has_compatible_gpu and min_gpu > 0:
            compatibility = "cpu_only"
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

def get_compatibility_message(compatibility: str, model: str, min_ram: float, 
                              available_ram: float, min_gpu: float, 
                              available_gpu: float) -> str:
    """Generate a user-friendly compatibility message."""
    if compatibility == "optimal":
        return f"✅ {model} is well-suited for your system."
    
    elif compatibility == "compatible":
        return f"✓ {model} should run adequately on your system."
    
    elif compatibility == "cpu_only":
        return f"⚠️ {model} will run on CPU only. Expect slow performance."
    
    else:  # insufficient_resources
        if available_ram < min_ram:
            return f"❌ {model} requires {min_ram}GB RAM, but only {available_ram}GB available."
        else:
            return f"❌ {model} requires resources beyond your system capabilities."

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
    
    for model in available_models:
        model_name = model.get("name", "")
        compatibility = check_model_compatibility(model_name, system_resources)
        model["compatibility"] = compatibility
        
        if compatibility["compatibility"] in ["optimal", "compatible"]:
            recommended.append(model)
    
    # If no optimal/compatible models, include CPU-only models
    if not recommended:
        for model in available_models:
            model_name = model.get("name", "")
            compatibility = check_model_compatibility(model_name, system_resources)
            
            if compatibility["compatibility"] == "cpu_only":
                model["compatibility"] = compatibility
                recommended.append(model)
    
    # Sort by compatibility (optimal first, then compatible, then cpu_only)
    def sort_key(model):
        comp = model.get("compatibility", {}).get("compatibility", "")
        if comp == "optimal":
            return 0
        elif comp == "compatible":
            return 1
        elif comp == "cpu_only":
            return 2
        return 3
    
    recommended.sort(key=sort_key)
    return recommended

if __name__ == "__main__":
    # Simple test if run directly
    print("Checking if Ollama is running...")
    if check_ollama_running():
        print("Ollama is running!")
        models = get_available_models()
        print(f"Found {len(models)} models:")
        for model in models:
            print(f"- {model.get('name')}")
        
        resources = get_system_resources()
        print("\nSystem Resources:")
        print(f"CPU: {resources['cpu_count']} cores ({resources['cpu_threads']} threads)")
        print(f"RAM: {resources['ram_total_gb']}GB total, {resources['ram_available_gb']}GB available")
        print(f"Platform: {resources['platform']} {resources['architecture']}")
        
        if resources["gpu_info"]:
            print("\nGPUs:")
            for gpu in resources["gpu_info"]:
                print(f"- {gpu['name']}: {gpu['vram_total_gb']}GB VRAM ({gpu['vram_free_gb']}GB free)")
        
        if models:
            print("\nModel Compatibility:")
            for model in models[:3]:  # Just show first 3 for brevity
                model_name = model.get("name", "")
                compat = check_model_compatibility(model_name, resources)
                print(f"- {model_name}: {compat['message']}")
    else:
        print("Ollama is not running. Please start the Ollama service.")