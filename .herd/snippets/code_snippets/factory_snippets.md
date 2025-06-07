# Code Snippets from toollama/API/api-tools/tools/Untitled/factory.py

File: `toollama/API/api-tools/tools/Untitled/factory.py`  
Language: Python  
Extracted: 2025-06-07 05:20:33  

## Snippet 1
Lines 1-6

```Python
from typing import Dict, Optional, Type
from .base import BaseProvider
from .coze import CozeProvider
from .mistral import MistralProvider
from ..utils.config import Config
```

## Snippet 2
Lines 8-16

```Python
"""Factory class for creating and managing AI providers."""

    _instance = None
    _providers: Dict[str, Type[BaseProvider]] = {
        'coze': CozeProvider,
        'mistral': MistralProvider
    }
    _instances: Dict[str, BaseProvider] = {}
```

## Snippet 3
Lines 18-22

```Python
if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```

## Snippet 4
Lines 24-28

```Python
if self._initialized:
            return
        self.config = Config()
        self._initialized = True
```

## Snippet 5
Lines 29-33

```Python
def register_provider(self, name: str, provider_class: Type[BaseProvider]) -> None:
        """Register a new provider class.

        Args:
            name: Provider name
```

## Snippet 6
Lines 38-44

```Python
def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get or create a provider instance.

        Args:
            name: Provider name

        Returns:
```

## Snippet 7
Lines 52-59

```Python
if not self.config.get_provider_key(name):
                return None

            try:
                self._instances[name] = self._providers[name]()
            except Exception:
                return None
```

## Snippet 8
Lines 63-66

```Python
def available_providers(self) -> Dict[str, bool]:
        """Get dictionary of available providers."""
        return self.config.active_providers
```

## Snippet 9
Lines 67-69

```Python
def clear_instances(self) -> None:
        """Clear all provider instances."""
        self._instances.clear()
```

