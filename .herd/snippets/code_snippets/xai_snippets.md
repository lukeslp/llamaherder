# Code Snippets from build/lib/herd_ai/utils/xai.py

File: `build/lib/herd_ai/utils/xai.py`  
Language: Python  
Extracted: 2025-06-07 05:09:17  

## Snippet 1
Lines 16-30

```Python
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
```

## Snippet 2
Lines 31-59

```Python
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
```

## Snippet 3
Lines 84-94

```Python
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
```

## Snippet 4
Lines 111-118

```Python
def send_prompt_to_xai(
    description: str,
    model: str = XAI_TEXT_MODEL,
    system_prompt: str = INSTRUCTION_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 60
) -> Optional[str]:
    api_key = get_xai_api_key()
```

## Snippet 5
Lines 119-122

```Python
if not api_key:
        logger.error("X.AI API key not set. Please set the XAI_API_KEY environment variable or use the login command.")
        return None
```

## Snippet 6
Lines 123-153

```Python
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
```

## Snippet 7
Lines 164-171

```Python
try:
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to parse X.AI response as JSON: {e}")
                logger.error(f"Raw response: {resp.text}")
                return None

            suggestion = data.get("choices", [{}])[0].get("message", {}).get("content", "")
```

## Snippet 8
Lines 172-177

```Python
if not suggestion:
                logger.warning("Empty or unexpected response from X.AI API.")
                logger.error(f"Full response: {json.dumps(data)[:500]}")
                return None

            text = suggestion.strip()
```

## Snippet 9
Lines 194-197

```Python
except Exception as e:
            logger.error(f"Unexpected error calling X.AI: {e}")
            return None
```

## Snippet 10
Lines 216-223

```Python
def send_image_to_xai(
    image_path: str,
    model: str = XAI_IMAGE_MODEL,
    prompt: str = IMAGE_ALT_TEXT_TEMPLATE,
    max_retries: int = 2,
    timeout: int = 90
) -> Optional[Dict]:
    api_key = get_xai_api_key()
```

## Snippet 11
Lines 224-229

```Python
if not api_key:
        logger.error("X.AI API key not set. Please set the XAI_API_KEY environment variable or use the login command.")
        return None

    MAX_FILE_SIZE_MB = 20
    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
```

## Snippet 12
Lines 234-236

```Python
for attempt in range(max_retries + 1):
        try:
            base64_image = encode_image(image_path)
```

## Snippet 13
Lines 237-270

```Python
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
```

## Snippet 14
Lines 271-284

```Python
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
```

## Snippet 15
Lines 289-291

```Python
if resp.status_code == 400 and "multimodal data" in error_text.lower():
                    logger.warning("Got a multimodal data error. Returning dummy result to avoid blocking workflow.")
                    return {
```

## Snippet 16
Lines 305-312

```Python
try:
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to parse X.AI response as JSON: {e}")
                logger.error(f"Raw response: {resp.text}")
                return None

            generated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
```

## Snippet 17
Lines 313-318

```Python
if not generated_text:
                logger.warning("Empty or unexpected response from X.AI API.")
                return None

            try:
                result = json.loads(generated_text)
```

## Snippet 18
Lines 320-322

```Python
logger.info(f"X.AI image response length: {len(generated_text)} chars")
                logger.info(f"X.AI image response has keys: {', '.join(result.keys())}")
                return result
```

## Snippet 19
Lines 323-327

```Python
except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON response: {e}")
                logger.error(f"Raw response: {generated_text[:200]}...")
                import re
                json_match = re.search(r'{[\s\S]*}', generated_text)
```

## Snippet 20
Lines 328-335

```Python
if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                        return result
                    except:
                        pass
                return None
```

## Snippet 21
Lines 344-349

```Python
except Exception as e:
            logger.error(f"Unexpected error processing image with X.AI: {e}")
            return None
        finally:
            gc.collect()
```

## Snippet 22
Lines 361-368

```Python
def validate_xai_api_key(api_key: str) -> bool:
    url = f"{XAI_API_URL}/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
```

## Snippet 23
Lines 369-371

```Python
if resp.status_code == 200:
            return True
        else:
```

## Snippet 24
Lines 374-376

```Python
except Exception as e:
        logger.error(f"Error validating X.AI API key: {e}")
        return False
```

