#!/usr/bin/env python
from typing import Dict, Optional, Any, Type
import importlib
import logging

from api.config import (
    ANTHROPIC_API_KEY, OPENAI_API_KEY, PERPLEXITY_API_KEY,
    MISTRAL_API_KEY, COHERE_API_KEY, XAI_API_KEY,
    COZE_AUTH_TOKEN, COZE_BOT_ID, COZE_TTS_BOT_ID
)
from api.services.providers.base import BaseProvider

# Logger for this module
logger = logging.getLogger(__name__)

class ProviderFactory:
    """Factory for creating provider instances."""
    
    # Dictionary mapping provider names to their implementations
    _provider_classes: Dict[str, Type[BaseProvider]] = {}
    
    # Dictionary of initialized provider instances
    _instances: Dict[str, BaseProvider] = {}
    
    @classmethod
    def register_provider(cls, provider_name: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a provider class with the factory.
        
        Args:
            provider_name: Name of the provider (e.g., 'anthropic', 'openai')
            provider_class: The provider class to register
        """
        cls._provider_classes[provider_name] = provider_class
        logger.info(f"Registered provider: {provider_name}")
    
    @classmethod
    def get_provider(cls, provider_name: str) -> Optional[BaseProvider]:
        """
        Get a provider instance by name. Initializes if not already initialized.
        
        Args:
            provider_name: Name of the provider to get
            
        Returns:
            Initialized provider instance or None if provider not registered
        """
        # Check if already initialized
        if provider_name in cls._instances:
            return cls._instances[provider_name]
        
        # Get the appropriate API key based on provider name
        api_key = cls._get_api_key(provider_name)
        
        # Try to initialize provider
        if provider_name in cls._provider_classes:
            try:
                # Special case for Coze which requires the API key only
                if provider_name == 'coze':
                    cls._instances[provider_name] = cls._provider_classes[provider_name](api_key=api_key)
                # Special case for MLX and LM Studio which don't need an API key
                elif provider_name in ['mlx', 'lmstudio']:
                    cls._instances[provider_name] = cls._provider_classes[provider_name]()
                else:
                    # Standard initialization with API key
                    cls._instances[provider_name] = cls._provider_classes[provider_name](api_key)
                    
                logger.info(f"Initialized provider: {provider_name}")
                return cls._instances[provider_name]
            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}: {str(e)}")
                return None
        else:
            logger.warning(f"Provider not registered: {provider_name}")
            return None
    
    @classmethod
    def _get_api_key(cls, provider_name: str) -> Optional[str]:
        """
        Get the API key for a provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            API key for the provider or None if not available
        """
        api_keys = {
            'anthropic': ANTHROPIC_API_KEY,
            'openai': OPENAI_API_KEY,
            'perplexity': PERPLEXITY_API_KEY,
            'mistral': MISTRAL_API_KEY,
            'cohere': COHERE_API_KEY,
            'xai': XAI_API_KEY,
            'coze': COZE_AUTH_TOKEN,
            'ollama': None,  # Ollama doesn't need an API key
            'mlx': None,     # MLX doesn't need an API key
            'lmstudio': None # LM Studio doesn't need an API key
        }
        
        return api_keys.get(provider_name)
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """
        Get all available providers and their availability status.
        
        Returns:
            Dictionary mapping provider names to their availability
        """
        providers = {
            'anthropic': ANTHROPIC_API_KEY is not None,
            'openai': OPENAI_API_KEY is not None,
            'perplexity': PERPLEXITY_API_KEY is not None,
            'mistral': MISTRAL_API_KEY is not None,
            'cohere': COHERE_API_KEY is not None,
            'xai': XAI_API_KEY is not None,
            'coze': COZE_AUTH_TOKEN is not None,
            'ollama': True,  # Ollama is always available locally
            'mlx': True,     # MLX is always available on Apple Silicon
            'lmstudio': True # LM Studio is always available when server is running
        }
        
        return providers

# Initialize factory with providers
def initialize_providers():
    """Import and register all provider implementations."""
    try:
        # Import known provider modules
        from api.services.providers.anthropic import AnthropicProvider
        from api.services.providers.mistral import MistralProvider
        from api.services.providers.lmstudio import LMStudioProvider
        from api.services.providers.mlx import MLXProvider
        
        # Register providers with factory
        ProviderFactory.register_provider('anthropic', AnthropicProvider)
        ProviderFactory.register_provider('mistral', MistralProvider)
        ProviderFactory.register_provider('lmstudio', LMStudioProvider)
        ProviderFactory.register_provider('mlx', MLXProvider)
        
        # Dynamically load other providers
        other_providers = {
            'openai': 'api.services.providers.openai.OpenAIProvider',
            'ollama': 'api.services.providers.ollama.OllamaProvider',
            'perplexity': 'api.services.providers.perplexity.PerplexityProvider',
            'cohere': 'api.services.providers.cohere.CohereProvider',
            'xai': 'api.services.providers.xai.XAIProvider',
            'coze': 'api.services.providers.coze.CozeProvider'
        }
        
        for provider_name, provider_path in other_providers.items():
            try:
                # Split the path into module and class name
                module_path, class_name = provider_path.rsplit('.', 1)
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Get the class
                provider_class = getattr(module, class_name)
                
                # Register the provider
                ProviderFactory.register_provider(provider_name, provider_class)
            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to load provider {provider_name}: {str(e)}")
                
    except ImportError as e:
        logger.warning(f"Failed to import core providers: {str(e)}")
        # If explicit import fails, fall back to dynamic loading
        providers = {
            'anthropic': 'api.services.providers.anthropic.AnthropicProvider',
            'openai': 'api.services.providers.openai.OpenAIProvider',
            'ollama': 'api.services.providers.ollama.OllamaProvider',
            'perplexity': 'api.services.providers.perplexity.PerplexityProvider',
            'mistral': 'api.services.providers.mistral.MistralProvider',
            'cohere': 'api.services.providers.cohere.CohereProvider',
            'xai': 'api.services.providers.xai.XAIProvider',
            'coze': 'api.services.providers.coze.CozeProvider',
            'mlx': 'api.services.providers.mlx.MLXProvider',
            'lmstudio': 'api.services.providers.lmstudio.LMStudioProvider'
        }
        
        for provider_name, provider_path in providers.items():
            try:
                # Split the path into module and class name
                module_path, class_name = provider_path.rsplit('.', 1)
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Get the class
                provider_class = getattr(module, class_name)
                
                # Register the provider
                ProviderFactory.register_provider(provider_name, provider_class)
            except (ImportError, AttributeError) as e:
                logger.warning(f"Failed to load provider {provider_name}: {str(e)}")


# Initialize providers when this module is imported
initialize_providers() 