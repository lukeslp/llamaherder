#!/usr/bin/env python
"""
Simple development server for the AI Image Generator.
Run this script to serve both the static frontend files and proxy API requests.
"""

import os
import sys
import logging
import requests
from flask import Flask, send_from_directory, request, jsonify, Response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for the API
API_BASE_URL = "https://api.assisted.space/v2"
# Define the path to static files
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Create Flask app
app = Flask(__name__, static_folder=STATIC_DIR)

# CORS headers for all responses
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses."""
    origin = request.headers.get('Origin', '*')
    response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Accept, Origin, Authorization, X-API-Key, Range',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Expose-Headers': 'Content-Length, Content-Range, Content-Disposition',
        'Access-Control-Max-Age': '3600',
        'Vary': 'Origin'
    })
    
    # If this is a preflight request, return immediately
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response
        
    return response

# Serve index.html at root
@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

# Serve static files
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(STATIC_DIR, path)

# API proxy for v2
@app.route('/v2', methods=['GET', 'OPTIONS'])
def api_info():
    """Forward requests to the API."""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
    
    try:
        # Forward request to actual API
        response = requests.get(API_BASE_URL)
        return jsonify(response.json())
    except Exception as e:
        logger.error(f"Error proxying API info request: {str(e)}")
        # Return a simulated response for development
        return jsonify({
            'status': 'ok',
            'version': 'v2',
            'providers': {
                'openai': True,
                'xai': True,
                'gemini': True
            }
        })

# API proxy for generate endpoint
@app.route('/v2/generate', methods=['POST', 'OPTIONS'])
def generate_image():
    """Proxy image generation requests."""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 204
    
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Forward request to actual API
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Origin': request.headers.get('Origin', '*')
        }
        
        # Forward authorization headers if present
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        if 'X-API-Key' in request.headers:
            headers['X-API-Key'] = request.headers['X-API-Key']
        
        response = requests.post(
            f"{API_BASE_URL}/generate",
            json=data,
            headers=headers
        )
        
        if not response.ok:
            return jsonify({"error": "API request failed", "details": response.text}), response.status_code
            
        # Parse the response
        try:
            response_data = response.json()
            
            # Ensure consistent format
            if response_data.get('data') and isinstance(response_data['data'], list):
                # Response is already in the correct format
                return jsonify(response_data)
            else:
                # Convert to standard format
                return jsonify({
                    "data": [{
                        "url": response_data.get('url') or response_data.get('image_url'),
                        "b64_json": response_data.get('b64_json'),
                        "revised_prompt": response_data.get('revised_prompt')
                    }]
                })
        except ValueError:
            # If response is not JSON, return error
            return jsonify({"error": "Invalid response from API"}), 500
        
    except Exception as e:
        logger.error(f"Error proxying generate image request: {str(e)}")
        # For development, return a mock response
        return jsonify({
            "data": [{
                "url": "https://placehold.co/512x512/random/random?text=API+Connection+Error",
                "revised_prompt": "Sample image (API unavailable)"
            }]
        })

# API proxy for images
@app.route('/v2/proxy-image', methods=['GET', 'OPTIONS'])
def proxy_image():
    """Proxy image requests to handle CORS."""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({"error": "No image URL provided"}), 400
        
        # Forward request to the image URL
        headers = {
            'User-Agent': request.headers.get('User-Agent', 'Mozilla/5.0'),
            'Accept': 'image/*',
            'Origin': request.headers.get('Origin', '*')
        }
        
        # Add authorization headers for X.AI if needed
        if 'x.ai' in image_url or 'xai' in image_url:
            headers['Authorization'] = request.headers.get('Authorization', '')
            headers['X-API-Key'] = request.headers.get('X-API-Key', '')
        
        response = requests.get(
            image_url,
            stream=True,
            headers=headers,
            allow_redirects=True  # Follow redirects
        )
        
        if not response.ok:
            logger.error(f"Failed to fetch image from {image_url}: {response.status_code}")
            return jsonify({"error": f"Failed to fetch image: {response.status_code}"}), response.status_code
        
        # Get content type from response or default to png
        content_type = response.headers.get('Content-Type', 'image/png')
        if not content_type.startswith('image/'):
            content_type = 'image/png'
        
        # Return the image with proper headers
        headers = {
            'Content-Type': content_type,
            'Content-Disposition': 'attachment',
            'Access-Control-Allow-Origin': request.headers.get('Origin', '*'),
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
            'Cache-Control': 'no-cache'
        }
        
        return Response(
            response.content,
            status=200,
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"Error proxying image request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting local development server at http://localhost:{port}")
    logger.info(f"API requests will be proxied to {API_BASE_URL}")
    logger.info("Press Ctrl+C to quit")
    app.run(host='0.0.0.0', port=port, debug=True) 