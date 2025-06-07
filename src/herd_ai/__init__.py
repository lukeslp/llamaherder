"""
Herd AI - Document Analysis & Code Management Tools

A unified toolset that lets you:
  - Batch-rename files using AI based on content
  - Extract and consolidate code snippets
  - Generate project documentation summaries
  - Extract citations and build bibliographies
  - Analyze and summarize local documents
  - Process and optimize images with accessibility features
"""

__version__ = "0.2.0"
__package_name__ = "herd-ai"
__command_name__ = "herd"

# Export main functions from each module
from .cli import main 
from .config import OLLAMA_MODEL

# Core functionalities
from .rename import process_renames
from .snippets import process_snippets
from .idealize import process_ideal
from .docs import generate_docs, export_document_summary
from .image_processor import process_images_cli

# Optional citations functionality (requires bibtexparser)
try:
    from .citations import process_directory
except ImportError:
    # Provide a fallback function when bibtexparser is not available
    def process_directory(*args, **kwargs):
        print("Citations functionality requires bibtexparser. Install with: pip install bibtexparser")
        return {"success": False, "error": "bibtexparser not available"}

# Utilities
from .utils.analysis import analyze_documents, generate_document_summary
from .utils.cache import clear_cache

# Compatibility layer for transition from llamacleaner to herd-ai
import warnings

def _show_rename_warning():
    warnings.warn(
        "The 'llamacleaner' package has been renamed to 'herd-ai'. "
        "Please update your imports and installation.",
        DeprecationWarning,
        stacklevel=2
    ) 