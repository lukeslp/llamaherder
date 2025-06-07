#!/usr/bin/env python
import os
import functools
import logging
from typing import Dict, Callable, Any, List, Optional
from flask import request, jsonify, current_app
import time
import hashlib
import hmac

from api.config import API_KEY_HEADER
from api.utils.errors import AuthenticationError, AuthorizationError, RateLimitError

# Logger for this module
logger = logging.getLogger(__name__)

# Dictionary to store API keys and their corresponding information
# In a production environment, this would be stored in a database
API_KEYS: Dict[str, Dict[str, Any]] = {
    # Example API key, should be replaced in production
    "test_api_key": {
        "user_id": "test_user",
        "name": "Test User",
        "rate_limit": 100,  # Requests per minute
        "scopes": ["chat:read", "chat:write", "alt:read", "alt:write", "tools:read", "tools:write", "files:read", "files:write"],
    }
}

# Dictionary to store rate limiting information
RATE_LIMITS: Dict[str, Dict[str, Any]] = {}


def verify_api_key(api_key: str) -> Dict[str, Any]:
    """
    Verify if an API key is valid.
    
    Args:
        api_key: The API key to verify
        
    Returns:
        API key information dictionary if valid
        
    Raises:
        AuthenticationError: If the API key is invalid
    """
    if api_key in API_KEYS:
        return API_KEYS[api_key]
    else:
        raise AuthenticationError("Invalid API key")


def check_rate_limit(api_key: str, user_info: Dict[str, Any]) -> None:
    """
    Check if the rate limit for an API key has been exceeded.
    
    Args:
        api_key: The API key to check
        user_info: API key information dictionary
        
    Raises:
        RateLimitError: If the rate limit has been exceeded
    """
    now = time.time()
    
    # Get or initialize rate limit info for this API key
    if api_key not in RATE_LIMITS:
        RATE_LIMITS[api_key] = {
            "requests": [],
            "limit": user_info.get("rate_limit", 60)  # Default to 60 requests per minute
        }
    
    rate_info = RATE_LIMITS[api_key]
    
    # Remove requests older than 1 minute
    rate_info["requests"] = [t for t in rate_info["requests"] if now - t < 60]
    
    # Check if rate limit exceeded
    if len(rate_info["requests"]) >= rate_info["limit"]:
        raise RateLimitError(
            f"Rate limit exceeded. Maximum {rate_info['limit']} requests per minute.",
            details={
                "limit": rate_info["limit"],
                "remaining": 0,
                "reset": min(rate_info["requests"]) + 60 if rate_info["requests"] else now + 60
            }
        )
    
    # Add current request
    rate_info["requests"].append(now)


def check_scope(user_info: Dict[str, Any], required_scope: str) -> None:
    """
    Check if a user has the required scope.
    
    Args:
        user_info: API key information dictionary
        required_scope: The scope to check for
        
    Raises:
        AuthorizationError: If the user doesn't have the required scope
    """
    if not user_info.get("scopes") or required_scope not in user_info["scopes"]:
        raise AuthorizationError(
            f"Missing required scope: {required_scope}",
            details={"required_scope": required_scope}
        )


def requires_auth(required_scope: Optional[str] = None) -> Callable:
    """
    Decorator for routes that require authentication.
    
    Args:
        required_scope: Optional scope required for the route
        
    Returns:
        Decorated function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get(API_KEY_HEADER)
            
            # If API key is not in header, check query parameters
            if not api_key:
                api_key = request.args.get("api_key")
            
            # If still no API key, try in JSON body
            if not api_key and request.is_json:
                api_key = request.json.get("api_key")
            
            # If still no API key, try in form data
            if not api_key and request.form:
                api_key = request.form.get("api_key")
            
            # If no API key provided, return error
            if not api_key:
                return jsonify({
                    "error": "AuthenticationError",
                    "message": f"Authentication required. Please provide API key in '{API_KEY_HEADER}' header."
                }), 401
            
            try:
                # Verify API key
                user_info = verify_api_key(api_key)
                
                # Check rate limit
                check_rate_limit(api_key, user_info)
                
                # Check scope if required
                if required_scope:
                    check_scope(user_info, required_scope)
                
                # Add user_info to kwargs
                kwargs["user_info"] = user_info
                
                return f(*args, **kwargs)
            
            except AuthenticationError as e:
                return jsonify(e.to_dict()), e.status_code
            except AuthorizationError as e:
                return jsonify(e.to_dict()), e.status_code
            except RateLimitError as e:
                return jsonify(e.to_dict()), e.status_code
        
        return decorated_function
    
    return decorator


def generate_hmac(message: str, secret: str) -> str:
    """
    Generate an HMAC signature for a message.
    
    Args:
        message: The message to sign
        secret: The secret key for signing
        
    Returns:
        HMAC signature as a hexadecimal string
    """
    key = secret.encode('utf-8')
    message = message.encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature 