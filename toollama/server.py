from flask import Flask, send_from_directory, request, Response, jsonify, redirect, render_template_string
from flask_cors import CORS
import os
import requests
import json
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup  # Required for parsing HTML in the Apple News functions

# Configure logging
def setup_logging():
    # Configure root logger
    logging.basicConfig(level=logging.WARNING)  # Only show warnings and above by default
    logger = logging.getLogger('toollama')
    logger.setLevel(logging.INFO)  # Show important info for our app
    
    # Create simple formatter
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File Handler for errors
    os.makedirs('logs', exist_ok=True)
    file_handler = RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10*1024*1024,
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
    file_handler.setLevel(logging.ERROR)
    
    # Set levels for noisy modules
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('fsevents').setLevel(logging.ERROR)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Initialize logging
logger = setup_logging()
logger.info("Starting server application...")

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
        "expose_headers": ["Content-Type", "X-Total-Count"],
        "supports_credentials": False,
        "max_age": "3600",
        "send_wildcard": True
    }
})

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept, Origin, X-Requested-With'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type, X-Total-Count'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    if request.method == 'OPTIONS':
        response.status_code = 204
    return response

@app.route('/')
def serve_index():
    logger.info("Serving index.html")
    return send_from_directory('.', 'index.html')

# Proxy route for Ollama API
@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def proxy_ollama_chat():
    logger.info(f"Chat endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    if request.method == 'OPTIONS':
        logger.debug("Handling OPTIONS request for chat endpoint")
        return '', 204
        
    try:
        logger.info("Forwarding request to Ollama API")
        logger.debug(f"Request data: {request.json}")
        
        response = requests.post(
            'http://localhost:11434/api/chat',
            json=request.json,
            stream=True
        )
        logger.debug(f"Ollama API response status: {response.status_code}")
        
        def generate():
            for chunk in response.iter_lines():
                if chunk:
                    logger.debug(f"Streaming chunk: {chunk}")
                    yield chunk + b'\n'
                    
        return Response(
            generate(),
            content_type=response.headers['content-type'],
            status=response.status_code
        )
    except Exception as e:
        logger.exception("Error in chat endpoint")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def proxy_ollama_generate():
    logger.info(f"Generate endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    if request.method == 'OPTIONS':
        logger.debug("Handling OPTIONS request for generate endpoint")
        return '', 204
        
    try:
        logger.info("Forwarding request to Ollama generate API")
        logger.debug(f"Request data: {request.json}")
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=request.json,
            stream=True
        )
        logger.debug(f"Ollama API response status: {response.status_code}")
        
        def generate():
            for chunk in response.iter_lines():
                if chunk:
                    logger.debug(f"Streaming chunk: {chunk}")
                    yield chunk + b'\n'
                    
        return Response(
            generate(),
            content_type=response.headers['content-type'],
            status=response.status_code
        )
    except Exception as e:
        logger.exception("Error in generate endpoint")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags', methods=['GET', 'OPTIONS'])
def proxy_ollama_tags():
    logger.info(f"Tags endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    if request.method == 'OPTIONS':
        logger.debug("Handling OPTIONS request for tags endpoint")
        return '', 204
        
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

@app.route('/api/tts', methods=['POST', 'OPTIONS'])
def tts():
    logger.info(f"TTS endpoint called with method: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    
    if request.method == 'OPTIONS':
        logger.debug("Handling OPTIONS request for TTS endpoint")
        return '', 204
    
    try:
        data = request.get_json()
        logger.debug(f"Received TTS request data: {data}")
        
        text = data.get('text')
        target_language = data.get('targetLanguage')
        
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
        
        # Log the output for debugging
        if result.stdout:
            logger.info(f"Command stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Command stderr: {result.stderr}")
            
        logger.debug(f"Command return code: {result.returncode}")
            
        if result.returncode != 0:
            logger.error(f"TTS failed: {result.stderr}")
            return jsonify({'error': f'TTS failed: {result.stderr}'}), 500
            
        if not os.path.exists(output_path):
            logger.error("TTS failed: No audio file generated")
            return jsonify({'error': 'TTS failed - no audio file generated'}), 500
            
        logger.info("TTS API: Successfully generated audio")
        # Return the relative URL path
        return jsonify({
            'status': 'completed',
            'audioPath': f'/static/audio/{filename}'
        })
    except Exception as e:
        logger.exception("TTS command failed with exception")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop-tts', methods=['POST'])
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

# -------------------------------------------
# New Helper Functions for Apple News Redirect
# -------------------------------------------
def extract_original_url(apple_news_url: str) -> str:
    """
    Fetches the provided Apple News URL and attempts to extract the original article URL.
    
    This function first performs a request using a mobile user-agent to trigger any redirects.
    If the final URL does not contain "apple.news", it is returned as the original URL.
    Otherwise, it parses the HTML for an anchor tag or meta refresh that may contain the URL.
    
    :param apple_news_url: The URL from Apple News that may be behind a paywall.
    :return: The original article URL if found; otherwise, None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) '
                      'AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    }
    try:
        resp = requests.get(apple_news_url, headers=headers, timeout=10)
        if resp.url and "apple.news" not in resp.url:
            logger.info("Extracted original from redirect: %s", resp.url)
            return resp.url
        
        # Otherwise parse HTML for anchor tags
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith("http") and "apple.news" not in href:
                logger.info("Found original URL in anchor: %s", href)
                return href

        # Check for meta refresh tag
        meta = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta:
            content = meta.get('content', '')
            if "URL=" in content:
                parts = content.split("URL=")
                if len(parts) > 1:
                    candidate = parts[1].strip()
                    if candidate.startswith("http") and "apple.news" not in candidate:
                        logger.info("Found original URL in meta refresh: %s", candidate)
                        return candidate
    except Exception as e:
        logger.error("Error extracting original URL: %s", e)
    return None

def check_proxy_for_block(proxy_url: str) -> bool:
    """
    Fetches the entire HTML from the given proxy URL (e.g., constructed from 12ft.io) and checks
    if it contains any messages (such as prompts to enable JavaScript or disable ad blockers)
    which indicate that the article is not served as expected.
    
    Logs the first ~4000 characters of fetched content for debugging purposes.
    
    :param proxy_url: The URL constructed with 12ft.io for bypassing paywalls.
    :return: True if the proxy HTML suggests a blockage; otherwise, False.
    """
    try:
        resp = requests.get(proxy_url, timeout=10)
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
        for kw in keywords:
            if kw in text_lower:
                logger.info("Detected keyword '%s' in proxy HTML => block", kw)
                return True
    except Exception as e:
        logger.error("Error fetching proxy: %s", e)
        return True
    return False

# -------------------------------------------
# New API Endpoint for Apple News Redirector
# -------------------------------------------
@app.route('/api/apple-news', methods=['POST'])
def apple_news_redirect():
    """
    API Endpoint for processing an Apple News link.
    
    Expects a JSON request with a key 'link' containing the Apple News URL, for example:
    {
        "link": "https://apple.news/..."
    }
    
    Workflow:
      1. Validates that the provided URL contains "apple.news".
      2. Uses `extract_original_url` to determine the original article URL.
      3. Constructs a bypass URL by prepending "https://12ft.io/".
      4. Checks the bypass URL using `check_proxy_for_block` to determine if it is blocked.
      5. Returns a JSON response with the constructed URL and the original URL.
      
    Accessibility Considerations:
      - Provides clear, descriptive error messages in the JSON response.
      
    CORS:
      - Inherits CORS configurations from the global settings.
    """
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data provided in apple news redirect endpoint")
            return jsonify({'error': 'No JSON data provided'}), 400

        link = data.get('link', '').strip()
        if not link or "apple.news" not in link:
            logger.error("Invalid Apple News link provided")
            return jsonify({'error': 'Please provide a valid Apple News link containing "apple.news".'}), 400

        logger.info(f"Processing Apple News link: {link}")
        original = extract_original_url(link)
        if not original:
            logger.error("Could not extract the original URL from the provided Apple News link.")
            return jsonify({'error': 'Could not extract the original URL from the given Apple News link. It may be unsupported.'}), 400

        # Construct 12ft.io URL for paywall bypass
        new_url = "https://12ft.io/" + original
        logger.info(f"Constructed 12ft.io URL: {new_url}")

        # Check if the proxy page is indicating a block (e.g., due to JS/adblock requirements)
        if check_proxy_for_block(new_url):
            logger.error("Blocked by 12ft.io: It appears that JavaScript/adblock restriction is active.")
            return jsonify({'error': ("12ft.io indicates 'Please enable JS and disable any ad blocker'. "
                                      "It may not serve the article as expected.")}), 400

        logger.info("Successfully processed Apple News redirect request")
        return jsonify({'url': new_url, 'original': original})
    except Exception as e:
        logger.exception("Error processing Apple News redirect endpoint")
        return jsonify({'error': str(e)}), 500

@app.route('/<path:path>')
def serve_file(path):
    logger.info(f"Serving file: {path}")
    return send_from_directory('.', path)

if __name__ == '__main__':
    logger.info("Starting Flask development server...")
    # Try to load existing tunnel info if available
    try:
        with open('tunnel_info.json', 'r') as f:
            TUNNEL_INFO = json.load(f)
            logger.info("Loaded tunnel information")
            logger.debug(f"Tunnel info: {TUNNEL_INFO}")
    except Exception as e:
        logger.warning(f"Could not load tunnel information: {str(e)}")
        
    app.run(port=8000, debug=True, host='0.0.0.0')