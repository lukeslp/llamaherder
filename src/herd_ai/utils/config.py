"""
===============================================================================
herd_ai.utils.config
-------------------------------------------------------------------------------
This module provides utility functions for managing configuration settings
for the Herd AI application. Configuration is stored in a JSON file located
at the project root. The configuration includes provider selection and
API credentials for different providers.

All functions handle file I/O and JSON serialization/deserialization.
===============================================================================
"""

import os
import json
from typing import Optional, List

# -----------------------------------------------------------------------------
# CONFIG_PATH: Path to the configuration JSON file at the project root.
# -----------------------------------------------------------------------------
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'config.json'
)

# Maximum number of recent models to remember
MAX_RECENT_MODELS = 5

# -----------------------------------------------------------------------------
# _load_config
# -----------------------------------------------------------------------------
# Loads the configuration from the config.json file.
#
# Returns:
#     dict: The configuration dictionary. Returns an empty dict if the file
#           does not exist or cannot be read.
# -----------------------------------------------------------------------------
def _load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def set_provider(provider: str):
    config = _load_config()
    config['provider'] = provider
    _save_config(config)

def get_provider() -> Optional[str]:
    config = _load_config()
    return config.get('provider')

def set_api_key(provider: str, api_key: str):
    config = _load_config()
    if 'api_keys' not in config:
        config['api_keys'] = {}
    config['api_keys'][provider] = api_key
    _save_config(config)

def get_api_key(provider: str) -> Optional[str]:
    config = _load_config()
    return config.get('api_keys', {}).get(provider)

def clear_api_key(provider: str):
    config = _load_config()
    if 'api_keys' in config and provider in config['api_keys']:
        del config['api_keys'][provider]
        _save_config(config)

def clear_provider():
    config = _load_config()
    if 'provider' in config:
        del config['provider']
        _save_config(config)

# -----------------------------------------------------------------------------
# Ollama Model Configuration Functions
# -----------------------------------------------------------------------------

def set_ollama_model(model_name: str):
    """
    Set the current Ollama model and add it to the list of recent models.
    
    Args:
        model_name: Name of the Ollama model to set as active
    """
    config = _load_config()
    config['ollama_model'] = model_name
    
    # Initialize recent models list if it doesn't exist
    if 'ollama_recent_models' not in config:
        config['ollama_recent_models'] = []
    
    # Add to recent models (move to front if already exists)
    if model_name in config['ollama_recent_models']:
        config['ollama_recent_models'].remove(model_name)
    
    # Add at the beginning and maintain limited history
    config['ollama_recent_models'].insert(0, model_name)
    config['ollama_recent_models'] = config['ollama_recent_models'][:MAX_RECENT_MODELS]
    
    _save_config(config)

def get_ollama_model() -> str:
    """
    Get the current Ollama model.
    
    Returns:
        The current Ollama model name or the default from config.py
    """
    config = _load_config()
    # If no model is set, we'll rely on the default from config.py
    return config.get('ollama_model')

def get_recent_ollama_models() -> List[str]:
    """
    Get the list of recently used Ollama models.
    
    Returns:
        List of recently used Ollama model names
    """
    config = _load_config()
    return config.get('ollama_recent_models', [])

def clear_ollama_model():
    """
    Clear the current Ollama model setting, reverting to the default.
    """
    config = _load_config()
    if 'ollama_model' in config:
        del config['ollama_model']
        _save_config(config)

def clear_recent_ollama_models():
    """
    Clear the list of recently used Ollama models.
    """
    config = _load_config()
    if 'ollama_recent_models' in config:
        del config['ollama_recent_models']
        _save_config(config) 