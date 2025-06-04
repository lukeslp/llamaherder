###############################################################################
# Herd AI - Document Analysis Utilities
#
# This module provides accessible, robust, and extensible tools for:
#   - Extracting keywords from text
#   - Analyzing document content and metadata
#   - Summarizing document collections
#   - Caching analysis results for performance
#
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
                def get_file_extension(path):
                    return Path(path).suffix.lower()
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
                def get_file_text(path):
                    return Path(path).read_text(encoding='utf-8', errors='ignore')
                def is_cached(key):
                    return False
                def get_from_cache(key):
                    return None
                def save_to_cache(key, data):
                    return False
except Exception as e:
    print(f"Error importing modules in utils/analysis.py: {e}")
    print("Make sure you're running from the project directory or the package is installed.")
    def get_file_extension(path):
        return Path(path).suffix.lower()
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
    def get_file_text(path):
        return Path(path).read_text(encoding='utf-8', errors='ignore')
    def is_cached(key):
        return False
    def get_from_cache(key):
        return None
    def save_to_cache(key, data):
        return False

###############################################################################
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
    words = [w for w in words if w not in stop and len(w) > 2]
    cnt: Dict[str, int] = {}
    for w in words:
        cnt[w] = cnt.get(w, 0) + 1
    return [w for w, _ in sorted(cnt.items(), key=lambda x: -x[1])[:max_keywords]]

###############################################################################
# get_language
#
# Detects the language of the provided text.
# Currently returns 'en' (English) as a placeholder.
###############################################################################
def get_language(text: str) -> str:
    return 'en'

###############################################################################
# analyze_document
#
# Analyzes a single document, extracting metadata and content information.
# Results are cached for performance. Returns a dictionary with document info
# and analysis results.
#
# Args:
#     fp: Path to the document
#     force: If True, force re-analysis even if cached
#     provider: AI provider to use for analysis (optional)
#
# Returns:
#     Dictionary with document info and analysis
###############################################################################
def analyze_document(fp: Path, force: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
    stat = fp.stat()
    key = f"{fp}:{stat.st_mtime}"
    if not force and is_cached(key):
        return get_from_cache(key)

    info = get_file_metadata(fp)
    text = get_file_text(fp)
    res = {'info': info, 'analysis': {}}

    if text:
        kw = extract_keywords(text)
        res['analysis'] = {
            'word_count': len(text.split()),
            'keywords': kw,
            'language': get_language(text)
        }

    save_to_cache(key, res)
    return res

###############################################################################
# analyze_documents
#
# Analyzes all documents in a directory, optionally recursively.
# Returns a dictionary of analysis results by file path.
#
# Args:
#     dir: Directory to scan
#     recursive: If True, scan subdirectories too
#     force: If True, force re-analysis even if cached
#     provider: AI provider to use for analysis (optional)
#
# Returns:
#     Dictionary of analysis results by file path
###############################################################################
def analyze_documents(dir: Path, recursive: bool = True, force: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    file_types = ('.pdf', '.docx', '.txt', '.md', '.rtf', '.odt')

    for p in (dir.rglob('*') if recursive else dir.glob('*')):
        if p.is_file() and get_file_extension(p).lower() in file_types:
            results[str(p)] = analyze_document(p, force, provider=provider)

    return results

###############################################################################
# generate_document_summary
#
# Generates a summary of all documents in a directory, including:
#   - Total document count
#   - Total word count
#   - Document type distribution
#   - Top keywords across all documents
#
# Args:
#     dir: Directory to scan
#     recursive: If True, scan subdirectories too
#     force: If True, force re-analysis even if cached
#     provider: AI provider to use for analysis (optional)
#
# Returns:
#     Dictionary with summary statistics
###############################################################################
def generate_document_summary(dir: Path, recursive: bool = True, force: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
    res = analyze_documents(dir, recursive, force, provider)
    summary = {
        'count': len(res),
        'total_words': 0,
        'document_types': {},
        'top_keywords': {}
    }

    for fp, r in res.items():
        cnt = r.get('analysis', {}).get('word_count', 0)
        summary['total_words'] += cnt
        ext = r['info']['extension'].lower()
        summary['document_types'][ext] = summary['document_types'].get(ext, 0) + 1
        for kw in r.get('analysis', {}).get('keywords', []):
            summary['top_keywords'][kw] = summary['top_keywords'].get(kw, 0) + 1

    return summary