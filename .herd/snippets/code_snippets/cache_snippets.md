# Code Snippets from build/lib/herd_ai/utils/cache.py

File: `build/lib/herd_ai/utils/cache.py`  
Language: Python  
Extracted: 2025-06-07 05:09:14  

## Snippet 1
Lines 10-16

```Python
"""Caching utilities for document analysis."""

import json
import os
from pathlib import Path
from typing import Any, Optional
```

## Snippet 2
Lines 17-35

```Python
# Try import as if from a package first, fall back to direct import
try:
    # Package imports (when installed or run as a module)
    try:
        from herd_ai.config import CACHE_DIR
        from herd_ai.utils.file import ensure_directory
    except ImportError:
        # Legacy package imports
        try:
            from llamacleaner.config import CACHE_DIR
            from llamacleaner.utils.file import ensure_directory
        except ImportError:
            # Direct imports (when run directly, not as a module)
            try:
                from config import CACHE_DIR
                from utils.file import ensure_directory
            except ImportError:
                # Set default cache directory
                CACHE_DIR = Path(".herd/cache")
```

## Snippet 3
Lines 37-40

```Python
def ensure_directory(path):
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)
                    return p
```

## Snippet 4
Lines 41-45

```Python
except Exception as e:
    print(f"Error importing modules in utils/cache.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    # Set default cache directory
    CACHE_DIR = Path(".herd/cache")
```

## Snippet 5
Lines 47-51

```Python
def ensure_directory(path):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p
```

## Snippet 6
Lines 59-66

```Python
if not cf.exists():
        return False
    try:
        c = json.loads(cf.read_text())
        return key in c
    except:
        return False
```

## Snippet 7
Lines 67-75

```Python
def get_from_cache(key: str) -> Any:
    """Get a value from the document cache by key."""
    cf = get_cache_path('doc_cache')
    try:
        c = json.loads(cf.read_text())
        return c.get(key)
    except:
        return None
```

## Snippet 8
Lines 76-79

```Python
def save_to_cache(key: str, data: Any) -> bool:
    """Save a value to the document cache with the given key."""
    cf = get_cache_path('doc_cache')
    try:
```

## Snippet 9
Lines 80-83

```Python
d = {} if not cf.exists() else json.loads(cf.read_text())
        d[key] = data
        cf.write_text(json.dumps(d, indent=2))
        return True
```

## Snippet 10
Lines 87-94

```Python
def clear_cache(key: Optional[str]=None) -> bool:
    """
    Clear the document cache.

    Args:
        key: If provided, only clear this specific key. Otherwise, clear the entire cache.

    Returns:
```

## Snippet 11
Lines 100-114

```Python
if key is None:
        try:
            cf.unlink()
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    else:
        try:
            d = json.loads(cf.read_text())
            d.pop(key, None)
            cf.write_text(json.dumps(d, indent=2))
        except Exception as e:
            print(f"Error clearing cache key '{key}': {e}")
            return False
    return True
```

