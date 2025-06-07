#!/usr/bin/env python
from flask import Flask, jsonify, send_from_directory, request, Response
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import sys
import json
import tempfile
import logging
import time
import mimetypes
import uuid
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to allow importing API modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from api.config import (
    API_DEBUG, API_HOST, API_PORT, API_BASE_URL, API_VERSION, API_FULL_URL,
    ALLOWED_ORIGINS, MAX_CONTENT_LENGTH, UPLOAD_FOLDER
)

# Import the provider factory
from api.services.provider_factory import ProviderFactory

# Import documentation routes
from api.routes.docs import register_docs_routes

# Import tools routes
from api.routes.tools import tools_bp

# Import dreamwalker routes
from api.routes.dreamwalker import dreamwalker_bp

# Import web search routes
from api.routes.web import web_bp

# Import research search routes
from api.routes.research import research_bp

# Import social routes
from api.routes.social import get_blueprint as get_social_blueprint

# Import news routes
from api.routes.news import get_blueprint as get_news_blueprint

# Import chat routes
from api.routes.chat import chat_bp

# Import API keys from the separate config module
from api.config.api_keys import ADDITIONAL_API_KEYS

# Import Gemini provider
from api.services.providers.gemini import GeminiProvider

# Get provider instances
providers = {
    "anthropic": ProviderFactory.get_provider("anthropic"),
    "mistral": ProviderFactory.get_provider("mistral"),
    "ollama": ProviderFactory.get_provider("ollama"),
    "perplexity": ProviderFactory.get_provider("perplexity"),
    "xai": ProviderFactory.get_provider("xai"),
    "coze": ProviderFactory.get_provider("coze"),
    "mlx": ProviderFactory.get_provider("mlx"),
    "lmstudio": ProviderFactory.get_provider("lmstudio"),
    "gemini": GeminiProvider()
}

# Direct initialization of OpenAI provider with hard-coded API key
try:
    from api.services.providers.openai import OpenAIProvider
    openai_api_key = "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"
    providers["openai"] = OpenAIProvider(api_key=openai_api_key)
    logger.info("Directly initialized OpenAI provider with hard-coded API key")
except Exception as e:
    logger.error(f"Failed to directly initialize OpenAI provider: {str(e)}")
    providers["openai"] = None

# Direct initialization of Cohere provider with the same API key as in cli/cohere.py
try:
    from api.services.providers.cohere import CohereProvider
    cohere_api_key = "8K2VDJ784DPHN57zYauE03mGuslFuaxBW1NUY1LO"  # Exact API key from cli/cohere.py
    providers["cohere"] = CohereProvider(api_key=cohere_api_key)
    logger.info("Directly initialized Cohere provider with API key from cli/cohere.py")
except Exception as e:
    logger.error(f"Failed to directly initialize Cohere provider: {str(e)}")
    providers["cohere"] = None

# Direct initialization of Perplexity provider with hardcoded API key
try:
    from api.services.providers.perplexity import PerplexityProvider, PERPLEXITY_API_KEY
    providers["perplexity"] = PerplexityProvider(api_key=PERPLEXITY_API_KEY)
    logger.info("Directly initialized Perplexity provider with hardcoded API key")
except Exception as e:
    logger.error(f"Failed to directly initialize Perplexity provider: {str(e)}")
    providers["perplexity"] = None

# Direct initialization of Coze provider with hardcoded API key from flask_chat_coze.py
try:
    from api.services.providers.coze import CozeProvider, COZE_AUTH_TOKEN
    providers["coze"] = CozeProvider(api_key=COZE_AUTH_TOKEN)
    logger.info("Directly initialized Coze provider with API key from flask_chat_coze.py")
except Exception as e:
    logger.error(f"Failed to directly initialize Coze provider: {str(e)}")
    providers["coze"] = None

# Direct initialization of MLX provider
try:
    from api.services.providers.mlx import MLXProvider
    providers["mlx"] = MLXProvider()
    logger.info("Directly initialized MLX provider")
except Exception as e:
    logger.error(f"Failed to directly initialize MLX provider: {str(e)}")
    providers["mlx"] = None

# Log which providers were successfully initialized
for provider_name, provider in providers.items():
    if provider:
        logger.info(f"Successfully initialized {provider_name} provider")
    else:
        logger.warning(f"Failed to initialize {provider_name} provider")

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static')
    
    # Configure the app
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Configure CORS
    ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:8000',
        'http://localhost:8080',
        'https://actuallyusefulai.com',
        'https://api.assisted.space'
    ]

    # Initialize CORS with proper configuration
    CORS(app, resources={
        r"/*": {
            "origins": ALLOWED_ORIGINS,
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "Accept", "Origin", "User-Agent"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "X-API-Key"],
            "max_age": 3600
        }
    })

    @app.after_request
    def add_cors_headers(response):
        """Add CORS headers to all responses."""
        origin = request.headers.get('Origin')
        
        # Apply CORS headers for allowed origins
        if origin == 'https://actuallyusefulai.com' or origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
            response.headers['Access-Control-Expose-Headers'] = 'Content-Type, X-API-Key'
            response.headers['Access-Control-Max-Age'] = '3600'
            response.headers['Vary'] = 'Origin'
        # Fallback: if header not set, set it to the Origin or '*' as default
        if 'Access-Control-Allow-Origin' not in response.headers:
            fallback_origin = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Origin'] = fallback_origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        
        # Add Content Security Policy header to force HTTPS
        response.headers['Content-Security-Policy'] = "upgrade-insecure-requests"
        
        # For streaming responses, add additional headers
        if response.mimetype == 'text/event-stream':
            response.headers.update({
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'  # Prevents Nginx from buffering
            })
            
        return response
    
    # Configure for proxies if needed
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # API Info endpoint
    @app.route(f'{API_BASE_URL}')
    def api_info():
        available_providers = {name: provider is not None for name, provider in providers.items()}
        return jsonify({
            'status': 'ok',
            'version': API_VERSION,
            'providers': available_providers,
            'endpoints': [
                f'{API_FULL_URL}/chat/{{provider}}',
                f'{API_FULL_URL}/alt/{{provider}}',
                f'{API_FULL_URL}/tools/{{provider}}',
                f'{API_FULL_URL}/models/{{provider}}',
                f'{API_FULL_URL}/docs',
                f'{API_FULL_URL}/web/duckduckgo',
                f'{API_FULL_URL}/generate',
                f'{API_FULL_URL}/tts/openai'
            ]
        })
    
    # Models endpoint - GET models from specified provider
    @app.route(f'{API_BASE_URL}/models/<provider_name>', methods=["GET", "OPTIONS"])
    def get_models(provider_name):
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["GET", "OPTIONS"]})
            return response
        
        try:
            sort_by = request.args.get("sort_by", "created")
            capability = request.args.get("capability")
            generation = request.args.get("generation")
            category = request.args.get("category")
            
            logger.info(f"Models request: provider={provider_name}, sort_by={sort_by}, capability={capability}")
            
            if capability == "none":
                capability = None
            if generation == "none":
                generation = None
            if category == "none":
                category = None
                
            provider = providers.get(provider_name)
            if not provider:
                logger.error(f"Provider {provider_name} not available")
                return jsonify({"error": f"Provider {provider_name} not available"}), 400
            
            # Prepare common parameters
            kwargs = {
                "sort_by": sort_by,
                "page": 1,
                "page_size": 1000
            }
            
            # Add provider-specific parameters
            if provider_name in ["anthropic", "mistral", "cohere", "xai", "coze"]:
                kwargs["capability_filter"] = capability
            if provider_name == "openai":
                kwargs["generation"] = generation
            if provider_name == "mistral":
                kwargs["category_filter"] = category
            
            # Call the list_models method
            models = provider.list_models(**kwargs)
            
            # Log the result
            logger.info(f"Retrieved {len(models)} models from {provider_name} API")
            if models:
                logger.info(f"First few models: {[m['id'] for m in models[:3]]}")
            
            return jsonify(models)
            
        except Exception as e:
            logger.error(f"Error in get_models: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # File Upload endpoint for Coze - POST to upload a file to the provider
    @app.route(f'{API_BASE_URL}/upload/coze', methods=["POST"])
    def upload_coze_file():
        try:
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files['file']
            if not file:
                return jsonify({"error": "Empty file"}), 400
                
            # Get file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            # Save to temporary file
            temp_dir = tempfile.gettempdir()
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=file_ext)
            try:
                logger.info(f"Saving uploaded file to {temp_file.name}")
                file.save(temp_file.name)
                temp_file.close()
                
                # Get Coze provider
                provider = providers.get("coze")
                if not provider:
                    return jsonify({"error": "Coze provider not available"}), 400
                    
                # Upload file
                file_id = provider.upload_file(temp_file.name)
                if not file_id:
                    return jsonify({"error": "Failed to upload file to Coze API"}), 500
                    
                return jsonify({
                    "success": True,
                    "file_id": file_id
                })
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return jsonify({"error": f"Error processing file: {str(e)}"}), 500
            finally:
                try:
                    os.remove(temp_file.name)
                    logger.info(f"Removed temporary file {temp_file.name}")
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temp file: {cleanup_error}")
                    
        except Exception as e:
            logger.error(f"Error in upload_coze_file: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def convert_to_bool(value):
        """Convert a value to boolean, supporting both string and boolean inputs."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == 'true'
        return bool(value)

    @app.route(f'{API_BASE_URL}/chat/<provider_name>', methods=["POST", "OPTIONS"])
    def provider_chat(provider_name):
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            origin = request.headers.get('Origin', '')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = 'https://actuallyusefulai.com'
            elif origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            response.headers['Vary'] = 'Origin'
            return response
        
        try:
            # Log request details for debugging
            logger.info(f"Chat request for provider: {provider_name}")
            logger.info(f"Request headers: {dict(request.headers)}")
            logger.info(f"Request origin: {request.headers.get('Origin', 'No origin')}")
            
            data = request.get_json()
            if not data:
                logger.error("No JSON data received in request")
                return jsonify({"error": "No data received"}), 400

            model = data.get("model")
            logger.info(f"Requested model: {model}")
            
            # Handle both prompt and messages formats
            prompt = data.get("prompt", "")
            messages = data.get("messages", [])
            
            # If messages are provided in OpenAI format, extract prompt from the last user message
            if not prompt and messages:
                # Log the incoming message format
                logger.info(f"Received messages format with {len(messages)} messages")
                
                # Extract system message if present
                system_content = next((msg.get("content", "") for msg in messages if msg.get("role") == "system"), "")
                
                # Extract the last user message as the primary prompt
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        prompt = msg.get("content", "")
                        break
                
                # If we have both system and user content, combine them
                if system_content and prompt:
                    prompt = f"System instruction: {system_content}\n\nUser message: {prompt}"
                
                logger.info(f"Extracted prompt from messages (showing first 100 chars): {prompt[:100]}...")
                
            max_tokens = data.get("max_tokens", 8096)
            stream = convert_to_bool(data.get("stream", True))
            image_path = data.get("image_path")
            use_test_image = data.get("use_test_image", False)
            
            logger.info(f"Chat request: provider={provider_name}, model={model}, stream={stream}")
            
            provider = providers.get(provider_name)
            if not provider:
                logger.error(f"Provider {provider_name} not available")
                return jsonify({"error": f"Provider {provider_name} not available"}), 400
            
            if not model:
                logger.error("Model parameter is required")
                return jsonify({"error": "Model parameter is required"}), 400
            
            # Check if stream_chat_response method exists
            if not hasattr(provider, 'stream_chat_response') or not callable(getattr(provider, 'stream_chat_response')):
                logger.error(f"Provider {provider_name} does not have stream_chat_response method")
                return jsonify({"error": f"Provider {provider_name} does not support streaming"}), 400
            
            # If streaming is requested
            if stream:
                def generate_response():
                    try:
                        result_text = ""
                        for chunk in provider.stream_chat_response(
                            prompt, 
                            model=model,
                            max_tokens=max_tokens,
                            temperature=temperature
                        ):
                            if isinstance(chunk, dict):
                                if "content" in chunk:
                                    result_text += chunk["content"]
                                yield json.dumps(chunk) + "\n"
                            else:
                                result_text += chunk
                                yield json.dumps({"type": "delta", "content": chunk}) + "\n"
                                
                        # Send a final complete message
                        yield json.dumps({
                            "type": "complete",
                            "content": result_text,
                            "model": model,
                            "provider": provider_name
                        }) + "\n"
                        
                    except Exception as e:
                        logger.error(f"Error generating tool response: {str(e)}")
                        yield json.dumps({"error": str(e)}) + "\n"
                
                # Create the Response with explicit CORS headers
                response = Response(generate_response(), mimetype="text/event-stream")
                
                # Set CORS headers explicitly
                origin = request.headers.get('Origin', '')
                response.headers.update({
                    'Access-Control-Allow-Origin': origin if origin else '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent',
                    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
                })
                
                return response
            else:
                # Non-streaming response
                try:
                    # Get the response - this returns the response object, not a generator
                    logger.info("Calling OpenAI create_response (non-streaming) with document paths: %s", document_paths)
                    response_data = provider.create_response(
                        document_paths=document_paths,
                        prompt=prompt,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=False,
                        tools=tools,
                        web_search=web_search,
                        file_search=file_search,
                        computer_use=computer_use,
                        debug_mode=debug_mode
                    )
                    
                    logger.info(f"Response data type: {type(response_data)}")
                    
                    # Check if response_data is a generator (which isn't JSON serializable)
                    if hasattr(response_data, '__iter__') and hasattr(response_data, '__next__') and not isinstance(response_data, dict):
                        # Convert generator to a response
                        logger.info("Converting generator response to dictionary")
                        try:
                            # Try to get the first value from the generator
                            first_chunk = next(response_data)
                            logger.info(f"First chunk from generator: {first_chunk}")
                            if isinstance(first_chunk, dict):
                                response_data = first_chunk
                            else:
                                response_data = {"content": str(first_chunk)}
                        except StopIteration:
                            # Generator was empty - return an error response
                            logger.error("Empty generator - no data received from OpenAI provider")
                            return jsonify({
                                "error": "No response received from OpenAI provider",
                                "status": "error"
                            }), 503
                    
                    if not response_data or not isinstance(response_data, dict):
                        logger.error(f"Invalid response data: {response_data}")
                        return jsonify({
                            "error": "Invalid response from OpenAI provider",
                            "status": "error"
                        }), 503
                    
                    # If we just have an error key, return as error
                    if 'error' in response_data and len(response_data) == 1:
                        logger.error(f"Error from OpenAI provider: {response_data['error']}")
                        return jsonify({
                            "error": response_data['error'],
                            "status": "error"
                        }), 503
                        
                    # Log the response data structure
                    logger.info(f"Response data keys: {list(response_data.keys())}")
                    
                    # Return the response as JSON
                    return jsonify(response_data)
                    
                except Exception as e:
                    logger.exception(f"Error in OpenAI Responses API call: {str(e)}")
                    return jsonify({"error": str(e), "status": "error"}), 500
                finally:
                    # Clean up temporary files
                    cleanup_temp_files(document_paths, temp_dir)
        
        except Exception as e:
            logger.error(f"Error in provider_chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Alt text generation endpoint
    @app.route(f'{API_BASE_URL}/alt/<provider_name>', methods=["POST", "OPTIONS"])
    def generate_alt_text(provider_name):
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            # Added explicit CORS headers for preflight requests
            origin = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
            return response
        
        try:
            prompt = request.form.get("prompt", "Generate descriptive alt text for this image")
            model = request.form.get("model")
            stream = convert_to_bool(request.form.get("stream", "false"))
            
            provider = providers.get(provider_name)
            if not provider:
                return jsonify({"error": f"Provider {provider_name} not available"}), 400
            
            if not model:
                return jsonify({"error": "Model parameter is required"}), 400
            
            # Process image upload
            if "image" not in request.files:
                return jsonify({"error": "No image file provided"}), 400
                
            image_file = request.files["image"]
            if not image_file.filename:
                return jsonify({"error": "Empty filename"}), 400
                
            # Get the file extension from the original filename
            file_ext = os.path.splitext(image_file.filename)[1].lower()
            if not file_ext:
                file_ext = ".png"  # Default to PNG if no extension
            
            # Save to temporary file with the original extension
            temp_dir = tempfile.gettempdir()
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=file_ext)
            try:
                logger.info(f"Saving uploaded image to {temp_file.name} with extension {file_ext}")
                image_file.save(temp_file.name)
                temp_file.close()
                
                image_path = temp_file.name
                image_data = None
                file_id = None
                
                # Process image based on provider requirements
                if provider_name == "anthropic":
                    # Anthropic uses the file path directly
                    logger.info(f"Using file path for Anthropic: {image_path}")
                elif provider_name in ["openai", "ollama", "xai", "mistral"]:
                    # For these providers, encode the image to base64
                    logger.info(f"Encoding image for {provider_name}")
                    try:
                        with open(image_path, "rb") as img_file:
                            import base64
                            image_bytes = img_file.read()
                            image_data = base64.b64encode(image_bytes).decode('utf-8')
                        logger.info(f"Successfully encoded image, length: {len(image_data)}")
                    except Exception as e:
                        logger.error(f"Failed to encode image for {provider_name}: {str(e)}")
                        return jsonify({"error": f"Failed to encode image: {str(e)}"}), 500
                elif provider_name == "coze":
                    # For Coze provider, use the specific file upload functionality
                    logger.info(f"Uploading file to Coze API")
                    file_id = provider.upload_file(image_path)
                    if not file_id:
                        return jsonify({"error": "Failed to upload file to Coze API"}), 500
                    logger.info(f"File uploaded to Coze, ID: {file_id}")
                
                if stream:
                    def stream_alt_text():
                        try:
                            # Configure provider-specific parameters
                            kwargs = {
                                "model": model,
                                "max_tokens": 8096,
                            }
                            
                            # Set the correct parameter based on provider requirements
                            if provider_name == "coze":
                                kwargs["file_id"] = file_id
                            elif provider_name in ["openai", "ollama", "xai", "mistral"] and image_data:
                                kwargs["image_data"] = image_data
                            else:
                                kwargs["image_path"] = image_path
                                
                            logger.info(f"Streaming response with kwargs: {list(kwargs.keys())}")
                            
                            for chunk in provider.stream_chat_response(prompt, **kwargs):
                                if isinstance(chunk, dict):
                                    yield json.dumps(chunk) + "\n"
                                else:
                                    yield chunk
                        except Exception as e:
                            logger.error(f"Error streaming alt text: {str(e)}")
                            yield f"Error: {str(e)}"
                        finally:
                            try:
                                os.remove(image_path)
                                logger.info(f"Removed temporary file {image_path}")
                            except Exception as cleanup_error:
                                logger.error(f"Error cleaning up temp file: {cleanup_error}")
                    
                    # Create the Response with explicit CORS headers
                    response = Response(stream_alt_text(), mimetype="text/event-stream")
                    
                    # Set CORS headers explicitly
                    origin = request.headers.get('Origin', '')
                    response.headers.update({
                        'Access-Control-Allow-Origin': origin if origin else '*',
                        'Access-Control-Allow-Credentials': 'true',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent',
                        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'X-Accel-Buffering': 'no'  # Prevents Nginx from buffering the response
                    })
                    
                    return response
                else:
                    # For non-streaming, collect all the chunks into a single response
                    try:
                        alt_text = ""
                        # Configure provider-specific parameters
                        kwargs = {
                            "model": model,
                            "max_tokens": 8096,
                        }
                        
                        # Set the correct parameter based on provider requirements
                        if provider_name == "coze":
                            kwargs["file_id"] = file_id
                        elif provider_name in ["openai", "ollama", "xai", "mistral"] and image_data:
                            kwargs["image_data"] = image_data
                        else:
                            kwargs["image_path"] = image_path
                            
                        logger.info(f"Non-streaming response with kwargs: {list(kwargs.keys())}")
                        
                        for chunk in provider.stream_chat_response(prompt, **kwargs):
                            if isinstance(chunk, dict) and "content" in chunk:
                                alt_text += chunk["content"]
                            elif isinstance(chunk, str):
                                alt_text += chunk
                        
                        return jsonify({
                            "alt_text": alt_text,
                            "model": model,
                            "provider": provider_name
                        })
                    except Exception as e:
                        logger.error(f"Error generating alt text: {str(e)}")
                        return jsonify({"error": str(e)}), 500
                    finally:
                        try:
                            os.remove(image_path)
                            logger.info(f"Removed temporary file {image_path}")
                        except Exception as cleanup_error:
                            logger.error(f"Error cleaning up temp file: {cleanup_error}")
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                return jsonify({"error": f"Error processing image: {str(e)}"}), 500
        
        except Exception as e:
            logger.error(f"Error in generate_alt_text: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Tool calling endpoint
    @app.route(f'{API_BASE_URL}/tools/<provider_name>', methods=["POST", "OPTIONS"])
    def call_tool(provider_name):
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            return response
        
        try:
            data = request.get_json()
            model = data.get("model")
            prompt = data.get("prompt", "")
            tools = data.get("tools", [])
            max_tokens = data.get("max_tokens", 8096)
            
            provider = providers.get(provider_name)
            if not provider:
                return jsonify({"error": f"Provider {provider_name} not available"}), 400
            
            if not model:
                return jsonify({"error": "Model parameter is required"}), 400
            
            # Check if the provider has a call_tool method
            if hasattr(provider, "call_tool"):
                # Use dedicated tool calling method if available
                result = provider.call_tool(
                    prompt=prompt,
                    model=model,
                    tools=tools,
                    max_tokens=max_tokens
                )
                return jsonify(result)
            else:
                # Fall back to regular chat with tools in the prompt
                # Format tools as a JSON string and append to prompt
                tools_str = json.dumps(tools, indent=2)
                enhanced_prompt = f"{prompt}\n\nAvailable tools:\n{tools_str}\n\nPlease use these tools to respond to the user's request."
                
                # Stream the response
                def generate_tool_response():
                    try:
                        result_text = ""
                        for chunk in provider.stream_chat_response(
                            enhanced_prompt, 
                            model=model,
                            max_tokens=max_tokens
                        ):
                            if isinstance(chunk, dict):
                                if "content" in chunk:
                                    result_text += chunk["content"]
                                yield json.dumps(chunk) + "\n"
                            else:
                                result_text += chunk
                                yield json.dumps({"type": "delta", "content": chunk}) + "\n"
                                
                        # Send a final complete message
                        yield json.dumps({
                            "type": "complete",
                            "content": result_text,
                            "model": model,
                            "provider": provider_name
                        }) + "\n"
                        
                    except Exception as e:
                        logger.error(f"Error generating tool response: {str(e)}")
                        yield json.dumps({"error": str(e)}) + "\n"
                
                # Create the Response with explicit CORS headers
                response = Response(generate_tool_response(), mimetype="text/event-stream")
                
                # Set CORS headers explicitly
                origin = request.headers.get('Origin', '')
                response.headers.update({
                    'Access-Control-Allow-Origin': origin if origin else '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent',
                    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
                })
                
                return response
            
        except Exception as e:
            logger.error(f"Error in call_tool: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Clear conversation history endpoint
    @app.route(f'{API_BASE_URL}/chat/<provider_name>/clear', methods=["POST", "OPTIONS"])
    def clear_chat(provider_name):
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            return response
        
        try:
            provider = providers.get(provider_name)
            if not provider:
                return jsonify({"error": f"Provider {provider_name} not available"}), 400
            
            # Original implementations simply call clear_conversation with no args
            if hasattr(provider, "clear_conversation"):
                provider.clear_conversation()
                return jsonify({"status": "success", "message": "Conversation cleared"})
            else:
                # If no clear_conversation method, create a simple success response
                logger.warning(f"Provider {provider_name} does not have clear_conversation method")
                return jsonify({"status": "warning", "message": f"Provider {provider_name} may not support conversation history"})
        
        except Exception as e:
            logger.error(f"Error in clear_chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Health check endpoint
    @app.route(f'{API_BASE_URL}/health', methods=["GET"])
    def health_check():
        return jsonify({
            'status': 'ok',
            'timestamp': time.time(),
            'providers': {name: provider is not None for name, provider in providers.items()}
        })
    
    # Test endpoint for Mistral CORS
    @app.route(f'{API_BASE_URL}/test/mistral', methods=["GET", "OPTIONS", "POST"])
    def test_mistral_cors():
        """Simple test endpoint to diagnose CORS issues with Mistral."""
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["GET", "POST", "OPTIONS"]})
        else:
            response = jsonify({
                'status': 'ok',
                'message': 'Mistral CORS test endpoint',
                'method': request.method,
                'headers': dict(request.headers),
                'origin': request.headers.get('Origin', 'No origin header')
            })
        
        # Explicitly set CORS headers
        origin = request.headers.get('Origin', '')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = '*'
        
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        response.headers['Vary'] = 'Origin'
        
        return response
    
    # Serve frontend at root
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    # Serve static files
    @app.route('/<path:path>')
    def static_files(path):
        return send_from_directory(os.path.join('static'), path)
    
    # Handle incorrect /api/chat routes (redirect to /chat)
    @app.route(f'{API_BASE_URL}/api/chat', methods=["OPTIONS", "POST"])
    def redirect_api_chat():
        logger.info(f"Redirecting /api/chat request to /chat endpoint")
        if request.method == "OPTIONS":
            # Handle OPTIONS request for CORS
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            return response
        
        # For POST requests, extract the provider from the body if possible
        try:
            data = request.get_json() or {}
            provider_name = data.get('provider', 'ollama')  # Default to ollama if not specified
            model = data.get('model')
            
            if not model and provider_name == 'ollama':
                model = 'mistral'  # Default model for Ollama
            
            # Log the redirect with provider and model information
            logger.info(f"Redirecting to /chat/{provider_name} with model {model}")
            
            # Forward to the actual provider chat endpoint
            return provider_chat(provider_name)
        except Exception as e:
            logger.error(f"Error in redirect_api_chat: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': str(error)}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({'error': 'Server error', 'message': str(error)}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request', 'message': str(error)}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized', 'message': str(error)}), 401
    
    # Register API documentation routes
    register_docs_routes(app)
    
    # Register tools routes
    app.register_blueprint(tools_bp, url_prefix=f'{API_BASE_URL}/tools')
    logger.info(f"Registered tools blueprint at {API_BASE_URL}/tools")
    
    # Register dreamwalker routes
    app.register_blueprint(dreamwalker_bp, url_prefix=f'{API_BASE_URL}/dreamwalker')
    logger.info(f"Registered dreamwalker blueprint at {API_BASE_URL}/dreamwalker")
    
    # Register web search routes
    app.register_blueprint(web_bp, url_prefix=f'{API_BASE_URL}/web')
    logger.info(f"Registered web blueprint at {API_BASE_URL}/web")
    
    # Register research search routes
    app.register_blueprint(research_bp, url_prefix=f'{API_BASE_URL}/research')
    logger.info(f"Registered research blueprint at {API_BASE_URL}/research")
    
    # Register social blueprint
    app.register_blueprint(get_social_blueprint(), url_prefix=f'{API_BASE_URL}/social')
    logger.info(f"Registered social blueprint at {API_BASE_URL}/social")
    
    # Register news blueprint
    app.register_blueprint(get_news_blueprint(), url_prefix=f'{API_BASE_URL}/news')
    logger.info(f"Registered news blueprint at {API_BASE_URL}/news")
    
    # Register chat blueprint
    app.register_blueprint(chat_bp, url_prefix=f'{API_BASE_URL}/chat')
    logger.info(f"Registered chat blueprint at {API_BASE_URL}/chat")

    # Direct routes for OpenAI Responses API
    @app.route(f'{API_BASE_URL}/responses', methods=["POST", "OPTIONS"])
    def openai_responses():
        """Handle OpenAI Responses API requests for document processing."""
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            origin = request.headers.get('Origin', '')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = 'https://actuallyusefulai.com'
            elif origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        temp_dir = None
        document_paths = []

        try:
            logger.info("OpenAI Responses API request received")
            
            # Validate API key first - support both header and form parameter
            api_key = request.headers.get('X-API-Key')
            if not api_key and request.form:
                api_key = request.form.get('api_key')
            
            logger.info(f"API Key present: {bool(api_key)}")
            
            # Initialize OpenAI provider with API key if provided
            if api_key:
                provider = OpenAIProvider(api_key=api_key)
                logger.info("Initialized OpenAI provider with provided API key")
            else:
                # Get the global provider instance
                provider = providers.get("openai")
                logger.info("Using global OpenAI provider instance")
                
            if not provider:
                logger.error("OpenAI provider not available")
                return jsonify({"error": "OpenAI provider not available"}), 503
                
            # Initialize mimetypes if not already done
            if not mimetypes.inited:
                mimetypes.init()
                
            # Check for files (optional)
            files = request.files.getlist('file')
            logger.info(f"Received {len(files)} files")
            
            if files and any(file.filename for file in files):
                # Create temporary directory to store uploaded files
                temp_dir = tempfile.mkdtemp(prefix="openai_responses_")
                logger.info(f"Created temporary directory: {temp_dir}")
                
                # Save uploaded files to temporary directory
                for file in files:
                    if file.filename:
                        file_path = os.path.join(temp_dir, file.filename)
                        file.save(file_path)
                        document_paths.append(file_path)
                        
                        # Log file type information
                        mime_type, _ = mimetypes.guess_type(file_path)
                        if mime_type:
                            logger.info(f"Saved uploaded file: {file_path} (type: {mime_type})")
                        else:
                            logger.info(f"Saved uploaded file: {file_path} (unknown type)")
            
            # Get parameters from form data or JSON
            if request.is_json:
                data = request.json
            else:
                data = request.form.to_dict()
                
            prompt = data.get('prompt', '')
            model = data.get('model', 'gpt-4o')
            max_tokens = int(data.get('max_tokens', 4096))
            temperature = float(data.get('temperature', 0.7))
            stream_mode = convert_to_bool(data.get('stream', 'false'))
            web_search = convert_to_bool(data.get('web_search', 'false'))
            file_search = convert_to_bool(data.get('file_search', 'false'))
            computer_use = convert_to_bool(data.get('computer_use', 'false'))
            
            # Get tools from request data
            tools = data.get('tools')
            if isinstance(tools, str):
                try:
                    tools = json.loads(tools)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing tools JSON: {e}")
                    return jsonify({"error": f"Invalid tools JSON: {str(e)}"}), 400
            
            # Check for debug mode flag
            debug_mode = convert_to_bool(data.get('debug_mode', 'false'))
            if debug_mode:
                logger.info("DEBUG MODE ENABLED - Bypassing actual API call")
                
                # Create a simple debug response for testing
                if stream_mode:
                    def generate_debug_response():
                        try:
                            yield json.dumps({"type": "start", "content": ""}) + "\n"
                            
                            # Create debug info about received parameters
                            debug_info = (
                                f"DEBUG INFO:\n\n"
                                f"- Prompt: {prompt}\n"
                                f"- Model: {model}\n"
                                f"- Documents: {len(document_paths)}\n"
                                f"- Web search: {web_search}\n"
                                f"- File search: {file_search}\n"
                                f"- Computer use: {computer_use}\n"
                                f"- Tools: {tools}\n"
                            )
                            
                            # Send initial status
                            yield json.dumps({"type": "status", "status": "processing"}) + "\n"
                            yield json.dumps({"type": "delta", "content": debug_info}) + "\n"
                            
                            # Simulate processing delay
                            time.sleep(1)
                            
                            # Send content in chunks
                            for chunk in "This is a debug mode response. Your parameters were successfully received, but we're bypassing the actual API call for testing.".split():
                                yield json.dumps({"type": "delta", "content": chunk + " "}) + "\n"
                                time.sleep(0.1)
                            
                            # Final status update
                            yield json.dumps({"type": "status", "status": "completed"}) + "\n"
                            
                        except Exception as e:
                            logger.error(f"Error generating debug response: {str(e)}")
                            yield json.dumps({"error": str(e)}) + "\n"
                        
                        finally:
                            # Clean up temporary files
                            cleanup_temp_files(document_paths, temp_dir)
                    
                    # Return streaming response
                    response = Response(
                        stream_with_context(generate_debug_response()),
                        content_type='text/event-stream',
                        headers={
                            'Cache-Control': 'no-cache',
                            'Connection': 'keep-alive',
                            'X-Accel-Buffering': 'no'
                        }
                    )
                    
                    # Set CORS headers explicitly
                    origin = request.headers.get('Origin', '')
                    response.headers.update({
                        'Access-Control-Allow-Origin': origin if origin else '*',
                        'Access-Control-Allow-Credentials': 'true',
                        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent',
                        'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
                    })
                    
                    return response
                else:
                    # Create a mock response_id
                    mock_response_id = f"debug_mock_{int(time.time())}"
                    
                    # Create debug info
                    debug_info = (
                        f"DEBUG INFO:\n\n"
                        f"- Prompt: {prompt}\n"
                        f"- Model: {model}\n"
                        f"- Documents: {len(document_paths)}\n"
                        f"- Web search: {web_search}\n"
                        f"- File search: {file_search}\n"
                        f"- Computer use: {computer_use}\n"
                        f"- Tools: {tools}\n"
                    )
                    
                    # Clean up temporary files
                    cleanup_temp_files(document_paths, temp_dir)
                    
                    # Return debug response
                    return jsonify({
                        "status": "completed",
                        "response_id": mock_response_id,
                        "model": model,
                        "content": f"{debug_info}\n\nThis is a debug mode response. Your parameters were successfully received, but we're bypassing the actual API call for testing.",
                        "usage": {
                            "prompt_tokens": 100,
                            "completion_tokens": 50,
                            "total_tokens": 150
                        }
                    })
            
            logger.info(f"OpenAI Responses request: model={model}, documents={len(document_paths)}, stream={stream_mode}")
            logger.info(f"Tools enabled: web_search={web_search}, file_search={file_search}, computer_use={computer_use}")
            
            if tools:
                logger.info(f"Custom tools provided: {tools}")
            
            # Validate required parameters explicitly
            if not prompt:
                logger.error("No prompt provided")
                return jsonify({"error": "Prompt parameter is required."}), 400
            
            # Handle streaming response
            if stream_mode:
                def generate_response():
                    try:
                        result_text = ""
                        for chunk in provider.stream_chat_response(
                            prompt, 
                            model=model,
                            max_tokens=max_tokens,
                            temperature=temperature
                        ):
                            if isinstance(chunk, dict):
                                if "content" in chunk:
                                    result_text += chunk["content"]
                                yield json.dumps(chunk) + "\n"
                            else:
                                result_text += chunk
                                yield json.dumps({"type": "delta", "content": chunk}) + "\n"
                                
                        # Send a final complete message
                        yield json.dumps({
                            "type": "complete",
                            "content": result_text,
                            "model": model,
                            "provider": provider_name
                        }) + "\n"
                        
                    except Exception as e:
                        logger.error(f"Error generating tool response: {str(e)}")
                        yield json.dumps({"error": str(e)}) + "\n"
                
                # Create the Response with explicit CORS headers
                response = Response(generate_response(), mimetype="text/event-stream")
                
                # Set CORS headers explicitly
                origin = request.headers.get('Origin', '')
                response.headers.update({
                    'Access-Control-Allow-Origin': origin if origin else '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent',
                    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
                })
                
                return response
            else:
                # Non-streaming response
                try:
                    # Get the response - this returns the response object, not a generator
                    logger.info("Calling OpenAI create_response (non-streaming) with document paths: %s", document_paths)
                    response_data = provider.create_response(
                        document_paths=document_paths,
                        prompt=prompt,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=False,
                        tools=tools,
                        web_search=web_search,
                        file_search=file_search,
                        computer_use=computer_use,
                        debug_mode=debug_mode
                    )
                    
                    logger.info(f"Response data type: {type(response_data)}")
                    
                    # Check if response_data is a generator (which isn't JSON serializable)
                    if hasattr(response_data, '__iter__') and hasattr(response_data, '__next__') and not isinstance(response_data, dict):
                        # Convert generator to a response
                        logger.info("Converting generator response to dictionary")
                        try:
                            # Try to get the first value from the generator
                            first_chunk = next(response_data)
                            logger.info(f"First chunk from generator: {first_chunk}")
                            if isinstance(first_chunk, dict):
                                response_data = first_chunk
                            else:
                                response_data = {"content": str(first_chunk)}
                        except StopIteration:
                            # Generator was empty - return an error response
                            logger.error("Empty generator - no data received from OpenAI provider")
                            return jsonify({
                                "error": "No response received from OpenAI provider",
                                "status": "error"
                            }), 503
                    
                    if not response_data or not isinstance(response_data, dict):
                        logger.error(f"Invalid response data: {response_data}")
                        return jsonify({
                            "error": "Invalid response from OpenAI provider",
                            "status": "error"
                        }), 503
                    
                    # If we just have an error key, return as error
                    if 'error' in response_data and len(response_data) == 1:
                        logger.error(f"Error from OpenAI provider: {response_data['error']}")
                        return jsonify({
                            "error": response_data['error'],
                            "status": "error"
                        }), 503
                        
                    # Log the response data structure
                    logger.info(f"Response data keys: {list(response_data.keys())}")
                    
                    # Return the response as JSON
                    return jsonify(response_data)
                    
                except Exception as e:
                    logger.exception(f"Error in OpenAI Responses API call: {str(e)}")
                    return jsonify({"error": str(e), "status": "error"}), 500
                finally:
                    # Clean up temporary files
                    cleanup_temp_files(document_paths, temp_dir)
        
        except Exception as e:
            logger.exception(f"Error in OpenAI Responses route: {str(e)}")
            
            # Clean up temporary files if exception occurs
            cleanup_temp_files(document_paths, temp_dir)
            
            return jsonify({"error": str(e), "status": "error"}), 500

    def cleanup_temp_files(document_paths, temp_dir):
        """Helper function to clean up temporary files and directory."""
        if document_paths:
            for doc_path in document_paths:
                try:
                    if os.path.exists(doc_path):
                        os.remove(doc_path)
                        logger.debug(f"Removed temporary file: {doc_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {doc_path}: {e}")
            
            if temp_dir:
                try:
                    if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                        os.rmdir(temp_dir)
                        logger.debug(f"Removed temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")

    @app.route(f'{API_BASE_URL}/responses/<response_id>', methods=["GET", "OPTIONS"])
    def retrieve_openai_response(response_id):
        """Retrieve a previously created OpenAI response."""
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["GET", "OPTIONS"]})
            origin = request.headers.get('Origin', '')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = 'https://actuallyusefulai.com'
            elif origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        try:
            provider = providers.get("openai")
            if not provider:
                logger.error("OpenAI provider not available")
                return jsonify({"error": "OpenAI provider not available"}), 503
            
            # Check if this is a UUID format (generated ID from our system)
            try:
                uuid_obj = uuid.UUID(response_id)
                is_generated_id = True
                logger.info(f"Detected generated UUID response_id: {response_id}")
            except ValueError:
                is_generated_id = False
                logger.info(f"Using native OpenAI response_id: {response_id}")
            
            # If it's a generated ID, we don't actually have a response to retrieve
            # so we return a mock response
            if is_generated_id:
                    return jsonify({
                    "status": "processing",
                    "response_id": response_id,
                    "message": "This response was not created via the OpenAI Responses API directly. The content may not be available."
                })
            
            # Otherwise, try to retrieve the actual response
            try:
                response_data = provider.retrieve_response(response_id)
                
                # Create response with explicit CORS headers
                response = jsonify(response_data)
                origin = request.headers.get('Origin', '')
                response.headers.update({
                    'Access-Control-Allow-Origin': origin if origin else '*',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent',
                    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
                })
                
                return response
            except Exception as e:
                error_msg = f"Error retrieving OpenAI response: {str(e)}"
                logger.error(error_msg)
                return jsonify({"error": error_msg}), 500
                
        except Exception as e:
            logger.error(f"Error retrieving OpenAI response: {str(e)}")
            return jsonify({"error": f"Error retrieving OpenAI response: {str(e)}"}), 500
            
    logger.info(f"Registered direct routes for OpenAI Responses API at {API_BASE_URL}/responses")
    
    # Direct routes for image generation across all providers
    @app.route(f'{API_BASE_URL}/generate', methods=["POST", "OPTIONS"])
    def generate_image():
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            return response
        
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400
            
            # Extract provider from data (default to openai as most stable)
            provider_name = data.get("provider")
            
            # If provider_name is not specified or is not a string, default to "openai"
            if not provider_name or not isinstance(provider_name, str):
                provider_name = "openai"
            else:
                provider_name = provider_name.lower()
            
            # Validate provider
            if provider_name not in ["openai", "gemini", "xai"]:
                return jsonify({
                    "error": f"Invalid provider: {provider_name}. Supported providers are: openai, gemini, xai"
                }), 400
            
            # Redirect to the appropriate provider endpoint
            if provider_name == "openai":
                return generate_image_openai()
            elif provider_name == "xai":
                return generate_image_xai()
            elif provider_name == "gemini":
                return generate_image_gemini()
            
        except Exception as e:
            logger.error(f"Error in generate_image: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route(f'{API_BASE_URL}/generate/gemini', methods=["POST", "OPTIONS"])
    def generate_image_gemini():
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            return response
        
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400
            
            # Extract parameters
            prompt = data.get("prompt")
            if not prompt:
                return jsonify({"error": "Prompt is required"}), 400
                
            model = data.get("model", "gemini-2.0-flash-exp-image-generation")
            n = int(data.get("n", 1))
            size = data.get("size", "1024x1024")
            quality = data.get("quality", "standard")
            style = data.get("style", "vivid")
            response_format = data.get("response_format", "url")
            
            # Try to get or create a Gemini provider
            provider = providers.get("gemini")
            if not provider:
                # Try importing Google Generative AI
                try:
                    import google.generativeai as genai
                    from api.services.providers.gemini import GeminiProvider
                    
                    # Get API key from request or config
                    api_key = data.get("api_key") or os.getenv("GOOGLE_API_KEY")
                    if not api_key:
                        return jsonify({"error": "Google API key not found. Please provide it in the request or set the GOOGLE_API_KEY environment variable."}), 400
                    
                    # Create provider with API key
                    provider = GeminiProvider(api_key=api_key)
                    providers["gemini"] = provider
                    logger.info("Created Gemini provider on-demand")
                except ImportError:
                    return jsonify({"error": "Google Generative AI library not installed. Please install with: pip install google-generativeai"}), 400
                except Exception as e:
                    logger.error(f"Error creating Gemini provider: {str(e)}")
                    return jsonify({"error": f"Failed to create Gemini provider: {str(e)}"}), 500
            
            # If API key is provided in request, pass it to the generate_image method
            api_key = data.get("api_key")
            additional_params = {}
            if api_key:
                additional_params["api_key"] = api_key
            
            # Generate image
            response = provider.generate_image(
                prompt=prompt,
                model=model,
                n=n,
                size=size,
                quality=quality,
                style=style,
                response_format=response_format,
                **additional_params
            )
            
            if "error" in response:
                logger.error(f"Error generating image with Gemini: {response['error']}")
                return jsonify({"error": response["error"]}), 400
                
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error generating image with Gemini: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route(f'{API_BASE_URL}/generate/openai', methods=["POST", "OPTIONS"])
    def generate_image_openai():
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            return response
        
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400
            
            # Extract parameters
            prompt = data.get("prompt")
            if not prompt:
                return jsonify({"error": "Prompt is required"}), 400
                
            model = data.get("model", "dall-e-3")
            n = int(data.get("n", 1))
            size = data.get("size", "1024x1024")
            quality = data.get("quality", "standard")
            style = data.get("style", "vivid")
            response_format = data.get("response_format", "url")
            
            # Try to get or create an OpenAI provider
            provider = providers.get("openai")
            if not provider:
                # Try importing OpenAI
                try:
                    from openai import OpenAI
                    from api.services.providers.openai import OpenAIProvider
                    
                    # Get API key from request or config
                    api_key = data.get("api_key") or os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        return jsonify({"error": "OpenAI API key not found"}), 400
                    
                    # Create provider with API key
                    provider = OpenAIProvider(api_key=api_key)
                    providers["openai"] = provider
                    logger.info("Created OpenAI provider on-demand")
                except ImportError:
                    return jsonify({"error": "OpenAI library not installed. Please install with: pip install openai"}), 400
                except Exception as e:
                    logger.error(f"Error creating OpenAI provider: {str(e)}")
                    return jsonify({"error": f"Failed to create OpenAI provider: {str(e)}"}), 500
            
            # Generate image
            # If API key is provided in request, pass it to the generate_image method
            api_key = data.get("api_key")
            kwargs = {}
            if api_key:
                kwargs["api_key"] = api_key
                
            response = provider.generate_image(
                prompt=prompt,
                model=model,
                n=n,
                size=size,
                quality=quality,
                style=style,
                response_format=response_format,
                **kwargs
            )
            
            if "error" in response:
                logger.error(f"Error generating image with OpenAI: {response['error']}")
                return jsonify({"error": response["error"]}), 400
                
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error generating image with OpenAI: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route(f'{API_BASE_URL}/generate/xai', methods=["POST", "OPTIONS"])
    def generate_image_xai():
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            return response
        
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data received"}), 400
            
            # Extract parameters
            prompt = data.get("prompt")
            if not prompt:
                return jsonify({"error": "Prompt is required"}), 400
                
            model = data.get("model", "grok-2-image")
            n = int(data.get("n", 1))
            size = data.get("size", "1024x1024")
            style = data.get("style", "vivid")
            response_format = data.get("response_format", "url")
            
            # Try to get or create an X.AI provider
            provider = providers.get("xai")
            if not provider:
                # Try importing OpenAI (used by X.AI provider)
                try:
                    from openai import OpenAI
                    from api.services.providers.xai import XAIProvider
                    
                    # Get API key from request or config
                    api_key = data.get("api_key") or os.getenv("XAI_API_KEY")
                    if not api_key:
                        return jsonify({"error": "X.AI API key not found"}), 400
                    
                    # Create provider with API key
                    provider = XAIProvider(api_key=api_key)
                    providers["xai"] = provider
                    logger.info("Created X.AI provider on-demand")
                except ImportError:
                    return jsonify({"error": "OpenAI library not installed. Please install with: pip install openai"}), 400
                except Exception as e:
                    logger.error(f"Error creating X.AI provider: {str(e)}")
                    return jsonify({"error": f"Failed to create X.AI provider: {str(e)}"}), 500
            
            # xAI-specific parameters
            additional_params = {}
            
            # Add seed if provided
            if "seed" in data:
                try:
                    additional_params["seed"] = int(data["seed"])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid seed value: {data['seed']}. Ignoring.")
            
            # Add HDR flag if provided
            if "hdr" in data:
                additional_params["hdr"] = bool(data["hdr"])
            
            # If API key is provided in request, pass it to the generate_image method
            api_key = data.get("api_key")
            if api_key:
                additional_params["api_key"] = api_key
            
            # Generate image
            response = provider.generate_image(
                prompt=prompt,
                model=model,
                n=n,
                response_format=response_format,
                **additional_params
            )
            
            if "error" in response:
                logger.error(f"Error generating image with xAI: {response['error']}")
                return jsonify({"error": response["error"]}), 400
                
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error generating image with xAI: {str(e)}")
            return jsonify({"error": str(e)}), 500

    # Text-to-speech endpoint
    @app.route(f'{API_BASE_URL}/tts/openai', methods=["POST", "OPTIONS"])
    def text_to_speech():
        """Generate speech from text using OpenAI's text-to-speech models."""
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            origin = request.headers.get('Origin', '')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = 'https://actuallyusefulai.com'
            elif origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        try:
            provider = providers.get("openai")
            if not provider:
                return jsonify({"error": "OpenAI provider not available"}), 400
            
            data = request.get_json() or {}
            text = data.get("text")
            model = data.get("model", "tts-1")
            voice = data.get("voice", "alloy")
            speed = float(data.get("speed", 1.0))
            
            if not text:
                return jsonify({"error": "Text is required"}), 400
            
            # Validate speed range
            if not 0.25 <= speed <= 4.0:
                return jsonify({"error": "Speed must be between 0.25 and 4.0"}), 400
            
            # Generate speech
            audio_data = provider.create_speech(
                text=text,
                model=model,
                voice=voice,
                speed=speed
            )
            
            if audio_data is None:
                return jsonify({"error": "Failed to generate speech"}), 500
            
            # Create a temporary file to store the audio
            temp_dir = tempfile.gettempdir()
            temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix='.mp3')
            temp_file.write(audio_data)
            temp_file.close()
            
            # Send the audio file
            return send_from_directory(
                temp_dir,
                os.path.basename(temp_file.name),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='speech.mp3'
            )
            
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route(f'{API_BASE_URL}/images/edit', methods=["POST", "OPTIONS"])
    def edit_image():
        """Edit an existing image using OpenAI's DALL-E models."""
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            origin = request.headers.get('Origin', '')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = 'https://actuallyusefulai.com'
            elif origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        try:
            provider = providers.get("openai")
            if not provider:
                logger.error("OpenAI provider not available")
                return jsonify({"error": "OpenAI provider not available"}), 503
            
            # Check for image file
            if 'image' not in request.files:
                return jsonify({"error": "No image file provided"}), 400
                
            image_file = request.files['image']
            if not image_file.filename:
                return jsonify({"error": "Empty filename"}), 400
            
            # Get mask file if provided
            mask_file = None
            mask_path = None
            if 'mask' in request.files:
                mask_file = request.files['mask']
                if mask_file.filename:
                    # Save mask to temporary file
                    mask_temp = tempfile.NamedTemporaryFile(suffix=os.path.splitext(mask_file.filename)[1], delete=False)
                    mask_file.save(mask_temp.name)
                    mask_temp.close()
                    mask_path = mask_temp.name
                    logger.info(f"Saved mask file to {mask_path}")
            
            # Check for prompt
            prompt = request.form.get('prompt')
            if not prompt:
                return jsonify({"error": "Prompt is required"}), 400
                
            # Get other parameters
            model = request.form.get('model', 'dall-e-2')
            n = int(request.form.get('n', 1))
            size = request.form.get('size', '1024x1024')
            response_format = request.form.get('response_format', 'url')
            
            # Save image to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(image_file.filename)[1], delete=False)
            image_file.save(temp_file.name)
            temp_file.close()
            image_path = temp_file.name
            logger.info(f"Saved image file to {image_path}")
            
            try:
                # Call provider's edit_image method
                result = provider.edit_image(
                    image_path=image_path,
                    prompt=prompt,
                    mask_path=mask_path,
                    model=model,
                    n=n,
                    size=size,
                    response_format=response_format
                )
                
                # Check for errors
                if "error" in result:
                    logger.error(f"Error editing image: {result['error']}")
                    return jsonify({"error": result["error"]}), 500
                
                return jsonify(result)
                
            finally:
                # Clean up temporary files
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.debug(f"Removed temporary file: {image_path}")
                    if mask_path and os.path.exists(mask_path):
                        os.remove(mask_path)
                        logger.debug(f"Removed temporary file: {mask_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary files: {e}")
                    
        except Exception as e:
            logger.error(f"Error in edit_image: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route(f'{API_BASE_URL}/images/variations', methods=["POST", "OPTIONS"])
    def create_image_variations():
        """Create variations of an existing image using OpenAI's DALL-E models."""
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            origin = request.headers.get('Origin', '')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = 'https://actuallyusefulai.com'
            elif origin:
                response.headers['Access-Control-Allow-Origin'] = origin
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-API-Key,Accept,Origin,User-Agent'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        try:
            provider = providers.get("openai")
            if not provider:
                logger.error("OpenAI provider not available")
                return jsonify({"error": "OpenAI provider not available"}), 503
            
            # Check for image file
            if 'image' not in request.files:
                return jsonify({"error": "No image file provided"}), 400
                
            image_file = request.files['image']
            if not image_file.filename:
                return jsonify({"error": "Empty filename"}), 400
            
            # Get other parameters
            model = request.form.get('model', 'dall-e-2')
            n = int(request.form.get('n', 1))
            size = request.form.get('size', '1024x1024')
            response_format = request.form.get('response_format', 'url')
            
            # Save image to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(image_file.filename)[1], delete=False)
            image_file.save(temp_file.name)
            temp_file.close()
            image_path = temp_file.name
            logger.info(f"Saved image file to {image_path}")
            
            try:
                # Call provider's create_image_variation method
                result = provider.create_image_variation(
                    image_path=image_path,
                    model=model,
                    n=n,
                    size=size,
                    response_format=response_format
                )
                
                # Check for errors
                if "error" in result:
                    logger.error(f"Error creating image variations: {result['error']}")
                    return jsonify({"error": result["error"]}), 500
                
                return jsonify(result)
                
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        logger.debug(f"Removed temporary file: {image_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file: {e}")
                
        except Exception as e:
            logger.error(f"Error in create_image_variations: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    logger.info(f"Registered direct routes for OpenAI Images API at {API_BASE_URL}/images")
    
    # New default alt text generation endpoint to handle requests without a provider in the URL
    @app.route(f'{API_BASE_URL}/alt', methods=["POST", "OPTIONS"])
    def generate_alt_text_default():
        # Handle OPTIONS request for CORS preflight
        if request.method == "OPTIONS":
            response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
            origin = request.headers.get('Origin', '*')
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
            return response
        
        # Check if we're receiving form data or JSON
        if request.content_type and 'application/json' in request.content_type:
            # For JSON requests
            try:
                data = request.get_json()
                provider_name = data.get("provider", "openai")
                logger.info(f"Using provider from JSON data: {provider_name}")
            except Exception as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                provider_name = "openai"
        else:
            # For form data requests
            provider_name = request.form.get("provider", "openai")
            logger.info(f"Using provider from form data: {provider_name}")
            
        return generate_alt_text(provider_name)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=API_HOST,
        port=API_PORT,
        debug=API_DEBUG
    ) 