#!/usr/bin/env python
from flask import Blueprint, request, jsonify, send_from_directory, current_app
import logging
import os
import uuid
import time
from typing import Dict, Any, List, Optional
from werkzeug.utils import secure_filename

from api.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from api.utils.errors import InvalidRequestError

# Logger for this module
logger = logging.getLogger(__name__)

# Blueprint for files routes
files_bp = Blueprint('files', __name__)


def allowed_file(filename: str) -> bool:
    """Check if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file to the server."""
    # Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    try:
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}_{int(time.time())}.{extension}"
        
        # Save the file
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {original_filename} -> {unique_filename}")
        
        return jsonify({
            "success": True,
            "file_id": unique_filename,
            "original_filename": original_filename,
            "size": os.path.getsize(filepath),
            "content_type": file.content_type
        })
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({"error": str(e)}), 500


@files_bp.route('/download/<file_id>', methods=['GET'])
def download_file(file_id: str):
    """Download a file from the server."""
    # Sanitize file_id to prevent directory traversal
    file_id = secure_filename(file_id)
    
    try:
        # Check if file exists
        filepath = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # Get the original filename from query parameters, or use file_id
        original_filename = request.args.get('filename', file_id)
        original_filename = secure_filename(original_filename)
        
        logger.info(f"File download: {file_id}")
        
        return send_from_directory(
            UPLOAD_FOLDER,
            file_id,
            download_name=original_filename,
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({"error": str(e)}), 500


@files_bp.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id: str):
    """Delete a file from the server."""
    # Sanitize file_id to prevent directory traversal
    file_id = secure_filename(file_id)
    
    try:
        # Check if file exists
        filepath = os.path.join(UPLOAD_FOLDER, file_id)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # Delete the file
        os.remove(filepath)
        
        logger.info(f"File deleted: {file_id}")
        
        return jsonify({
            "success": True,
            "message": f"File {file_id} deleted successfully"
        })
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": str(e)}), 500


@files_bp.route('/list', methods=['GET'])
def list_files():
    """List all uploaded files."""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # Get filter parameters
        filter_extension = request.args.get('extension')
        
        # Get all files in the upload directory
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                # Get file extension
                extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                # Apply extension filter if specified
                if filter_extension and extension != filter_extension.lower():
                    continue
                
                files.append({
                    "file_id": filename,
                    "size": os.path.getsize(filepath),
                    "created": os.path.getctime(filepath),
                    "extension": extension
                })
        
        # Sort files by creation time (newest first)
        files.sort(key=lambda x: x["created"], reverse=True)
        
        # Calculate pagination
        total_files = len(files)
        total_pages = (total_files + page_size - 1) // page_size
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_files)
        paginated_files = files[start_idx:end_idx]
        
        return jsonify({
            "files": paginated_files,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_files": total_files
            }
        })
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({"error": str(e)}), 500 