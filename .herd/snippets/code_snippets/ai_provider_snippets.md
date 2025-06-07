# Code Snippets from src/herd_ai/utils/ai_provider.py

File: `src/herd_ai/utils/ai_provider.py`  
Language: Python  
Extracted: 2025-06-07 05:09:57  

## Snippet 1
Lines 24-115

```Python
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
```

## Snippet 2
Lines 121-123

```Python
elif provider == "mistral":
            return DEFAULT_MISTRAL_MODEL
        return "gemma3:4b"
```

## Snippet 3
Lines 126-160

```Python
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
```

## Snippet 4
Lines 175-181

```Python
},
    "mistral-large": {
        "id": "mistral-large",
        "context_length": 32768,
        "description": "Most capable Mistral model",
        "capabilities": ["text", "function", "vision"]
    }
```

## Snippet 5
Lines 202-206

```Python
if provider not in AI_PROVIDERS:
        logger.warning(f"Unknown AI provider '{provider}', falling back to {DEFAULT_AI_PROVIDER}")
        provider = DEFAULT_AI_PROVIDER
    return provider
```

## Snippet 6
Lines 228-236

```Python
def process_with_ai(
    file_path: Union[str, Path],
    prompt: str,
    provider: str = None,
    custom_system_prompt: str = None,
    **kwargs
) -> Optional[Union[str, dict]]:
    provider = get_ai_provider(provider)
    is_image = is_image_extension(file_path)
```

## Snippet 7
Lines 242-255

```Python
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
```

## Snippet 8
Lines 257-268

```Python
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
```

## Snippet 9
Lines 270-281

```Python
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
```

## Snippet 10
Lines 283-292

```Python
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
```

## Snippet 11
Lines 294-306

```Python
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
```

## Snippet 12
Lines 308-313

```Python
if is_image and mistral is not None:
                return mistral.process_image_with_mistral(
                    image_path=str(file_path),
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider)
                )
```

## Snippet 13
Lines 314-322

```Python
elif mistral is not None:
                return mistral.process_with_mistral(
                    prompt=prompt,
                    model=get_model_for_file(file_path, provider),
                    system_message=system_prompt
                )
            else:
                logger.error("Mistral provider requested but module not available")
                return None
```

## Snippet 14
Lines 323-325

```Python
else:
            logger.error(f"Unsupported AI provider: {provider}")
            return None
```

## Snippet 15
Lines 327-330

```Python
error_msg = f"Error processing {file_path} with {provider}: {e}"
        logger.error(error_msg)
        return {"text": error_msg, "error": True, "as_text": True}
```

## Snippet 16
Lines 344-349

```Python
def process_image(
    image_path: Union[str, Path],
    prompt: str,
    provider: str = None
) -> Optional[Union[dict, str]]:
    provider = get_ai_provider(provider)
```

## Snippet 17
Lines 353-361

```Python
if provider == "ollama":
            response = ollama.send_image_prompt_to_ollama(
                image_path=str(image_path),
                prompt=prompt,
                model=get_model_for_file(image_path, provider),
                system_prompt=IMAGE_ALT_TEXT_TEMPLATE
            )
            # Pass through the response as is, including any error indicators and as_text flag
            return response
```

## Snippet 18
Lines 362-367

```Python
elif provider == "xai":
            return xai.send_image_to_xai(
                str(image_path),
                model=get_model_for_file(image_path, provider),
                prompt=prompt
            )
```

## Snippet 19
Lines 368-373

```Python
elif provider == "gemini":
            return gemini.send_image_to_gemini(
                str(image_path),
                model=get_model_for_file(image_path, provider),
                prompt=prompt
            )
```

## Snippet 20
Lines 374-379

```Python
elif provider == "openai":
            return process_with_openai_image(
                image_path=str(image_path),
                prompt=prompt,
                system_prompt=IMAGE_ALT_TEXT_TEMPLATE
            )
```

## Snippet 21
Lines 380-386

```Python
elif provider == "mistral" and mistral is not None:
            return mistral.send_image_prompt_to_mistral(
                image_path=str(image_path),
                prompt=prompt,
                description=IMAGE_ALT_TEXT_TEMPLATE
            )
        else:
```

## Snippet 22
Lines 390-394

```Python
error_msg = f"Error processing image {image_path} with {provider}: {e}"
        logger.error(error_msg)
        # Return error in a format consistent with the Ollama API error response
        return {"text": error_msg, "error": True, "as_text": True}
```

## Snippet 23
Lines 407-410

```Python
if provider not in AI_PROVIDERS:
        logger.error(f"Unknown AI provider: {provider}")
        return False
```

## Snippet 24
Lines 412-415

```Python
if provider == "ollama" and not check_local_provider():
        logger.error("Ollama is not available locally")
        return False
```

## Snippet 25
Lines 419-422

```Python
if not api_key:
            logger.error("X.AI API key not found in config or environment")
            return False
```

## Snippet 26
Lines 426-429

```Python
if not api_key:
            logger.error("Gemini API key not found in config or environment")
            return False
```

## Snippet 27
Lines 433-436

```Python
if not api_key:
            logger.error("OpenAI API key not found in config or environment")
            return False
```

## Snippet 28
Lines 447-456

```Python
def check_local_provider() -> bool:
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except Exception:
        return False

###############################################################################
# list_models
#
```

## Snippet 29
Lines 473-476

```Python
except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return ["gemma3:4b", "llama3", "mistral"]
```

## Snippet 30
Lines 484-492

```Python
if cohere is not None:
            try:
                return cohere.list_cohere_models()
            except Exception as e:
                logger.error(f"Error listing Cohere models: {e}")
                return ["command-a-03-2025", "command-light-a", "command-nightly"]
        else:
            return ["command-a-03-2025", "command-light-a", "command-nightly"]
```

## Snippet 31
Lines 497-500

```Python
if api_key and OpenAI:
                client = OpenAI(api_key=api_key)
                response = client.models.list()
                models = []
```

## Snippet 32
Lines 507-510

```Python
except Exception as e:
            logger.error(f"Error listing OpenAI models: {e}")
            return list(OPENAI_DEFAULT_MODELS.keys())
```

## Snippet 33
Lines 512-516

```Python
if mistral is not None:
            try:
                return mistral.list_mistral_models()
            except Exception as e:
                logger.error(f"Error listing Mistral models: {e}")
```

## Snippet 34
Lines 527-533

```Python
def get_openai_api_key() -> str:
    """Get OpenAI API key from config or environment."""
    api_key = None

    # Try to get from environment
    api_key = os.environ.get("OPENAI_API_KEY")
```

## Snippet 35
Lines 535-538

```Python
if not api_key and herd_config:
        api_key = herd_config.get_api_key('openai')

    # Fall back to the imported constant
```

## Snippet 36
Lines 539-543

```Python
if not api_key:
        api_key = OPENAI_API_KEY

    return api_key
```

## Snippet 37
Lines 546-550

```Python
if not OpenAI:
        logger.error("OpenAI Python package is not installed. Install with: pip install openai")
        return None

    api_key = get_openai_api_key()
```

## Snippet 38
Lines 551-556

```Python
if not api_key:
        logger.error("OpenAI API key not found. Set OPENAI_API_KEY environment variable or configure in settings.")
        return None

    return OpenAI(api_key=api_key)
```

## Snippet 39
Lines 557-571

```Python
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
```

## Snippet 40
Lines 575-578

```Python
Returns:
        Dict with response text and metadata
    """
    client = init_openai_client()
```

## Snippet 41
Lines 579-587

```Python
if not client:
        return {"text": "OpenAI client initialization failed", "error": True}

    try:
        # Get model to use
        model = model or DEFAULT_OPENAI_MODEL

        # Create messages list
        messages = []
```

## Snippet 42
Lines 588-598

```Python
if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Set up parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
```

## Snippet 43
Lines 599-602

```Python
if max_tokens:
            params["max_tokens"] = max_tokens

        # Add any additional parameters from kwargs
```

## Snippet 44
Lines 607-623

```Python
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
```

## Snippet 45
Lines 624-627

```Python
except Exception as e:
        logger.error(f"Error using OpenAI: {e}")
        return {"text": f"Error: {str(e)}", "error": True, "provider": "openai"}
```

## Snippet 46
Lines 628-643

```Python
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
```

## Snippet 47
Lines 646-649

```Python
Returns:
        Dict with response text and metadata
    """
    client = init_openai_client()
```

## Snippet 48
Lines 650-653

```Python
if not client:
        return {"text": "OpenAI client initialization failed", "error": True}

    try:
```

## Snippet 49
Lines 654-660

```Python
# Default to a vision-capable model if none specified
        model = model or "gpt-4o"

        # Read and encode the image
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
```

## Snippet 50
Lines 661-677

```Python
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
```

## Snippet 51
Lines 678-687

```Python
if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})

        # Set up parameters
        params = {
            "model": model,
            "messages": messages,
        }
```

## Snippet 52
Lines 688-691

```Python
if max_tokens:
            params["max_tokens"] = max_tokens

        # Add any additional parameters from kwargs
```

## Snippet 53
Lines 696-712

```Python
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
```

## Snippet 54
Lines 713-715

```Python
except Exception as e:
        logger.error(f"Error using OpenAI vision: {e}")
        return {"text": f"Error: {str(e)}", "error": True, "provider": "openai"}
```

