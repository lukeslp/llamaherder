#!/usr/bin/env python
from typing import Dict, Any, Optional


class APIError(Exception):
    """Base class for API exceptions."""
    
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to a dictionary for JSON response."""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code
        }
        
        if self.details:
            result["details"] = self.details
            
        return result


class InvalidRequestError(APIError):
    """Exception raised for invalid requests."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(APIError):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str = "You do not have permission to access this resource", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(APIError):
    """Exception raised for resources that are not found."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class RateLimitError(APIError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=429, details=details)


class ProviderError(APIError):
    """Exception raised for provider-specific errors."""
    
    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["provider"] = provider
        super().__init__(message, status_code=500, details=details)


class ProviderNotAvailableError(ProviderError):
    """Exception raised when a provider is not available."""
    
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(message, provider, details={"reason": "not_available"})


class ModelNotAvailableError(ProviderError):
    """Exception raised when a model is not available."""
    
    def __init__(self, message: str, provider: str, model: str):
        super().__init__(
            message, 
            provider, 
            details={
                "reason": "model_not_available",
                "model": model
            }
        ) 