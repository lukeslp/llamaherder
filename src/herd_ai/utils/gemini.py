# =============================================================================
# herd_ai.utils.gemini
# -----------------------------------------------------------------------------
# Utilities for interacting with the Google Gemini API, including:
#   - Sending text prompts to Gemini models
#   - Sending images for Gemini Vision model analysis
#   - Encoding images for API transmission
#   - Validating API credentials
#
# Credentials:
#   - GEMINI_API_KEY: API key for authenticating with Gemini (from config or env)
#   - GEMINI_API_URL: Base URL for Gemini API endpoints
#   - GEMINI_TEXT_MODEL: Default text model name
#   - GEMINI_IMAGE_MODEL: Default image model name
#   - INSTRUCTION_TEMPLATE: Default system prompt for text models
#   - IMAGE_ALT_TEXT_TEMPLATE: Default prompt for image alt text
# =============================================================================

import json
import logging
import time
import os
import base64
from typing import Optional, Dict, Any, Union
import requests
from pathlib import Path

# =============================================================================
# Configuration Import Logic
# Attempts to import Gemini credentials and settings from various locations.
# Falls back to defaults if not found.
# =============================================================================
try:
    try:
        from herd_ai.config import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_TEXT_MODEL, GEMINI_IMAGE_MODEL, INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE
    except ImportError:
        try:
            from llamacleaner.config import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_TEXT_MODEL, GEMINI_IMAGE_MODEL, INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE
        except ImportError:
            from config import GEMINI_API_KEY, GEMINI_API_URL, GEMINI_TEXT_MODEL, GEMINI_IMAGE_MODEL, INSTRUCTION_TEMPLATE, IMAGE_ALT_TEXT_TEMPLATE
except Exception as e:
    print(f"Error importing modules in utils/gemini.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    GEMINI_API_KEY = ""
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_TEXT_MODEL = "gemini-2.0-flash"
    GEMINI_IMAGE_MODEL = "gemini-2.0-flash"
    INSTRUCTION_TEMPLATE = "You are a helpful assistant."
    IMAGE_ALT_TEXT_TEMPLATE = "Describe this image in detail."

try:
    from herd_ai.utils import config as herd_config
except ImportError:
    herd_config = None

logger = logging.getLogger(__name__)

# =============================================================================
# get_gemini_api_key
# -----------------------------------------------------------------------------
# Retrieves the Gemini API key from the config utility or environment variable.
#
# Returns:
#   str: The Gemini API key as a string. Returns an empty string if not found.
# =============================================================================
def get_gemini_api_key() -> str:
    if herd_config:
        key = herd_config.get_api_key('gemini')
        if key:
            return key
    return os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)

# =============================================================================
# encode_image
# -----------------------------------------------------------------------------
# Encodes an image file as a base64 string for API transmission.
#
# Args:
#   image_path (str or Path): Path to the image file.
#
# Returns:
#   str: Base64 encoded image string, or None if encoding failed.
# =============================================================================
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()
            return base64.b64encode(image_bytes).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

# =============================================================================
# send_prompt_to_gemini
# -----------------------------------------------------------------------------
# Sends a text prompt to the Google Gemini API and returns the assistant's reply.
#
# Args:
#   description (str): The user message to send.
#   model (str): The Gemini model to use (default: GEMINI_TEXT_MODEL).
#   system_prompt (str): The system prompt to guide the model's behavior (default: INSTRUCTION_TEMPLATE).
#   max_retries (int): Maximum number of retry attempts (default: 2).
#   timeout (int): Timeout in seconds for the request (default: 60).
#
# Returns:
#   Optional[str]: The model's response text, or None if an error occurred.
# =============================================================================
def send_prompt_to_gemini(
    description: str,
    model: str = GEMINI_TEXT_MODEL,
    system_prompt: str = INSTRUCTION_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 60
) -> Optional[str]:
    api_key = get_gemini_api_key()
    if not api_key:
        logger.error("Gemini API key not set. Please set the GEMINI_API_KEY environment variable or use the login command.")
        return None

    for attempt in range(max_retries + 1):
        try:
            headers = {
                "Content-Type": "application/json"
            }
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": description}]}
                ],
                "generationConfig": {
                    "temperature": 0.1
                },
                "system_instruction": {"parts": [{"text": system_prompt}]}
            }
            url = f"{GEMINI_API_URL}/models/{model}:generateContent?key={api_key}"

            logger.info(f"Sending request to Gemini API")
            logger.info(f"Using model: {model}")
            logger.debug(f"Content length: {len(description)}")

            start_time = time.time()
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                logger.debug(f"Response status code: {resp.status_code}")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error - Is the Gemini API accessible? Error: {e}")
                raise

            if resp.status_code != 200:
                error_text = resp.text if len(resp.text) < 500 else f"{resp.text[:500]}..."
                logger.error(f"Gemini HTTP error: {resp.status_code} - {error_text}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return None

            if resp.status_code == 429 or "overloaded" in resp.text.lower():
                logger.error("Gemini model is overloaded. Please try again later.")
                return None

            try:
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Raw response: {resp.text}")
                return None

            suggestion = ""
            if "candidates" in data and data["candidates"]:
                content = data["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "text" in part:
                        suggestion += part["text"]

            if not suggestion:
                logger.warning("Empty or unexpected response from Gemini API.")
                logger.error(f"Full response: {json.dumps(data)[:500]}")
                return None

            if isinstance(suggestion, dict):
                return suggestion
            elif isinstance(suggestion, str):
                return suggestion.strip()
            else:
                logger.warning("Unexpected response type from Gemini API.")
                return None
        except requests.RequestException as e:
            logger.error(f"Gemini request error (attempt {attempt+1}/{max_retries+1}): {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            return None

# =============================================================================
# send_image_to_gemini
# -----------------------------------------------------------------------------
# Sends an image to the Gemini Vision API and returns the generated description.
#
# Args:
#   image_path (str): Path to the image file.
#   model (str): The Gemini vision model to use (default: GEMINI_IMAGE_MODEL).
#   prompt (str): The prompt to guide the model's image analysis (default: IMAGE_ALT_TEXT_TEMPLATE).
#   max_retries (int): Maximum number of retry attempts (default: 2).
#   timeout (int): Timeout in seconds for the request (default: 90).
#
# Returns:
#   Optional[Dict]: Dictionary with image description data or None if an error occurred.
# =============================================================================
def send_image_to_gemini(
    image_path: str,
    model: str = GEMINI_IMAGE_MODEL,
    prompt: str = IMAGE_ALT_TEXT_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 90
) -> Optional[Dict]:
    api_key = get_gemini_api_key()
    if not api_key:
        logger.error("Gemini API key not set. Please set the GEMINI_API_KEY environment variable or use the login command.")
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
                "Content-Type": "application/json"
            }
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": "Describe this image."},
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {"temperature": 0.1}
            }
            url = f"{GEMINI_API_URL}/models/{model}:generateContent?key={api_key}"

            logger.info(f"Sending image request to Gemini API")
            logger.info(f"Using model: {model}")
            logger.info(f"Image size: {file_size_mb:.2f} MB, Base64 length: {len(base64_image[:20])}...{len(base64_image)} chars")

            start_time = time.time()
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                logger.info(f"Response status code: {resp.status_code}")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error - Is the Gemini API accessible? Error: {e}")
                raise

            if resp.status_code != 200:
                error_text = resp.text if len(resp.text) < 500 else f"{resp.text[:500]}..."
                logger.error(f"Gemini HTTP error: {resp.status_code} - {error_text}")
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                return None

            if resp.status_code == 429 or "overloaded" in resp.text.lower():
                logger.error("Gemini model is overloaded. Please try again later.")
                return None

            try:
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Raw response: {resp.text}")
                return None

            suggestion = ""
            if "candidates" in data and data["candidates"]:
                content = data["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "text" in part:
                        suggestion += part["text"]

            if not suggestion:
                logger.warning("Empty or unexpected response from Gemini API.")
                logger.error(f"Full response: {json.dumps(data)[:500]}")
                return None

            if isinstance(suggestion, dict):
                return suggestion
            elif isinstance(suggestion, str):
                return suggestion.strip()
            else:
                logger.warning("Unexpected response type from Gemini API.")
                return None
        except requests.RequestException as e:
            logger.error(f"Gemini request error (attempt {attempt+1}/{max_retries+1}): {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None
        except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            return None

# =============================================================================
# validate_gemini_api_key
# -----------------------------------------------------------------------------
# Validates that the provided API key is valid for the Gemini API.
#
# Args:
#   api_key (str): The API key to validate.
#
# Returns:
#   bool: True if the API key is valid, False otherwise.
# =============================================================================
def validate_gemini_api_key(api_key: str) -> bool:
    if not api_key:
        return False

    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": "Hello, just testing my API key."}]}
        ]
    }

    try:
        url = f"{GEMINI_API_URL}/models/gemini-2.0-flash:generateContent?key={api_key}"
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        logger.error(f"Error validating Gemini API key: {e}")
        return False 