#!/usr/bin/env python
from flask import Blueprint, request, jsonify, Response, stream_with_context
import logging
import json
import os
import tempfile
import mimetypes
from typing import Dict, Any, Generator, List

from api.services.provider_factory import ProviderFactory
from api.utils.errors import InvalidRequestError, ProviderNotAvailableError

# Logger for this module
logger = logging.getLogger(__name__)

# Blueprint for chat routes
chat_bp = Blueprint('chat', __name__)


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


def convert_to_bool(value):
    """Convert a value to boolean, supporting both string and boolean inputs."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == 'true'
    return bool(value)


@chat_bp.route('/stream', methods=['POST'])
def stream_chat():
    """Stream a chat response from an AI provider."""
    data = request.json or {}
    
    # Get required parameters
    provider_name = data.get('provider', 'anthropic')
    model = data.get('model')
    prompt = data.get('prompt', 'How can I help you today?')
    max_tokens = data.get('max_tokens', -1)
    
    # Enforce max_tokens limit for Anthropic
    if provider_name == 'anthropic' and max_tokens > 4096:
        logger.warning(f"Requested max_tokens ({max_tokens}) exceeds limit. Capping at 4096.")
        max_tokens = 4096
    
    # Get provider instance
    provider = ProviderFactory.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Provider '{provider_name}' not available"}), 400
    
    if not model:
        return jsonify({"error": "Model parameter is required"}), 400
    
    # Optional parameters
    stream = convert_to_bool(data.get('stream', True))
    
    # Get conversation parameters
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id', 'default_user')
    
    logger.info(f"Chat request: provider={provider_name}, model={model}, stream={stream}, max_tokens={max_tokens}")
    
    def generate_response() -> Generator[str, None, None]:
        """Generate streaming response from the provider."""
        try:
            # Start event
            yield format_chunk({"type": "start", "content": ""})
            
            # Stream chat response from provider
            for chunk in provider.stream_chat_response(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                conversation_id=conversation_id,
                user_id=user_id
            ):
                yield format_chunk(chunk)
                
            # Complete event
            yield format_chunk({"type": "complete", "tokens": max_tokens})
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            yield format_chunk(str(e), is_error=True)
    
    # If streaming is disabled, collect all chunks and return as a single response
    if not stream:
        try:
            full_response = ""
            for chunk in provider.stream_chat_response(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                conversation_id=conversation_id,
                user_id=user_id
            ):
                if isinstance(chunk, dict) and "content" in chunk:
                    full_response += chunk["content"]
                elif isinstance(chunk, str):
                    full_response += chunk
            
            return jsonify({
                "content": full_response,
                "model": model,
                "provider": provider_name
            })
        except Exception as e:
            logger.error(f"Error generating non-streaming response: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Return streaming response
    response = Response(
        stream_with_context(generate_response()),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )

    # Explicitly set CORS headers for streaming response
    origin = request.headers.get('Origin')
    if origin == 'https://actuallyusefulai.com':
        response.headers['Access-Control-Allow-Origin'] = origin 
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, X-API-Key'
        
    return response


@chat_bp.route('/stream', methods=['OPTIONS'])
def stream_chat_options():
    """Handle OPTIONS request for CORS preflight."""
    response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
    
    # Set CORS headers
    origin = request.headers.get('Origin')
    if origin == 'https://actuallyusefulai.com':
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Type, X-API-Key'
    
    return response


@chat_bp.route('/completions', methods=['POST'])
def chat_completions():
    """Non-streaming chat completions endpoint."""
    # Simply delegate to stream_chat with stream=False
    request.json = request.json or {}
    request.json['stream'] = False
    return stream_chat()


@chat_bp.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a provider."""
    data = request.json or {}
    provider_name = data.get('provider', 'anthropic')
    
    # Get provider instance
    provider = ProviderFactory.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Provider '{provider_name}' not available"}), 400
    
    try:
        provider.clear_conversation()
        return jsonify({"status": "success", "message": "Conversation cleared"})
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/models', methods=['GET'])
def list_models():
    """List available models for a provider."""
    provider_name = request.args.get('provider', 'anthropic')
    
    # Get provider instance
    provider = ProviderFactory.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Provider '{provider_name}' not available"}), 400
    
    try:
        models = provider.list_models()
        return jsonify({"models": models, "provider": provider_name})
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/mlx', methods=['POST', 'OPTIONS'])
def mlx_chat():
    """Handle MLX chat requests."""
    # Handle OPTIONS request for CORS preflight
    if request.method == "OPTIONS":
        response = jsonify({"allowed_methods": ["POST", "OPTIONS"]})
        return response
        
    try:
        # Get the MLX provider
        provider = ProviderFactory.get_provider("mlx")
        if not provider:
            logger.error("MLX provider not available")
            return jsonify({"error": "MLX provider not available"}), 503

        # Get request data
        data = request.get_json() or {}
        prompt = data.get("message", "")
        model = data.get("model", "mistral:7b")
        max_tokens = data.get("max_tokens", 4096)

        # Log request details
        logger.info(f"MLX chat request: model={model}, prompt={prompt[:100]}...")

        # Handle streaming response
        if request.headers.get('Accept') == 'text/event-stream':
            def generate_response():
                try:
                    for chunk in provider.stream_chat_response(
                        prompt=prompt,
                        model=model,
                        max_tokens=max_tokens
                    ):
                        if isinstance(chunk, dict):
                            if "error" in chunk:
                                yield json.dumps({
                                    "error": chunk["error"],
                                    "model": model,
                                    "provider": "mlx"
                                }) + "\n\n"
                            elif "content" in chunk:
                                yield json.dumps({
                                    "message": chunk,
                                    "model": model,
                                    "provider": "mlx"
                                }) + "\n\n"
                        elif isinstance(chunk, str):
                            yield json.dumps({
                                "message": {
                                    "content": chunk
                                },
                                "model": model,
                                "provider": "mlx"
                            }) + "\n\n"
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error generating streaming response: {error_msg}")
                    yield json.dumps({"error": error_msg}) + "\n\n"

            response = Response(generate_response(), mimetype="text/event-stream")
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['Connection'] = 'keep-alive'
            response.headers['X-Accel-Buffering'] = 'no'
            
            # Explicitly set CORS headers for streaming response
            origin = request.headers.get('Origin')
            if origin == 'https://actuallyusefulai.com':
                response.headers['Access-Control-Allow-Origin'] = origin 
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key, Accept, Origin, User-Agent'
                response.headers['Access-Control-Expose-Headers'] = 'Content-Type, X-API-Key'
                
            return response

        # Handle non-streaming response
        try:
            response_text = ""
            for chunk in provider.stream_chat_response(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens
            ):
                if isinstance(chunk, dict):
                    if "error" in chunk:
                        return jsonify({"error": chunk["error"]}), 500
                    elif "content" in chunk:
                        response_text += chunk["content"]
                elif isinstance(chunk, str):
                    response_text += chunk

            return jsonify({
                "message": {"content": response_text},
                "model": model,
                "provider": "mlx"
            })

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating non-streaming response: {error_msg}")
            return jsonify({"error": error_msg}), 500

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in MLX chat endpoint: {error_msg}")
        return jsonify({"error": error_msg}), 500 


@chat_bp.route('/openai', methods=['POST'])
def openai_chat():
    """Handle OpenAI chat requests with file upload support."""
    try:
        provider = ProviderFactory.get_provider("openai")
        if not provider:
            logger.error("OpenAI provider not available")
            return jsonify({"error": "OpenAI provider not available"}), 503
            
        # Initialize mimetypes if not already done
        if not mimetypes.inited:
            mimetypes.init()
            
        # Check if there are file uploads
        files = request.files.getlist('file')
        file_paths = []
        
        if files and any(file.filename for file in files):
            logger.info(f"Received {len(files)} files for OpenAI chat")
            
            # Create temporary directory to store uploaded files
            temp_dir = tempfile.mkdtemp(prefix="openai_upload_")
            
            # Save uploaded files to temporary directory
            for file in files:
                if file.filename:
                    file_path = os.path.join(temp_dir, file.filename)
                    file.save(file_path)
                    file_paths.append(file_path)
                    
                    # Log file type information
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type:
                        logger.info(f"Saved uploaded file: {file_path} (type: {mime_type})")
                        
                        # Special handling note for PDFs
                        if mime_type == "application/pdf":
                            logger.warning(f"PDF file detected: {file_path}. This endpoint only processes images. For PDF processing, use the /responses endpoint.")
                    else:
                        logger.info(f"Saved uploaded file: {file_path} (unknown type)")
                    
        # Get other parameters from form data or JSON
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
            
        prompt = data.get('prompt', 'How can I help you today?')
        model = data.get('model', 'gpt-4o-2024-11-20')
        max_tokens = int(data.get('max_tokens', 1024))
        temperature = float(data.get('temperature', 0.7))
        stream_mode = convert_to_bool(data.get('stream', 'false'))
        
        logger.info(f"OpenAI chat request: model={model}, files={len(file_paths)}, stream={stream_mode}")
        
        # Handle streaming response
        if stream_mode:
            def generate_response():
                try:
                    yield format_chunk({"type": "start", "content": ""})
                    
                    for chunk in provider.stream_chat_response(
                        message=prompt,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        file_paths=file_paths
                    ):
                        yield format_chunk(chunk)
                        
                    yield format_chunk({"type": "complete", "tokens": max_tokens})
                    
                except Exception as e:
                    logger.error(f"Error generating response: {str(e)}")
                    yield format_chunk(str(e), is_error=True)
                
                finally:
                    # Clean up temporary files
                    if file_paths:
                        for file_path in file_paths:
                            try:
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                    logger.debug(f"Removed temporary file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Failed to remove temporary file {file_path}: {e}")
                        
                        try:
                            if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                                os.rmdir(temp_dir)
                                logger.debug(f"Removed temporary directory: {temp_dir}")
                        except Exception as e:
                            logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
            
            # Return streaming response
            response = Response(
                stream_with_context(generate_response()),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
            
            return response
        else:
            # Non-streaming response
            try:
                full_response = ""
                for chunk in provider.stream_chat_response(
                    message=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    file_paths=file_paths
                ):
                    if isinstance(chunk, dict) and "content" in chunk:
                        full_response += chunk["content"]
                    elif isinstance(chunk, str):
                        full_response += chunk
                
                response_json = {
                    "content": full_response,
                    "model": model,
                    "provider": "openai"
                }
                
                return jsonify(response_json)
            
            except Exception as e:
                logger.error(f"Error generating non-streaming response: {str(e)}")
                return jsonify({"error": str(e)}), 500
                
            finally:
                # Clean up temporary files
                if file_paths:
                    for file_path in file_paths:
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                logger.debug(f"Removed temporary file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Failed to remove temporary file {file_path}: {e}")
                    
                    try:
                        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                            os.rmdir(temp_dir)
                            logger.debug(f"Removed temporary directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
    
    except Exception as e:
        logger.error(f"Error in OpenAI chat: {str(e)}")
        return jsonify({"error": str(e)}), 500 


@chat_bp.route('/responses', methods=['POST'])
def openai_responses():
    """Handle OpenAI Responses API requests for document processing."""
    try:
        provider = ProviderFactory.get_provider("openai")
        if not provider:
            logger.error("OpenAI provider not available")
            return jsonify({"error": "OpenAI provider not available"}), 503
            
        # Initialize mimetypes if not already done
        if not mimetypes.inited:
            mimetypes.init()
            
        # Check for files (optional)
        files = request.files.getlist('file')
        document_paths = []
        
        if files and any(file.filename for file in files):
            # Create temporary directory to store uploaded files
            temp_dir = tempfile.mkdtemp(prefix="openai_responses_")
            
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
        
        logger.info(f"OpenAI Responses request: model={model}, documents={len(document_paths)}, stream={stream_mode}")
        
        # Handle streaming response
        if stream_mode:
            def generate_response():
                try:
                    yield format_chunk({"type": "start", "content": ""})
                    
                    for chunk in provider.create_response(
                        document_paths=document_paths,
                        prompt=prompt,
                        model=model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stream=True
                    ):
                        yield format_chunk(chunk)
                        
                    yield format_chunk({"type": "complete", "tokens": max_tokens})
                    
                except Exception as e:
                    logger.error(f"Error generating response: {str(e)}")
                    yield format_chunk(str(e), is_error=True)
                    
                finally:
                    # Clean up temporary files
                    if document_paths:
                        for doc_path in document_paths:
                            try:
                                if os.path.exists(doc_path):
                                    os.remove(doc_path)
                                    logger.debug(f"Removed temporary file: {doc_path}")
                            except Exception as e:
                                logger.warning(f"Failed to remove temporary file {doc_path}: {e}")
                        
                        try:
                            if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                                os.rmdir(temp_dir)
                                logger.debug(f"Removed temporary directory: {temp_dir}")
                        except Exception as e:
                            logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
            
            # Return streaming response
            response = Response(
                stream_with_context(generate_response()),
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
            # Non-streaming response
            try:
                response_data = provider.create_response(
                    document_paths=document_paths,
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False
                )
                
                return jsonify(response_data)
            
            except Exception as e:
                logger.error(f"Error generating non-streaming response: {str(e)}")
                return jsonify({"error": str(e)}), 500
                
            finally:
                # Clean up temporary files
                if document_paths:
                    for doc_path in document_paths:
                        try:
                            if os.path.exists(doc_path):
                                os.remove(doc_path)
                                logger.debug(f"Removed temporary file: {doc_path}")
                        except Exception as e:
                            logger.warning(f"Failed to remove temporary file {doc_path}: {e}")
                    
                    try:
                        if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                            os.rmdir(temp_dir)
                            logger.debug(f"Removed temporary directory: {temp_dir}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")
    
    except Exception as e:
        logger.error(f"Error in OpenAI Responses: {str(e)}")
        return jsonify({"error": str(e)}), 500


@chat_bp.route('/responses/<response_id>', methods=['GET'])
def retrieve_openai_response(response_id):
    """Retrieve a previously created OpenAI response."""
    try:
        provider = ProviderFactory.get_provider("openai")
        if not provider:
            logger.error("OpenAI provider not available")
            return jsonify({"error": "OpenAI provider not available"}), 503
        
        response_data = provider.retrieve_response(response_id)
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error retrieving OpenAI response: {str(e)}")
        return jsonify({"error": str(e)}), 500 