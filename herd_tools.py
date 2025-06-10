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

# Try to import dotenv for .env loading
try:
    from dotenv import load_dotenv
    import os
    from pathlib import Path
    
    # Load environment variables from .env file
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass  # Silently continue if dotenv is not available

# Try import with robust error handling
try:
    # First try direct imports (for standalone use)
    try:
        # Core functionalities
        from cli import main
        from config import OLLAMA_MODEL
        from rename import process_renames
        from snippets import process_snippets
        from idealize import process_ideal
        from docs import generate_docs, export_document_summary
        from citations import process_file_or_directory
        from image_processor import process_images_cli
        
        # Utilities
        from utils.analysis import analyze_documents, generate_document_summary
        from utils.cache import clear_cache
    except ImportError:
        # Then try package imports (when installed)
        try:
            # Core functionalities
            from herd_ai.cli import main
            from herd_ai.config import OLLAMA_MODEL
            from herd_ai.rename import process_renames
            from herd_ai.snippets import process_snippets
            from herd_ai.idealize import process_ideal
            from herd_ai.docs import generate_docs, export_document_summary
            from herd_ai.citations import process_file_or_directory
            from herd_ai.image_processor import process_images_cli
            
            # Utilities
            from herd_ai.utils.analysis import analyze_documents, generate_document_summary
            from herd_ai.utils.cache import clear_cache
        except ImportError:
            # Legacy imports (for backward compatibility)
            from llamacleaner.cli import main
            from llamacleaner.config import OLLAMA_MODEL
            from llamacleaner.rename import process_renames
            from llamacleaner.snippets import process_snippets
            from llamacleaner.idealize import process_ideal
            from llamacleaner.docs import generate_docs, export_document_summary
            from llamacleaner.citations import process_file_or_directory
            from llamacleaner.image_processor import process_images_cli
            
            # Utilities
            from llamacleaner.utils.analysis import analyze_documents, generate_document_summary
            from llamacleaner.utils.cache import clear_cache
except Exception as e:
    print(f"Error initializing package: {e}")
    print("Some functions may not be available.")

# Compatibility layer for transition from llamacleaner to herd-ai
import warnings

def _show_rename_warning():
    warnings.warn(
        "The 'llamacleaner' package has been renamed to 'herd-ai'. "
        "Please update your imports and installation.",
        DeprecationWarning,
        stacklevel=2
    ) 