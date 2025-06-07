# Code Snippets from src/herd_ai/utils/config.py

File: `src/herd_ai/utils/config.py`  
Language: Python  
Extracted: 2025-06-07 05:09:52  

## Snippet 1
Lines 8-17

```Python
API credentials for different providers.

All functions handle file I/O and JSON serialization/deserialization.
===============================================================================
"""

import os
import json
from typing import Optional, List
```

## Snippet 2
Lines 20-28

```Python
# -----------------------------------------------------------------------------
CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'config.json'
)

# Maximum number of recent models to remember
MAX_RECENT_MODELS = 5
```

## Snippet 3
Lines 39-46

```Python
if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {}
```

## Snippet 4
Lines 47-51

```Python
def _save_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
```

## Snippet 5
Lines 52-56

```Python
def set_provider(provider: str):
    config = _load_config()
    config['provider'] = provider
    _save_config(config)
```

## Snippet 6
Lines 57-60

```Python
def get_provider() -> Optional[str]:
    config = _load_config()
    return config.get('provider')
```

## Snippet 7
Lines 63-67

```Python
if 'api_keys' not in config:
        config['api_keys'] = {}
    config['api_keys'][provider] = api_key
    _save_config(config)
```

## Snippet 8
Lines 68-71

```Python
def get_api_key(provider: str) -> Optional[str]:
    config = _load_config()
    return config.get('api_keys', {}).get(provider)
```

## Snippet 9
Lines 80-83

```Python
if 'provider' in config:
        del config['provider']
        _save_config(config)
```

## Snippet 10
Lines 88-97

```Python
def set_ollama_model(model_name: str):
    """
    Set the current Ollama model and add it to the list of recent models.

    Args:
        model_name: Name of the Ollama model to set as active
    """
    config = _load_config()
    config['ollama_model'] = model_name
```

## Snippet 11
Lines 103-111

```Python
if model_name in config['ollama_recent_models']:
        config['ollama_recent_models'].remove(model_name)

    # Add at the beginning and maintain limited history
    config['ollama_recent_models'].insert(0, model_name)
    config['ollama_recent_models'] = config['ollama_recent_models'][:MAX_RECENT_MODELS]

    _save_config(config)
```

## Snippet 12
Lines 112-122

```Python
def get_ollama_model() -> str:
    """
    Get the current Ollama model.

    Returns:
        The current Ollama model name or the default from config.py
    """
    config = _load_config()
    # If no model is set, we'll rely on the default from config.py
    return config.get('ollama_model')
```

## Snippet 13
Lines 123-132

```Python
def get_recent_ollama_models() -> List[str]:
    """
    Get the list of recently used Ollama models.

    Returns:
        List of recently used Ollama model names
    """
    config = _load_config()
    return config.get('ollama_recent_models', [])
```

## Snippet 14
Lines 133-137

```Python
def clear_ollama_model():
    """
    Clear the current Ollama model setting, reverting to the default.
    """
    config = _load_config()
```

## Snippet 15
Lines 138-141

```Python
if 'ollama_model' in config:
        del config['ollama_model']
        _save_config(config)
```

## Snippet 16
Lines 142-146

```Python
def clear_recent_ollama_models():
    """
    Clear the list of recently used Ollama models.
    """
    config = _load_config()
```

## Snippet 17
Lines 147-149

```Python
if 'ollama_recent_models' in config:
        del config['ollama_recent_models']
        _save_config(config)
```

