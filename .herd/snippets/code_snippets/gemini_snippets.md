# Code Snippets from src/herd_ai/utils/gemini.py

File: `src/herd_ai/utils/gemini.py`  
Language: Python  
Extracted: 2025-06-07 05:09:47  

## Snippet 1
Lines 16-30

```Python
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
```

## Snippet 2
Lines 31-59

```Python
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
```

## Snippet 3
Lines 84-94

```Python
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
```

## Snippet 4
Lines 108-115

```Python
def send_prompt_to_gemini(
    description: str,
    model: str = GEMINI_TEXT_MODEL,
    system_prompt: str = INSTRUCTION_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 60
) -> Optional[str]:
    api_key = get_gemini_api_key()
```

## Snippet 5
Lines 116-119

```Python
if not api_key:
        logger.error("Gemini API key not set. Please set the GEMINI_API_KEY environment variable or use the login command.")
        return None
```

## Snippet 6
Lines 120-147

```Python
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
```

## Snippet 7
Lines 158-169

```Python
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
```

## Snippet 8
Lines 177-181

```Python
if not suggestion:
                logger.warning("Empty or unexpected response from Gemini API.")
                logger.error(f"Full response: {json.dumps(data)[:500]}")
                return None
```

## Snippet 9
Lines 184-188

```Python
elif isinstance(suggestion, str):
                return suggestion.strip()
            else:
                logger.warning("Unexpected response type from Gemini API.")
                return None
```

## Snippet 10
Lines 197-200

```Python
except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            return None
```

## Snippet 11
Lines 216-223

```Python
def send_image_to_gemini(
    image_path: str,
    model: str = GEMINI_IMAGE_MODEL,
    prompt: str = IMAGE_ALT_TEXT_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 90
) -> Optional[Dict]:
    api_key = get_gemini_api_key()
```

## Snippet 12
Lines 224-229

```Python
if not api_key:
        logger.error("Gemini API key not set. Please set the GEMINI_API_KEY environment variable or use the login command.")
        return None

    MAX_FILE_SIZE_MB = 20
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
```

## Snippet 13
Lines 234-236

```Python
for attempt in range(max_retries + 1):
        try:
            base64_image = encode_image(image_path)
```

## Snippet 14
Lines 237-264

```Python
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
```

## Snippet 15
Lines 265-274

```Python
logger.info(f"Image size: {file_size_mb:.2f} MB, Base64 length: {len(base64_image[:20])}...{len(base64_image)} chars")

            start_time = time.time()
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
                logger.info(f"Response status code: {resp.status_code}")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error - Is the Gemini API accessible? Error: {e}")
                raise
```

## Snippet 16
Lines 285-296

```Python
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
```

## Snippet 17
Lines 304-308

```Python
if not suggestion:
                logger.warning("Empty or unexpected response from Gemini API.")
                logger.error(f"Full response: {json.dumps(data)[:500]}")
                return None
```

## Snippet 18
Lines 311-315

```Python
elif isinstance(suggestion, str):
                return suggestion.strip()
            else:
                logger.warning("Unexpected response type from Gemini API.")
                return None
```

## Snippet 19
Lines 324-327

```Python
except Exception as e:
            logger.error(f"Unexpected error calling Gemini: {e}")
            return None
```

## Snippet 20
Lines 340-358

```Python
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
```

