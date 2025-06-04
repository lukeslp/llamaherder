###############################################################################
# Herd AI - AI Provider Utility Module
#
# This module provides a unified interface for selecting and using different
# AI providers (Ollama, X.AI, Gemini) for text and image processing tasks.
#
# Features:
#   - Provider selection and fallback logic
#   - Abstraction for sending prompts/files to the appropriate provider
#   - Handles both text and image modalities
#
# Credentials:
#   - Ollama: No credentials required for local use
#   - X.AI: Requires XAI_API_KEY (see config or environment variable)
#   - Gemini: Requires GEMINI_API_KEY (see config or environment variable)
#
# Arguments:
#   - file_path: str or pathlib.Path, path to the file to process
#   - prompt: str, the prompt or description to send to the AI
#   - provider: str, provider name ("ollama", "xai", "gemini"), optional
#   - custom_system_prompt: str, optional system prompt to override default
#
# Returns:
#   - AI response (str or dict), or None if processing failed
#
###############################################################################

import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
import requests
from herd_ai.config import DEFAULT_COHERE_MODEL

# Add OpenAI import
import os
import json
import base64
import io
from PIL import Image

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Add Mistral import
try:
    from herd_ai.utils import mistral
except ImportError:
    try:
        import utils.mistral as mistral
    except ImportError:
        mistral = None

# Add Cohere import
try:
    from herd_ai.utils import cohere
except ImportError:
    try:
        import utils.cohere as cohere
    except ImportError:
        cohere = None

###############################################################################
# Provider and Config Import Logic
#
# Attempts to import configuration and provider utilities from the package,
# falling back to legacy or direct imports as needed. If all imports fail,
# provides minimal fallback implementations to ensure basic functionality.
###############################################################################
try:
    try:
        from herd_ai.config import (
            DEFAULT_AI_PROVIDER, AI_PROVIDERS, 
            is_image_extension, get_model_for_file, 
            INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE,
            OPENAI_API_KEY, DEFAULT_OPENAI_MODEL,  # OpenAI config imports
            MISTRAL_API_KEY, DEFAULT_MISTRAL_MODEL  # Mistral config imports
        )
        from herd_ai.utils import ollama, xai, gemini
        from herd_ai.utils import config as herd_config
    except ImportError:
        try:
            from llamacleaner.config import (
                DEFAULT_AI_PROVIDER, AI_PROVIDERS,
                is_image_extension, get_model_for_file, 
                INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE,
                OPENAI_API_KEY, DEFAULT_OPENAI_MODEL,  # OpenAI config imports
                MISTRAL_API_KEY, DEFAULT_MISTRAL_MODEL  # Mistral config imports
            )
            from llamacleaner.utils import ollama, xai, gemini
            from llamacleaner.utils import config as herd_config
        except ImportError:
            from config import (
                DEFAULT_AI_PROVIDER, AI_PROVIDERS, 
                is_image_extension, get_model_for_file, 
                INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE,
                OPENAI_API_KEY, DEFAULT_OPENAI_MODEL,  # OpenAI config imports
                MISTRAL_API_KEY, DEFAULT_MISTRAL_MODEL  # Mistral config imports
            )
            import utils.ollama as ollama
            import utils.xai as xai
            import utils.gemini as gemini
            herd_config = None
except Exception as e:
    print(f"Error importing modules in utils/ai_provider.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    DEFAULT_AI_PROVIDER = "xai"
    AI_PROVIDERS = ["ollama", "xai", "gemini", "cohere", "openai", "mistral"]  # Add mistral
    INSTRUCTION_TEMPLATE = "You are a helpful assistant."
    IMAGE_ALT_TEXT_TEMPLATE = "Describe this image in detail."
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    DEFAULT_OPENAI_MODEL = "gpt-4o"
    MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
    DEFAULT_MISTRAL_MODEL = "mistral-medium"
    def is_image_extension(file_path):
        return str(file_path).lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg'))
    def get_model_for_file(file_path, provider="ollama"):
        if provider == "openai":
            return DEFAULT_OPENAI_MODEL
        elif provider == "mistral":
            return DEFAULT_MISTRAL_MODEL
        return "gemma3:4b"
    herd_config = None

logger = logging.getLogger(__name__)

# OpenAI default models
OPENAI_DEFAULT_MODELS = {
    "gpt-4o": {
        "id": "gpt-4o",
        "context_length": 128000,
        "description": "GPT-4o model with all capabilities",
        "capabilities": ["text", "vision", "function"]
    },
    "gpt-4-vision-preview": {
        "id": "gpt-4-vision-preview",
        "context_length": 128000,
        "description": "GPT-4 with image understanding",
        "capabilities": ["text", "vision", "function"]
    },
    "gpt-4-turbo": {
        "id": "gpt-4-turbo",
        "context_length": 128000,
        "description": "Most capable GPT-4 model",
        "capabilities": ["text", "function"]
    },
    "gpt-3.5-turbo": {
        "id": "gpt-3.5-turbo",
        "context_length": 16385,
        "description": "Efficient GPT-3.5 model",
        "capabilities": ["text", "function"]
    }
}

# Mistral default models
MISTRAL_DEFAULT_MODELS = {
    "mistral-tiny": {
        "id": "mistral-tiny",
        "context_length": 32768,
        "description": "Fast and efficient model for simple tasks",
        "capabilities": ["text"]
    },
    "mistral-small": {
        "id": "mistral-small",
        "context_length": 32768,
        "description": "Balanced model for general use",
        "capabilities": ["text", "function"]
    },
    "mistral-medium": {
        "id": "mistral-medium",
        "context_length": 32768,
        "description": "More capable model for complex tasks",
        "capabilities": ["text", "function"]
    },
    "mistral-large": {
        "id": "mistral-large",
        "context_length": 32768,
        "description": "Most capable Mistral model",
        "capabilities": ["text", "function", "vision"]
    }
}

###############################################################################
# get_ai_provider
#
# Determines the AI provider to use for a given operation.
#
# Arguments:
#   - provider (str, optional): The provider name to use. If None, will attempt
#     to use the configured default from herd_config, or fall back to the
#     DEFAULT_AI_PROVIDER.
#
# Returns:
#   - str: The resolved provider name.
###############################################################################
def get_ai_provider(provider: str = None) -> str:
    if provider is None and herd_config:
        provider = herd_config.get_provider()
    if provider is None:
        provider = DEFAULT_AI_PROVIDER
    if provider not in AI_PROVIDERS:
        logger.warning(f"Unknown AI provider '{provider}', falling back to {DEFAULT_AI_PROVIDER}")
        provider = DEFAULT_AI_PROVIDER
    return provider

###############################################################################
# process_with_ai
#
# Processes a file (text or image) with the selected AI provider and model.
#
# Arguments:
#   - file_path (str | Path): Path to the file to process.
#   - prompt (str): Prompt or description to send to the AI.
#   - provider (str, optional): AI provider to use. If None, uses default.
#   - custom_system_prompt (str, optional): Custom system prompt to override
#     the default instruction or image alt text template.
#
# Returns:
#   - str | dict | None: The AI response, or None if processing failed.
#
# Provider Credentials:
#   - Ollama: No credentials required (local API)
#   - X.AI: Requires XAI_API_KEY (see config or environment)
#   - Gemini: Requires GEMINI_API_KEY (see config or environment)
#   - OpenAI: Requires OPENAI_API_KEY (see config or environment)
###############################################################################
def process_with_ai(
    file_path: Union[str, Path],
    prompt: str,
    provider: str = None,
    custom_system_prompt: str = None,
    **kwargs
) -> Optional[Union[str, dict]]:
    provider = get_ai_provider(provider)
    is_image = is_image_extension(file_path)
    system_prompt = custom_system_prompt or (IMAGE_ALT_TEXT_TEMPLATE if is_image else INSTRUCTION_TEMPLATE)
    logger.info(f"Processing {file_path} with {provider}")

    try:
        if provider == "ollama":
            if is_image:
                response = ollama.send_image_prompt_to_ollama(
                    image_path=str(file_path),
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_prompt=system_prompt
                )
                return response
            else:
                return ollama.send_prompt_to_ollama(
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_prompt=system_prompt
                )
        elif provider == "xai":
            if is_image:
                return xai.send_image_to_xai(
                    str(file_path),
                    model=get_model_for_file(file_path, provider),
                    prompt=system_prompt
                )
            else:
                return xai.send_prompt_to_xai(
                    description=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_prompt=system_prompt
                )
        elif provider == "gemini":
            if is_image:
                return gemini.send_image_to_gemini(
                    str(file_path),
                    model=get_model_for_file(file_path, provider),
                    prompt=system_prompt
                )
            else:
                return gemini.send_prompt_to_gemini(
                    description=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_prompt=system_prompt
                )
        elif provider == "cohere":
            if cohere is not None:
                return cohere.process_with_cohere(
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_message=system_prompt,
                    **kwargs
                )
            else:
                logger.error("Cohere provider requested but module not available")
                return {"text": "Error: Cohere module not available", "error": True}
        elif provider == "openai":
            if is_image:
                return process_with_openai_image(
                    image_path=str(file_path),
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
            else:
                return process_with_openai(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    **kwargs
                )
        elif provider == "mistral":
            if is_image and mistral is not None:
                return mistral.process_image_with_mistral(
                    image_path=str(file_path),
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider)
                )
            elif mistral is not None:
                return mistral.process_with_mistral(
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_message=system_prompt
                )
            else:
                logger.error("Mistral provider requested but module not available")
                return None
        else:
            logger.error(f"Unsupported AI provider: {provider}")
            return None
    except Exception as e:
        error_msg = f"Error processing {file_path} with {provider}: {e}"
        logger.error(error_msg)
        return {"text": error_msg, "error": True, "as_text": True}

###############################################################################
# process_image
#
# Process an image file with the selected AI provider and return analysis.
#
# Arguments:
#   - image_path (str | Path): Path to the image file.
#   - prompt (str): Description or instruction for analyzing the image.
#   - provider (str, optional): AI provider to use. If None, uses default.
#
# Returns:
#   - dict | str | None: AI response containing image analysis.
###############################################################################
def process_image(
    image_path: Union[str, Path],
    prompt: str,
    provider: str = None
) -> Optional[Union[dict, str]]:
    provider = get_ai_provider(provider)
    logger.info(f"Processing image {image_path} with {provider}")
    
    try:
        if provider == "ollama":
            response = ollama.send_image_prompt_to_ollama(
                image_path=str(image_path),
                prompt=prompt,
                model=get_model_for_file(image_path, provider),
                system_prompt=IMAGE_ALT_TEXT_TEMPLATE
            )
            # Pass through the response as is, including any error indicators and as_text flag
            return response
        elif provider == "xai":
            return xai.send_image_to_xai(
                str(image_path),
                model=get_model_for_file(image_path, provider),
                prompt=prompt
            )
        elif provider == "gemini":
            return gemini.send_image_to_gemini(
                str(image_path),
                model=get_model_for_file(image_path, provider),
                prompt=prompt
            )
        elif provider == "openai":
            return process_with_openai_image(
                image_path=str(image_path),
                prompt=prompt,
                system_prompt=IMAGE_ALT_TEXT_TEMPLATE
            )
        elif provider == "mistral" and mistral is not None:
            return mistral.send_image_prompt_to_mistral(
                image_path=str(image_path),
                prompt=prompt,
                description=IMAGE_ALT_TEXT_TEMPLATE
            )
        else:
            logger.error(f"Unsupported AI provider for image processing: {provider}")
            return None
    except Exception as e:
        error_msg = f"Error processing image {image_path} with {provider}: {e}"
        logger.error(error_msg)
        # Return error in a format consistent with the Ollama API error response
        return {"text": error_msg, "error": True, "as_text": True}

###############################################################################
# validate_provider
#
# Check if a provider name is valid and available.
#
# Arguments:
#   - provider (str): Name of the provider to validate.
#
# Returns:
#   - bool: True if the provider is valid and available, False otherwise.
###############################################################################
def validate_provider(provider: str) -> bool:
    if provider not in AI_PROVIDERS:
        logger.error(f"Unknown AI provider: {provider}")
        return False
        
    # For Ollama, check if the local API is available
    if provider == "ollama" and not check_local_provider():
        logger.error("Ollama is not available locally")
        return False
        
    # For X.AI, check if API key is available
    if provider == "xai" and herd_config:
        api_key = herd_config.get_api_key('xai')
        if not api_key:
            logger.error("X.AI API key not found in config or environment")
            return False
            
    # For Gemini, check if API key is available
    if provider == "gemini" and herd_config:
        api_key = herd_config.get_api_key('gemini')
        if not api_key:
            logger.error("Gemini API key not found in config or environment")
            return False
    
    # For OpenAI, check if API key is available
    if provider == "openai" and herd_config:
        api_key = herd_config.get_api_key('openai')
        if not api_key:
            logger.error("OpenAI API key not found in config or environment")
            return False
            
    return True

###############################################################################
# check_local_provider
#
# Check if Ollama is running locally.
#
# Returns:
#   - bool: True if Ollama is available, False otherwise.
###############################################################################
def check_local_provider() -> bool:
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

###############################################################################
# list_models
#
# Get a list of available models for a specific provider.
#
# Arguments:
#   - provider (str, optional): Provider name. If None, uses default provider.
#
# Returns:
#   - list: List of available model names. Empty list if no models available.
###############################################################################
def list_models(provider: str = None) -> list:
    provider = get_ai_provider(provider)
    
    if provider == "ollama":
        try:
            # Use the new Ollama utilities to get models
            models = ollama.get_available_models()
            return [model.get("name", "") for model in models if model.get("name")]
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return ["gemma3:4b", "llama3", "mistral"]
    
    elif provider == "xai":
        return ["grok-3-beta", "grok-2-vision-latest"]
    
    elif provider == "gemini":
        return ["gemini-2.5-flash-latest", "gemini-2.5-pro-latest", "gemini-2.5-flash-preview-04-17"]
    
    elif provider == "cohere":
        if cohere is not None:
            try:
                return cohere.list_cohere_models()
            except Exception as e:
                logger.error(f"Error listing Cohere models: {e}")
                return ["command-a-03-2025", "command-light-a", "command-nightly"]
        else:
            return ["command-a-03-2025", "command-light-a", "command-nightly"]
    
    elif provider == "openai":
        try:
            # Try to get live models if we can
            api_key = get_openai_api_key()
            if api_key and OpenAI:
                client = OpenAI(api_key=api_key)
                response = client.models.list()
                models = []
                for model in response.data:
                    if any(name in model.id for name in ["gpt", "dall-e"]):
                        models.append(model.id)
                return models
            # Fall back to default models list
            return list(OPENAI_DEFAULT_MODELS.keys())
        except Exception as e:
            logger.error(f"Error listing OpenAI models: {e}")
            return list(OPENAI_DEFAULT_MODELS.keys())
    
    elif provider == "mistral":
        if mistral is not None:
            try:
                return mistral.list_mistral_models()
            except Exception as e:
                logger.error(f"Error listing Mistral models: {e}")
                return [model for model in MISTRAL_DEFAULT_MODELS.values()]
        else:
            return [model for model in MISTRAL_DEFAULT_MODELS.values()]
    
    return [] 

###############################################################################
# OpenAI-specific functions
###############################################################################

def get_openai_api_key() -> str:
    """Get OpenAI API key from config or environment."""
    api_key = None
    
    # Try to get from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # Try to get from herd_config if available
    if not api_key and herd_config:
        api_key = herd_config.get_api_key('openai')
    
    # Fall back to the imported constant
    if not api_key:
        api_key = OPENAI_API_KEY
        
    return api_key

def init_openai_client():
    """Initialize and return OpenAI client."""
    if not OpenAI:
        logger.error("OpenAI Python package is not installed. Install with: pip install openai")
        return None
        
    api_key = get_openai_api_key()
    if not api_key:
        logger.error("OpenAI API key not found. Set OPENAI_API_KEY environment variable or configure in settings.")
        return None
        
    return OpenAI(api_key=api_key)

def process_with_openai(
    prompt: str,
    system_prompt: str = None,
    model: str = None,
    max_tokens: int = None,
    temperature: float = 0.7,
    **kwargs
) -> dict:
    """
    Send a prompt to OpenAI's API and return the response.
    
    Args:
        prompt: The user prompt to send
        system_prompt: The system prompt to use
        model: The OpenAI model to use
        max_tokens: Maximum tokens for completion
        temperature: Temperature for sampling (0-2)
        
    Returns:
        Dict with response text and metadata
    """
    client = init_openai_client()
    if not client:
        return {"text": "OpenAI client initialization failed", "error": True}
    
    try:
        # Get model to use
        model = model or DEFAULT_OPENAI_MODEL
        
        # Create messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Set up parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value
                
        # Make the API call
        response = client.chat.completions.create(**params)
        
        # Extract the assistant's message
        result = response.choices[0].message.content
        
        # Return standardized response
        return {
            "text": result,
            "model": model,
            "provider": "openai",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        logger.error(f"Error using OpenAI: {e}")
        return {"text": f"Error: {str(e)}", "error": True, "provider": "openai"}

def process_with_openai_image(
    image_path: str,
    prompt: str,
    system_prompt: str = None,
    model: str = None,
    max_tokens: int = None,
    **kwargs
) -> dict:
    """
    Send an image and prompt to OpenAI's vision model and return the response.
    
    Args:
        image_path: Path to the image file
        prompt: The prompt describing what to do with the image
        system_prompt: The system prompt to use
        model: The OpenAI model to use (must support vision)
        max_tokens: Maximum tokens for completion
        
    Returns:
        Dict with response text and metadata
    """
    client = init_openai_client()
    if not client:
        return {"text": "OpenAI client initialization failed", "error": True}
    
    try:
        # Default to a vision-capable model if none specified
        model = model or "gpt-4o"
        
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        # Prepare base64 encoding for the image
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create messages with the image
        content = [
            {"type": "text", "text": prompt}
        ]
        
        # Add the image content
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{encoded_image}"
            }
        })
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        
        # Set up parameters
        params = {
            "model": model,
            "messages": messages,
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        # Add any additional parameters from kwargs
        for key, value in kwargs.items():
            if key not in params:
                params[key] = value
        
        # Make the API call        
        response = client.chat.completions.create(**params)
        
        # Extract the assistant's message
        result = response.choices[0].message.content
        
        # Return standardized response
        return {
            "text": result,
            "model": model,
            "provider": "openai",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        logger.error(f"Error using OpenAI vision: {e}")
        return {"text": f"Error: {str(e)}", "error": True, "provider": "openai"} 