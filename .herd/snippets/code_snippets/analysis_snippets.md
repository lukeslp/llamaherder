# Code Snippets from src/herd_ai/utils/analysis.py

File: `src/herd_ai/utils/analysis.py`  
Language: Python  
Extracted: 2025-06-07 05:09:55  

## Snippet 1
Lines 10-37

```Python
# Fallback import strategies are supported for flexible usage in different
# environments. All major functions are documented with banner comments.
###############################################################################

import re
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

###############################################################################
# Import Utility Functions with Fallbacks
#
# Attempts to import file and cache utilities from various locations.
# If all imports fail, defines minimal local versions to ensure functionality.
###############################################################################
try:
    try:
        from herd_ai.utils.file import get_file_extension, get_file_metadata, get_file_text
        from herd_ai.utils.cache import is_cached, get_from_cache, save_to_cache
    except ImportError:
        try:
            from llamacleaner.utils.file import get_file_extension, get_file_metadata, get_file_text
            from llamacleaner.utils.cache import is_cached, get_from_cache, save_to_cache
        except ImportError:
            try:
                from utils.file import get_file_extension, get_file_metadata, get_file_text
                from utils.cache import is_cached, get_from_cache, save_to_cache
            except ImportError:
```

## Snippet 2
Lines 40-49

```Python
def get_file_metadata(path):
                    p = Path(path)
                    stat = p.stat()
                    return {
                        'path': str(p),
                        'name': p.name,
                        'extension': p.suffix,
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                    }
```

## Snippet 3
Lines 58-60

```Python
except Exception as e:
    print(f"Error importing modules in utils/analysis.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
```

## Snippet 4
Lines 63-72

```Python
def get_file_metadata(path):
        p = Path(path)
        stat = p.stat()
        return {
            'path': str(p),
            'name': p.name,
            'extension': p.suffix,
            'size': stat.st_size,
            'modified': stat.st_mtime,
        }
```

## Snippet 5
Lines 83-112

```Python
# --- Herd AI Utility Imports (robust, fallback style) ---
#
# Attempts to import file and cache utilities from various locations.
# If all imports fail, defines minimal local versions to ensure functionality.
###############################################################################
try:
    from herd_ai.utils import dedupe, config as herd_config, file, scrambler, undo_log
except ImportError:
    try:
        from llamacleaner.utils import dedupe, config as herd_config, file, scrambler, undo_log
    except ImportError:
        try:
            import utils.dedupe as dedupe
            import utils.config as herd_config
            import utils.file as file
            import utils.scrambler as scrambler
            import utils.undo_log as undo_log
        except ImportError:
            dedupe = None
            herd_config = None
            file = None
            scrambler = None
            undo_log = None

###############################################################################
# extract_keywords
#
# Extracts the most frequent keywords from a text, filtering out common stop
# words. Returns a list of up to `max_keywords` keywords sorted by frequency.
###############################################################################
```

## Snippet 6
Lines 113-122

```Python
def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    stop = set([
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 'what',
        'when', 'where', 'how', 'who', 'which', 'this', 'that', 'to', 'in',
        'of', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
        'does', 'did', 'can', 'could', 'will', 'would', 'shall', 'should',
        'may', 'might', 'must', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    ])
    words = re.findall(r'\b\w+\b', text.lower())
```

## Snippet 7
Lines 135-141

```Python
def get_language(text: str) -> str:
    return 'en'

###############################################################################
# analyze_document
#
# Analyzes a single document, extracting metadata and content information.
```

## Snippet 8
Lines 153-155

```Python
def analyze_document(fp: Path, force: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
    stat = fp.stat()
    key = f"{fp}:{stat.st_mtime}"
```

## Snippet 9
Lines 156-162

```Python
if not force and is_cached(key):
        return get_from_cache(key)

    info = get_file_metadata(fp)
    text = get_file_text(fp)
    res = {'info': info, 'analysis': {}}
```

## Snippet 10
Lines 163-173

```Python
if text:
        kw = extract_keywords(text)
        res['analysis'] = {
            'word_count': len(text.split()),
            'keywords': kw,
            'language': get_language(text)
        }

    save_to_cache(key, res)
    return res
```

## Snippet 11
Lines 189-192

```Python
def analyze_documents(dir: Path, recursive: bool = True, force: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    file_types = ('.pdf', '.docx', '.txt', '.md', '.rtf', '.odt')
```

## Snippet 12
Lines 217-225

```Python
def generate_document_summary(dir: Path, recursive: bool = True, force: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
    res = analyze_documents(dir, recursive, force, provider)
    summary = {
        'count': len(res),
        'total_words': 0,
        'document_types': {},
        'top_keywords': {}
    }
```

## Snippet 13
Lines 226-230

```Python
for fp, r in res.items():
        cnt = r.get('analysis', {}).get('word_count', 0)
        summary['total_words'] += cnt
        ext = r['info']['extension'].lower()
        summary['document_types'][ext] = summary['document_types'].get(ext, 0) + 1
```

