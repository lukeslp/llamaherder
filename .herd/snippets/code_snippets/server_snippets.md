# Code Snippets from toollama/server.py

File: `toollama/server.py`  
Language: Python  
Extracted: 2025-06-07 05:08:14  

## Snippet 1
Lines 1-9

```Python
from flask import Flask, send_from_directory, request, Response, jsonify, redirect, render_template_string
from flask_cors import CORS
import os
import requests
import json
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler
```

## Snippet 2
Lines 10-12

```Python
from bs4 import BeautifulSoup  # Required for parsing HTML in the Apple News functions

# Configure logging
```

## Snippet 3
Lines 13-16

```Python
def setup_logging():
    # Configure root logger
    logging.basicConfig(level=logging.WARNING)  # Only show warnings and above by default
    logger = logging.getLogger('toollama')
```

## Snippet 4
Lines 17-26

```Python
logger.setLevel(logging.INFO)  # Show important info for our app

    # Create simple formatter
    formatter = logging.Formatter('%(levelname)s: %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
```

## Snippet 5
Lines 27-36

```Python
# File Handler for errors
    os.makedirs('logs', exist_ok=True)
    file_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10*1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    file_handler.setLevel(logging.ERROR)
```

## Snippet 6
Lines 37-45

```Python
# Set levels for noisy modules
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('fsevents').setLevel(logging.ERROR)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

## Snippet 7
Lines 46-53

```Python
# Initialize logging
logger = setup_logging()
logger.info("Starting server application...")

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
```

## Snippet 8
Lines 54-62

```Python
r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        "expose_headers": ["Content-Type", "X-Total-Count"],
        "supports_credentials": False,
        "max_age": "3600",
        "send_wildcard": True
    }
```

## Snippet 9
Lines 68-77

```Python
if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'

    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, X-Total-Count'
    response.headers['Access-Control-Max-Age'] = '3600'
```

## Snippet 10
Lines 78-81

```Python
if request.method == 'OPTIONS':
        response.status_code = 204
    return response
```

## Snippet 11
Lines 83-86

```Python
def serve_index():
    logger.info("Serving index.html")
    return send_from_directory('.', 'index.html')
```

## Snippet 12
Lines 89-92

```Python
def proxy_ollama_chat():
    logger.info(f"Chat endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
```

## Snippet 13
Lines 97-107

```Python
try:
        logger.info("Forwarding request to Ollama API")
        logger.debug(f"Request data: {request.json}")

        response = requests.post(
            'http://localhost:11434/api/chat',
            json=request.json,
            stream=True
        )
        logger.debug(f"Ollama API response status: {response.status_code}")
```

## Snippet 14
Lines 110-113

```Python
if chunk:
                    logger.debug(f"Streaming chunk: {chunk}")
                    yield chunk + b'\n'
```

## Snippet 15
Lines 114-118

```Python
return Response(
            generate(),
            content_type=response.headers['content-type'],
            status=response.status_code
        )
```

## Snippet 16
Lines 119-122

```Python
except Exception as e:
        logger.exception("Error in chat endpoint")
        return jsonify({'error': str(e)}), 500
```

## Snippet 17
Lines 124-127

```Python
def proxy_ollama_generate():
    logger.info(f"Generate endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
```

## Snippet 18
Lines 132-142

```Python
try:
        logger.info("Forwarding request to Ollama generate API")
        logger.debug(f"Request data: {request.json}")

        response = requests.post(
            'http://localhost:11434/api/generate',
            json=request.json,
            stream=True
        )
        logger.debug(f"Ollama API response status: {response.status_code}")
```

## Snippet 19
Lines 145-148

```Python
if chunk:
                    logger.debug(f"Streaming chunk: {chunk}")
                    yield chunk + b'\n'
```

## Snippet 20
Lines 149-153

```Python
return Response(
            generate(),
            content_type=response.headers['content-type'],
            status=response.status_code
        )
```

## Snippet 21
Lines 154-157

```Python
except Exception as e:
        logger.exception("Error in generate endpoint")
        return jsonify({'error': str(e)}), 500
```

## Snippet 22
Lines 159-162

```Python
def proxy_ollama_tags():
    logger.info(f"Tags endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
```

## Snippet 23
Lines 167-184

```Python
try:
        logger.info("Forwarding request to Ollama tags API")

        response = requests.get(
            'http://localhost:11434/api/tags',
            stream=False
        )
        logger.debug(f"Ollama API response status: {response.status_code}")

        return Response(
            response.content,
            content_type=response.headers['content-type'],
            status=response.status_code
        )
    except Exception as e:
        logger.exception("Error in tags endpoint")
        return jsonify({'error': str(e)}), 500
```

## Snippet 24
Lines 186-189

```Python
def tts():
    logger.info(f"TTS endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
```

## Snippet 25
Lines 194-200

```Python
try:
        data = request.get_json()
        logger.debug(f"Received TTS request data: {data}")

        text = data.get('text')
        target_language = data.get('targetLanguage')
```

## Snippet 26
Lines 201-219

```Python
if not text or not target_language:
            logger.error(f"TTS API: Missing parameters - text: {bool(text)}, language: {bool(target_language)}")
            return jsonify({'error': 'Missing text or targetLanguage'}), 400

        # Create audio directory in the static folder
        audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
        logger.debug(f"Using audio directory: {audio_dir}")
        os.makedirs(audio_dir, exist_ok=True)

        # Generate unique filename
        filename = f"tts_{int(time.time() * 1000)}.mp3"
        output_path = os.path.join(audio_dir, filename)
        logger.debug(f"Generated output path: {output_path}")

        # Escape special characters and quotes
        safe_text = text.replace('"', '\\"').replace("'", "\\'")
        logger.debug(f"Escaped text: {safe_text}")

        # Build the trans command
```

## Snippet 27
Lines 220-246

```Python
command = f'trans -speak -player "mpv" -o "{output_path}" :{target_language} "{safe_text}"'
        logger.info(f"TTS API: Processing '{safe_text[:30]}...' to {target_language}")

        # Set up environment with PATH and other necessary variables
        env = os.environ.copy()
        env['PATH'] = f"{env.get('PATH', '')}:/usr/local/bin:/usr/bin:/bin"
        env['DISPLAY'] = env.get('DISPLAY', ':0')  # For mpv
        env['XDG_RUNTIME_DIR'] = env.get('XDG_RUNTIME_DIR', '/run/user/1000')  # For mpv
        env['HOME'] = env.get('HOME', os.path.expanduser('~'))  # Ensure HOME is set

        logger.debug(f"Environment variables:")
        logger.debug(f"PATH: {env['PATH']}")
        logger.debug(f"DISPLAY: {env['DISPLAY']}")
        logger.debug(f"XDG_RUNTIME_DIR: {env['XDG_RUNTIME_DIR']}")
        logger.debug(f"HOME: {env['HOME']}")

        # Run the command with the enhanced environment
        logger.info("Starting subprocess execution")
        result = subprocess.run(
            command,
            shell=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
```

## Snippet 28
Lines 250-254

```Python
if result.stderr:
            logger.warning(f"Command stderr: {result.stderr}")

        logger.debug(f"Command return code: {result.returncode}")
```

## Snippet 29
Lines 255-258

```Python
if result.returncode != 0:
            logger.error(f"TTS failed: {result.stderr}")
            return jsonify({'error': f'TTS failed: {result.stderr}'}), 500
```

## Snippet 30
Lines 259-268

```Python
if not os.path.exists(output_path):
            logger.error("TTS failed: No audio file generated")
            return jsonify({'error': 'TTS failed - no audio file generated'}), 500

        logger.info("TTS API: Successfully generated audio")
        # Return the relative URL path
        return jsonify({
            'status': 'completed',
            'audioPath': f'/static/audio/{filename}'
        })
```

## Snippet 31
Lines 269-272

```Python
except Exception as e:
        logger.exception("TTS command failed with exception")
        return jsonify({'error': str(e)}), 500
```

## Snippet 32
Lines 274-285

```Python
def stop_tts():
    logger.info("Attempting to stop TTS playback")
    try:
        # Terminate all mpv processes
        logger.debug("Executing pkill mpv command")
        result = subprocess.call(['pkill', 'mpv'])
        logger.info(f"pkill command returned: {result}")
        return jsonify({'status': 'stopped'})
    except Exception as e:
        logger.exception("Failed to stop TTS playback")
        return jsonify({'error': str(e)}), 500
```

## Snippet 33
Lines 289-292

```Python
def extract_original_url(apple_news_url: str) -> str:
    """
    Fetches the provided Apple News URL and attempts to extract the original article URL.
```

## Snippet 34
Lines 295-297

```Python
Otherwise, it parses the HTML for an anchor tag or meta refresh that may contain the URL.

    :param apple_news_url: The URL from Apple News that may be behind a paywall.
```

## Snippet 35
Lines 298-305

```Python
:return: The original article URL if found; otherwise, None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    try:
        resp = requests.get(apple_news_url, headers=headers, timeout=10)
```

## Snippet 36
Lines 306-309

```Python
if resp.url and "apple.news" not in resp.url:
            logger.info("Extracted original from redirect: %s", resp.url)
            return resp.url
```

## Snippet 37
Lines 314-317

```Python
if href.startswith("http") and "apple.news" not in href:
                logger.info("Found original URL in anchor: %s", href)
                return href
```

## Snippet 38
Lines 326-328

```Python
if candidate.startswith("http") and "apple.news" not in candidate:
                        logger.info("Found original URL in meta refresh: %s", candidate)
                        return candidate
```

## Snippet 39
Lines 329-332

```Python
except Exception as e:
        logger.error("Error extracting original URL: %s", e)
    return None
```

## Snippet 40
Lines 333-335

```Python
def check_proxy_for_block(proxy_url: str) -> bool:
    """
    Fetches the entire HTML from the given proxy URL (e.g., constructed from 12ft.io) and checks
```

## Snippet 41
Lines 342-345

```Python
:return: True if the proxy HTML suggests a blockage; otherwise, False.
    """
    try:
        resp = requests.get(proxy_url, timeout=10)
```

## Snippet 42
Lines 346-363

```Python
if resp.status_code != 200:
            logger.info("Proxy returned non-200 status: %s", resp.status_code)
            return True

        content = resp.text
        snippet = content[:4000]
        logger.info("First 4000 chars of proxy response:\n%s\n", snippet)

        text_lower = " ".join(content.split()).lower()
        keywords = [
            "please enable js and disable any ad blocker",
            "enable javascript to run this app",
            "disable adblock to proceed",
            "disable any ad blocker",
            "please enable javascript",
            "please disable adblock",
            "turn off your ad blocker",
        ]
```

## Snippet 43
Lines 365-367

```Python
if kw in text_lower:
                logger.info("Detected keyword '%s' in proxy HTML => block", kw)
                return True
```

## Snippet 44
Lines 368-372

```Python
except Exception as e:
        logger.error("Error fetching proxy: %s", e)
        return True
    return False
```

## Snippet 45
Lines 381-389

```Python
Expects a JSON request with a key 'link' containing the Apple News URL, for example:
    {
        "link": "https://apple.news/..."
    }

    Workflow:
      1. Validates that the provided URL contains "apple.news".
      2. Uses `extract_original_url` to determine the original article URL.
      3. Constructs a bypass URL by prepending "https://12ft.io/".
```

## Snippet 46
Lines 393-400

```Python
Accessibility Considerations:
      - Provides clear, descriptive error messages in the JSON response.

    CORS:
      - Inherits CORS configurations from the global settings.
    """
    try:
        data = request.get_json()
```

## Snippet 47
Lines 401-405

```Python
if not data:
            logger.error("No JSON data provided in apple news redirect endpoint")
            return jsonify({'error': 'No JSON data provided'}), 400

        link = data.get('link', '').strip()
```

## Snippet 48
Lines 406-411

```Python
if not link or "apple.news" not in link:
            logger.error("Invalid Apple News link provided")
            return jsonify({'error': 'Please provide a valid Apple News link containing "apple.news".'}), 400

        logger.info(f"Processing Apple News link: {link}")
        original = extract_original_url(link)
```

## Snippet 49
Lines 412-415

```Python
if not original:
            logger.error("Could not extract the original URL from the provided Apple News link.")
            return jsonify({'error': 'Could not extract the original URL from the given Apple News link. It may be unsupported.'}), 400
```

## Snippet 50
Lines 421-427

```Python
if check_proxy_for_block(new_url):
            logger.error("Blocked by 12ft.io: It appears that JavaScript/adblock restriction is active.")
            return jsonify({'error': ("12ft.io indicates 'Please enable JS and disable any ad blocker'. "
                                      "It may not serve the article as expected.")}), 400

        logger.info("Successfully processed Apple News redirect request")
        return jsonify({'url': new_url, 'original': original})
```

## Snippet 51
Lines 428-431

```Python
except Exception as e:
        logger.exception("Error processing Apple News redirect endpoint")
        return jsonify({'error': str(e)}), 500
```

## Snippet 52
Lines 433-436

```Python
def serve_file(path):
    logger.info(f"Serving file: {path}")
    return send_from_directory('.', path)
```

## Snippet 53
Lines 439-448

```Python
# Try to load existing tunnel info if available
    try:
        with open('tunnel_info.json', 'r') as f:
            TUNNEL_INFO = json.load(f)
            logger.info("Loaded tunnel information")
            logger.debug(f"Tunnel info: {TUNNEL_INFO}")
    except Exception as e:
        logger.warning(f"Could not load tunnel information: {str(e)}")

    app.run(port=8000, debug=True, host='0.0.0.0')
```

