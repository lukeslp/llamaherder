#!/usr/bin/env python
from flask import Blueprint, request, jsonify, Response, stream_with_context, current_app
import logging
import json
import os
import tempfile
from typing import Dict, Any, Generator, Optional
from werkzeug.utils import secure_filename

from api.services.provider_factory import ProviderFactory
from api.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from api.utils.errors import InvalidRequestError, ProviderNotAvailableError

# Logger for this module
logger = logging.getLogger(__name__)

# Blueprint for alt text routes
alt_bp = Blueprint('alt', __name__)


def format_chunk(chunk: Any, is_error: bool = False) -> str:
    """Format a response chunk for consistent streaming."""
    if is_error:
        return json.dumps({"error": str(chunk)}) + "\n"
    
    if isinstance(chunk, dict):
        # Make sure each chunk ends with a newline to ensure proper separation
        return json.dumps(chunk) + "\n"
    
    if isinstance(chunk, str):
        # For string chunks, wrap them in a delta format for consistency
        return json.dumps({"type": "delta", "content": chunk}) + "\n"
    
    # Fallback for unknown types
    return json.dumps({"type": "delta", "content": str(chunk)}) + "\n"


def allowed_file(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_uploaded_image(provider_name: str, file) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Process an uploaded image file based on provider requirements.
    
    Args:
        provider_name: Name of the provider
        file: The uploaded file object
        
    Returns:
        Tuple of (image_path, image_data, file_id)
    """
    if not file or not allowed_file(file.filename):
        return None, None, None
    
    # Create a temporary file
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
    file.save(temp_file.name)
    temp_file.close()
    
    image_path = None
    image_data = None
    file_id = None
    
    try:
        # Get provider instance
        provider = ProviderFactory.get_provider(provider_name)
        if not provider:
            raise ProviderNotAvailableError(f"Provider '{provider_name}' not available")
        
        if provider_name == "anthropic":
            # For Anthropic, we need to keep the file path
            image_path = temp_file.name
            logger.info(f"Using file path for Anthropic: {image_path}")
        elif provider_name in ["openai", "ollama", "xai", "mistral"]:
            # For these providers, we need to encode the image to base64
            logger.info(f"Encoding image for {provider_name}")
            image_data = provider.encode_image(temp_file.name)
            if not image_data:
                raise Exception(f"Failed to encode image for {provider_name}")
            logger.info(f"Successfully encoded image, length: {len(image_data)}")
        elif provider_name == "coze":
            # For Coze, we need to upload the file and get a file ID
            logger.info(f"Uploading file to Coze")
            file_id = provider.upload_file(temp_file.name)
            if not file_id:
                raise Exception("Failed to upload file to Coze")
            logger.info(f"File uploaded to Coze, ID: {file_id}")
        
        return image_path, image_data, file_id
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        
        # Clean up temporary file if not needed
        if provider_name != "anthropic" and os.path.exists(temp_file.name):
            try:
                os.remove(temp_file.name)
            except Exception as cleanup_error:
                logger.error(f"Error cleaning up temporary file: {cleanup_error}")
        
        raise


def convert_to_bool(value):
    """Convert a value to boolean, supporting both string and boolean inputs."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)


@alt_bp.route('/generate', methods=['POST'])
def generate_alt_text():
    """Generate alt text for an image."""
    # Check if an image was uploaded
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image_file = request.files['image']
    if not image_file.filename:
        return jsonify({"error": "No image selected"}), 400
    
    if not allowed_file(image_file.filename):
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Get request parameters
    provider_name = request.form.get('provider', 'anthropic')
    model = request.form.get('model')
    prompt = request.form.get('prompt', 'Generate descriptive alt text for the visually impaired for social media')
    stream = convert_to_bool(request.form.get('stream', 'true'))
    
    # Get provider instance
    provider = ProviderFactory.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Provider '{provider_name}' not available"}), 400
    
    if not model:
        return jsonify({"error": "Model parameter is required"}), 400
    
    # Process the uploaded image
    try:
        image_path, image_data, file_id = process_uploaded_image(provider_name, image_file)
    except Exception as e:
        return jsonify({"error": f"Error processing image: {str(e)}"}), 500
    
    logger.info(f"Alt text request: provider={provider_name}, model={model}, stream={stream}")
    
    def generate_response() -> Generator[str, None, None]:
        """Generate streaming response from the provider."""
        try:
            # Start event
            yield format_chunk({"type": "start", "content": ""})
            
            # Stream chat response from provider with the image
            kwargs = {}
            if image_path:
                kwargs['image_path'] = image_path
            if image_data:
                kwargs['image_data'] = image_data
            if file_id:
                kwargs['file_id'] = file_id
                
            logger.info(f"Streaming response with kwargs: {kwargs.keys()}")
            
            for chunk in provider.stream_chat_response(
                prompt=prompt,
                model=model,
                **kwargs
            ):
                yield format_chunk(chunk)
                
            # Complete event
            yield format_chunk({"type": "complete"})
            
        except Exception as e:
            logger.error(f"Error generating alt text: {str(e)}")
            yield format_chunk(str(e), is_error=True)
        finally:
            # Clean up temporary file if it was an Anthropic request
            if provider_name == "anthropic" and image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {cleanup_error}")
    
    # If streaming is disabled, collect all chunks and return as a single response
    if not stream:
        try:
            full_response = ""
            kwargs = {}
            if image_path:
                kwargs['image_path'] = image_path
            if image_data:
                kwargs['image_data'] = image_data
            if file_id:
                kwargs['file_id'] = file_id
                
            for chunk in provider.stream_chat_response(
                prompt=prompt,
                model=model,
                **kwargs
            ):
                if isinstance(chunk, dict) and "content" in chunk:
                    full_response += chunk["content"]
                elif isinstance(chunk, str):
                    full_response += chunk
            
            # Clean up temporary file if it was an Anthropic request
            if provider_name == "anthropic" and image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {cleanup_error}")
            
            return jsonify({
                "alt_text": full_response,
                "model": model,
                "provider": provider_name
            })
        except Exception as e:
            logger.error(f"Error generating non-streaming alt text: {str(e)}")
            
            # Clean up temporary file if it was an Anthropic request
            if provider_name == "anthropic" and image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up temporary file: {cleanup_error}")
                    
            return jsonify({"error": str(e)}), 500
    
    # Return streaming response
    return Response(
        stream_with_context(generate_response()),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    ) 

@alt_bp.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"  # Or specify the allowed domain, e.g., 'https://actuallyusefulai.com'
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, Accept, Authorization"
    return response