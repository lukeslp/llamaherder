# =============================================================================
# herd_ai.utils.xai
# -----------------------------------------------------------------------------
# Utilities for interacting with the X.AI API, including:
#   - Sending text prompts to X.AI models
#   - Sending images for vision model analysis
#   - Encoding images for API transmission
#   - Validating API credentials
#
# Credentials:
#   - XAI_API_KEY: API key for authenticating with X.AI (from config or env)
#   - XAI_API_URL: Base URL for X.AI API endpoints
#   - XAI_TEXT_MODEL: Default text model name
#   - XAI_IMAGE_MODEL: Default image model name
#   - INSTRUCTION_TEMPLATE: Default system prompt for text models
#   - IMAGE_ALT_TEXT_TEMPLATE: Default prompt for image alt text
# =============================================================================

import json
import logging
import time
import base64
import gc
from typing import Optional, Dict, Any, Union
import requests
import os

# =============================================================================
# Configuration Import Logic
# Attempts to import X.AI credentials and settings from various locations.
# Falls back to defaults if not found.
# =============================================================================
try:
    try:
        from herd_ai.config import XAI_API_KEY, XAI_API_URL, XAI_TEXT_MODEL, XAI_IMAGE_MODEL, INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE
    except ImportError:
        try:
            from llamacleaner.config import XAI_API_KEY, XAI_API_URL, XAI_TEXT_MODEL, XAI_IMAGE_MODEL, INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE
        except ImportError:
            from config import XAI_API_KEY, XAI_API_URL, XAI_TEXT_MODEL, XAI_IMAGE_MODEL, INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE
except Exception as e:
    print(f"Error importing modules in utils/xai.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    XAI_API_KEY = ""
    XAI_API_URL = "https://api.x.ai/v1"
    XAI_TEXT_MODEL = "grok-3-mini"
    XAI_IMAGE_MODEL = "grok-2-vision-latest"
    INSTRUCTION_TEMPLATE = "You are a helpful assistant."
    IMAGE_ALT_TEXT_TEMPLATE = "Describe this image in detail."

try:
    from herd_ai.utils import config as herd_config
except ImportError:
    herd_config = None

logger = logging.getLogger(__name__)

# =============================================================================
# get_xai_api_key
# -----------------------------------------------------------------------------
# Retrieves the X.AI API key from the config utility or environment variable.
#
# Returns:
#   str: The API key as a string. Returns an empty string if not found.
# =============================================================================
def get_xai_api_key() -> str:
    if herd_config:
        key = herd_config.get_api_key('xai')
        if key:
            return key
    return os.environ.get("XAI_API_KEY", XAI_API_KEY)

# =============================================================================
# encode_image
# -----------------------------------------------------------------------------
# Encodes an image file as a base64 string for API transmission.
#
# Args:
#   image_path (str): Path to the image file to encode.
#
# Returns:
#   str | None: Base64-encoded image string, or None if encoding fails.
# =============================================================================
def encode_image(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

# =============================================================================
# send_prompt_to_xai
# -----------------------------------------------------------------------------
# Sends a text prompt to the X.AI API and returns the assistant's reply.
#
# Args:
#   description (str): The user message to send.
#   model (str): The X.AI model to use (default: XAI_TEXT_MODEL).
#   system_prompt (str): System prompt to guide model behavior (default: INSTRUCTION_TEMPLATE).
#   max_retries (int): Maximum number of retry attempts (default: 2).
#   timeout (int): Timeout in seconds for the request (default: 60).
#
# Returns:
#   str | None: The model's response text, or None if an error occurred.
#
# Credentials:
#   Requires a valid X.AI API key.
# =============================================================================
def send_prompt_to_xai(
    description: str,
    model: str = XAI_TEXT_MODEL,
    system_prompt: str = INSTRUCTION_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 60
) -> Optional[str]:
    api_key = get_xai_api_key()
    if not api_key:
        logger.error("X.AI API key not set. Please set the XAI_API_KEY environment variable or use the login command.")
        return None

    for attempt in range(max_retries + 1):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": description}
                ],
                "temperature": 0.01,
                "response_format": {"type": "text"}
            }
            logger.info(f"Sending request to X.AI API: {XAI_API_URL}/chat/completions")
            logger.info(f"Using model: {model}")
            logger.debug(f"Content length: {len(description)}")
            start_time = time.time()
            try:
                resp = requests.post(
                    f"{XAI_API_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                logger.debug(f"Response status code: {resp.status_code}")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error - Is the X.AI API accessible? Error: {e}")
                raise

            if resp.status_code != 200:
                error_text = resp.text if len(resp.text) < 500 else f"{resp.text[:500]}..."
                logger.error(f"X.AI HTTP error: {resp.status_code} - {error_text}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return None

            try:
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to parse X.AI response as JSON: {e}")
                logger.error(f"Raw response: {resp.text}")
                return None

            suggestion = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not suggestion:
                logger.warning("Empty or unexpected response from X.AI API.")
                logger.error(f"Full response: {json.dumps(data)[:500]}")
                return None

            text = suggestion.strip()
            logger.info(f"X.AI response received in {time.time() - start_time:.2f} seconds, length: {len(text)}")
            logger.debug(f"Response preview: {text[:100]}...")

            if text.lower().startswith("please") or "i need more" in text.lower():
                logger.warning("LLM is asking for more information, treating as no suggestion")
                return None

            return text
        except requests.RequestException as e:
            logger.error(f"X.AI request error (attempt {attempt+1}/{max_retries+1}): {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
        except Exception as e:
            logger.error(f"Unexpected error calling X.AI: {e}")
            return None

# =============================================================================
# send_image_to_xai
# -----------------------------------------------------------------------------
# Sends an image to the X.AI Vision API and returns the generated description.
#
# Args:
#   image_path (str): Path to the image file.
#   model (str): The X.AI vision model to use (default: XAI_IMAGE_MODEL).
#   prompt (str): Prompt to guide the model's image analysis (default: IMAGE_ALT_TEXT_TEMPLATE).
#   max_retries (int): Maximum number of retry attempts (default: 2).
#   timeout (int): Timeout in seconds for the request (default: 90).
#
# Returns:
#   dict | None: Dictionary with image description data, or None if an error occurred.
#
# Credentials:
#   Requires a valid X.AI API key.
# =============================================================================
def send_image_to_xai(
    image_path: str,
    model: str = XAI_IMAGE_MODEL,
    prompt: str = IMAGE_ALT_TEXT_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 90
) -> Optional[Dict]:
    api_key = get_xai_api_key()
    if not api_key:
        logger.error("X.AI API key not set. Please set the XAI_API_KEY environment variable or use the login command.")
        return None

    MAX_FILE_SIZE_MB = 20
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        logger.error(f"Image too large ({file_size_mb:.1f} MB > {MAX_FILE_SIZE_MB} MB): {image_path}")
        return None

    for attempt in range(max_retries + 1):
        try:
            base64_image = encode_image(image_path)
            if not base64_image:
                logger.error(f"Failed to encode image: {image_path}")
                return None

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.01,
                "response_format": {"type": "json_object"}
            }
            logger.info(f"Sending image request to X.AI API: {XAI_API_URL}/chat/completions")
            logger.info(f"Using model: {model}")
            logger.info(f"Image size: {file_size_mb:.2f} MB, Base64 length: {len(base64_image[:20])}...{len(base64_image)} chars")
            start_time = time.time()
            try:
                resp = requests.post(
                    f"{XAI_API_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout
                )
                logger.info(f"Response status code: {resp.status_code}")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error - Is the X.AI API accessible? Error: {e}")
                raise

            if resp.status_code != 200:
                error_text = resp.text if len(resp.text) < 500 else f"{resp.text[:500]}..."
                logger.error(f"X.AI HTTP error: {resp.status_code} - {error_text}")

                if resp.status_code == 400 and "multimodal data" in error_text.lower():
                    logger.warning("Got a multimodal data error. Returning dummy result to avoid blocking workflow.")
                    return {
                        "alt_text": f"Image from {os.path.basename(image_path)} (X.AI parsing error)",
                        "description": f"This is a placeholder for an image that X.AI was unable to parse: {os.path.basename(image_path)}",
                        "tags": ["placeholder", "error"],
                        "suggested_filename": f"image_{os.path.splitext(os.path.basename(image_path))[0]}"
                    }

                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return None

            try:
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to parse X.AI response as JSON: {e}")
                logger.error(f"Raw response: {resp.text}")
                return None

            generated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not generated_text:
                logger.warning("Empty or unexpected response from X.AI API.")
                return None

            try:
                result = json.loads(generated_text)
                logger.info(f"X.AI image response received in {time.time() - start_time:.2f} seconds")
                logger.info(f"X.AI image response length: {len(generated_text)} chars")
                logger.info(f"X.AI image response has keys: {', '.join(result.keys())}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Raw response: {generated_text[:200]}...")
                import re
                json_match = re.search(r'{[\s\S]*}', generated_text)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                        return result
                    except:
                        pass
                return None

        except requests.RequestException as e:
            logger.error(f"X.AI image request error (attempt {attempt+1}/{max_retries+1}): {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
        except Exception as e:
            logger.error(f"Unexpected error processing image with X.AI: {e}")
            return None
        finally:
            gc.collect()

# =============================================================================
# validate_xai_api_key
# -----------------------------------------------------------------------------
# Validates the X.AI API key by making a lightweight request to the /models endpoint.
#
# Args:
#   api_key (str): The API key to validate.
#
# Returns:
#   bool: True if the API key is valid, False otherwise.
# =============================================================================
def validate_xai_api_key(api_key: str) -> bool:
    url = f"{XAI_API_URL}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return True
        else:
            logger.error(f"X.AI API key validation failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Error validating X.AI API key: {e}")
        return False 