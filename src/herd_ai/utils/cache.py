###############################################################################
# herd_ai.utils.cache
#
# Caching utilities for document analysis and processing.
#
# This module provides functions to store, retrieve, and manage cached data
# (typically JSON-serializable) for document analysis tasks. The cache is
# stored as a JSON file in a configurable directory. The cache directory can
# be set via project configuration, and the module is robust to different
"""Caching utilities for document analysis."""

import json
import os
from pathlib import Path
from typing import Any, Optional

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
                # Define minimal version if all imports fail
                def ensure_directory(path):
                    p = Path(path)
                    p.mkdir(parents=True, exist_ok=True)
                    return p
except Exception as e:
    print(f"Error importing modules in utils/cache.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    # Set default cache directory
    CACHE_DIR = Path(".herd/cache")
    # Define minimal version if all imports fail
    def ensure_directory(path):
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

def get_cache_path(name: str) -> Path:
    """Get the path to a cache file for the given name."""
    return ensure_directory(CACHE_DIR) / f"{name}.json"

def is_cached(key: str) -> bool:
    """Check if a key exists in the document cache."""
    cf = get_cache_path('doc_cache')
    if not cf.exists():
        return False
    try:
        c = json.loads(cf.read_text())
        return key in c
    except:
        return False

def get_from_cache(key: str) -> Any:
    """Get a value from the document cache by key."""
    cf = get_cache_path('doc_cache')
    try:
        c = json.loads(cf.read_text())
        return c.get(key)
    except:
        return None

def save_to_cache(key: str, data: Any) -> bool:
    """Save a value to the document cache with the given key."""
    cf = get_cache_path('doc_cache')
    try:
        d = {} if not cf.exists() else json.loads(cf.read_text())
        d[key] = data
        cf.write_text(json.dumps(d, indent=2))
        return True
    except:
        return False

def clear_cache(key: Optional[str]=None) -> bool:
    """
    Clear the document cache.
    
    Args:
        key: If provided, only clear this specific key. Otherwise, clear the entire cache.
        
    Returns:
        True if successful, False otherwise.
    """
    cf = get_cache_path('doc_cache')
    if not cf.exists():
        return True
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