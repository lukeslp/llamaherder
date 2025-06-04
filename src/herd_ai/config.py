# =============================================================================
# OmniLlama Cleaner - Centralized Configuration Module
#
# This file defines all global configuration settings, environment variable
# overrides, file extension groupings, AI provider options, UI theming, and
# utility functions for the OmniLlama Cleaner project.
#
# All constants and functions here are intended to be imported by other modules
# to ensure consistent behavior and maintainability across the codebase.
# =============================================================================

import os
from pathlib import Path

# --- Herd AI Utility Imports (robust, fallback style) ---
try:
    from herd_ai.utils import dedupe, analysis, file, scrambler, undo_log
except ImportError:
    try:
        from llamacleaner.utils import dedupe, analysis, file, scrambler, undo_log
    except ImportError:
        try:
            import utils.dedupe as dedupe
            import utils.analysis as analysis
            import utils.file as file
            import utils.scrambler as scrambler
            import utils.undo_log as undo_log
        except ImportError:
            dedupe = None
            analysis = None
            file = None
            scrambler = None
            undo_log = None

# =============================================================================
# Directory and Path Configuration
# -----------------------------------------------------------------------------
# Sets up base directories for storing user data and cache, using environment
# variables if provided, and ensures these directories exist.
# =============================================================================
HOME_DIR = Path.home()
BASE_DIR = os.environ.get("LLAMACLEANER_BASE_DIR", str(HOME_DIR / ".herd"))
CACHE_DIR = os.environ.get("LLAMACLEANER_CACHE_DIR", str(Path(BASE_DIR) / "cache"))

Path(BASE_DIR).mkdir(exist_ok=True)
Path(CACHE_DIR).mkdir(exist_ok=True)

# =============================================================================
# File Extension Groupings
# -----------------------------------------------------------------------------
# Defines sets and mappings for different file types used throughout the app.
# These are used for filtering, processing, and feature enablement.
# =============================================================================
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'React JSX',
    '.tsx': 'React TSX',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.less': 'Less',
    '.php': 'PHP',
    '.rb': 'Ruby',
    '.go': 'Go',
    '.rs': 'Rust',
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C Header',
    '.hpp': 'C++ Header',
    '.cs': 'C#',
    '.swift': 'Swift',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    '.dart': 'Dart'
}

TEXT_EXTENSIONS = {
    '.txt', '.md', '.rst', '.tex',
    '.json', '.yaml', '.yml', '.toml', '.xml',
    '.env', '.properties', '.conf', '.ini',
    '.sql', '.graphql',
    '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd'
}

DOCUMENT_EXTENSIONS = {
    '.pdf',
    '.docx', '.doc',
    '.pptx', '.ppt',
    '.xlsx', '.xls',
    '.odt', '.ods', '.odp'
}

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif',
    '.webp', '.bmp', '.tiff', '.svg'
}

SNIPPET_EXTENSIONS = CODE_EXTENSIONS
IDEALIZE_EXTENSIONS = CODE_EXTENSIONS.keys() | TEXT_EXTENSIONS
CITATION_EXTENSIONS = TEXT_EXTENSIONS | DOCUMENT_EXTENSIONS
PROCESS_EXTENSIONS = CODE_EXTENSIONS.keys() | TEXT_EXTENSIONS | DOCUMENT_EXTENSIONS
SUPPORTED_EXTENSIONS = CODE_EXTENSIONS.keys() | TEXT_EXTENSIONS | DOCUMENT_EXTENSIONS | IMAGE_EXTENSIONS

EXCLUDE_PATTERNS = {
    '.git', '.ipynb_checkpoints', '__pycache__',
    '.DS_Store', '.env', '.idea', '.vscode',
    'node_modules', 'build', 'dist', 'target',
    'coverage', '.next', '.nuxt', '.cache'
}

# =============================================================================
# AI Provider and Model Configuration
# -----------------------------------------------------------------------------
# Defines available AI providers, their API endpoints, and model names.
# Environment variables can override defaults for flexibility.
# =============================================================================
AI_PROVIDERS = ["ollama", "xai", "openai", "anthropic", "gemini", "groq", "cohere", "mistral"]
DEFAULT_AI_PROVIDER = os.environ.get("LLAMACLEANER_AI_PROVIDER", "xai")

# Ollama configuration
OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
OLLAMA_CHAT_API_URL = f"{OLLAMA_API_URL}/api/chat"
OLLAMA_TEXT_MODEL = os.environ.get("OLLAMA_TEXT_MODEL", "gemma3:4b")
OLLAMA_IMAGE_MODEL = os.environ.get("OLLAMA_IMAGE_MODEL", "gemma3:4b")
OLLAMA_MODEL = OLLAMA_TEXT_MODEL
# Store history of Ollama models used for easier switching
OLLAMA_RECENT_MODELS = []
# Maximum number of recent models to remember
OLLAMA_MAX_RECENT_MODELS = 5

XAI_API_URL = os.environ.get("XAI_API_URL", "https://api.x.ai/v1")
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
XAI_TEXT_MODEL = os.environ.get("XAI_TEXT_MODEL", "grok-3-beta")
XAI_IMAGE_MODEL = os.environ.get("XAI_IMAGE_MODEL", "grok-2-vision-latest")

GEMINI_API_URL = os.environ.get("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyB6YEhNp-Bt5I4vUbST0Q2cspvA95Oho4k")
GEMINI_TEXT_MODEL = os.environ.get("GEMINI_TEXT_MODEL", "gemini-2.5-flash-preview-04-17")
GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-preview-04-17")

# Add Cohere configurations if they don't already exist
COHERE_API_KEY = os.environ.get("COHERE_API_KEY", "")
DEFAULT_COHERE_MODEL = "command-a-03-2025"

# OpenAI API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_OPENAI_MODEL = "gpt-4o"

# Add Mistral API key and default model configurations
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
DEFAULT_MISTRAL_MODEL = "mistral-medium"
DEFAULT_MISTRAL_IMAGE_MODEL = "mistral-large"  # For vision capabilities

# Update provider display names to include Mistral
PROVIDER_DISPLAY_NAMES = {
    "ollama": "Ollama (Local)",
    "xai": "X.AI/Grok (API)",
    "openai": "OpenAI (API)",
    "anthropic": "Anthropic Claude (API)",
    "gemini": "Google Gemini (API)",
    "groq": "Groq (API)",
    "cohere": "Cohere (API)",
    "mistral": "Mistral AI (API)"
}

# =============================================================================
# Logging and Processing Settings
# -----------------------------------------------------------------------------
# Controls log verbosity, batch sizes, and file size limits for processing.
# =============================================================================
LOG_LEVEL = os.environ.get("LLAMACLEANER_LOG_LEVEL", "INFO")
BATCH_SIZE = int(os.environ.get("LLAMACLEANER_BATCH_SIZE", "100"))
MAX_FILE_SIZE = int(os.environ.get("LLAMACLEANER_MAX_FILE_SIZE", str(1024 * 1024)))

# =============================================================================
# UI Theming and Accessibility
# -----------------------------------------------------------------------------
# Defines color schemes for the CLI and UI, including high-contrast options.
# =============================================================================
UI_THEME = os.environ.get("LLAMACLEANER_THEME", "default")
UI_COLORS = {
    "default": {
        "header": "bold magenta",
        "footer": "dim",
        "menu_border": "cyan",
        "menu_title": "bold cyan",
        "panel_border": "blue",
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "info": "cyan",
    },
    "high_contrast": {
        "header": "bold white on black",
        "footer": "white on black",
        "menu_border": "white on black",
        "menu_title": "bold white on black",
        "panel_border": "white on black",
        "success": "bold white on green",
        "error": "bold white on red",
        "warning": "bold black on yellow",
        "info": "bold black on cyan",
    }
}

# =============================================================================
# Prompt Templates for LLM Interactions
# -----------------------------------------------------------------------------
# Provides reusable prompt templates for instructions, file renaming, and
# image alt text generation, with accessibility and clarity in mind.
# =============================================================================
INSTRUCTION_TEMPLATE = (
    "You are a helpful AI assistant. Your task is to provide clear, concise responses "
    "based on the given input. Focus on being accurate and practical. If you're unsure, "
    "say so rather than making assumptions. Keep responses focused and relevant to the "
    "specific task at hand."
)

RENAME_TEMPLATE = (
    "You are an assistant that renames files to improve clarity and usability. "
    "Suggest a short, practical filename in lowercase, using underscores instead of spaces. "
    "Limit to 6-10 words and 120 characters total. Exclude file extensions. "
    "Do NOT repeat the current filename; if you cannot improve it, append `_v2`. "
    "Do NOT append or prepend things like filename_ - remove generic identifiers like that where present. "
    "If you lack information, still generate a descriptive name without asking for more details. "
    "If the file is a journal‐article PDF, detect the first author's last name(s), "
    "the publication year, then a concise rendition of the article title (6–8 words), "
    "joined by underscores. For example steuber_2015_schizophrenia_bipolar_analysis "
    "Respond with ONLY the filename (no extensions) and no extra text. "
    "Example: descriptive_name_for_file_without_extension_six_to_twelve_words"
)

IMAGE_ALT_TEXT_TEMPLATE = (
    "You are an AI specializing in describing images for accessibility purposes. "
    "Write comprehensive alt text for this image, as though for a blind engineer who needs "
    "to understand every detail of the information including text. "
    "Also suggest a 6=10 word descriptive filename based on the content of the image. "
    "Format your response in this exact JSON structure:\n"
    "{\n"
    "  \"description\": \"Detailed description of the image\",\n"
    "  \"alt_text\": \"Concise alt text for the image\",\n"
    "  \"suggested_filename\": \"descriptive_name_for_file_without_extension_six_to_twelve_words\",\n"
    "  \"tags\": [\"tag1\", \"tag2\", ...]\n"
    "}"
)

BASE_DIR_NAME = ".herd"
DEFAULT_OCR_LANGUAGE = "eng"

# =============================================================================
# Utility Functions for File Type and Model Selection
# -----------------------------------------------------------------------------
# These functions help determine file types and select the appropriate AI model
# for a given file and provider.
# =============================================================================

def is_code_extension(file_path):
    """
    Determine if a file has a recognized code extension.

    Args:
        file_path: Path or object with .suffix or .name attribute.

    Returns:
        bool: True if the file is a code file, False otherwise.
    """
    ext = file_path.suffix.lower() if hasattr(file_path, 'suffix') else ''
    if not ext and hasattr(file_path, 'name'):
        parts = file_path.name.split('.')
        if len(parts) > 1:
            ext = f".{parts[-1].lower()}"
    return ext in CODE_EXTENSIONS

def is_image_extension(file_path):
    """
    Determine if a file has a recognized image extension.

    Args:
        file_path: Path or object with .suffix or .name attribute.

    Returns:
        bool: True if the file is an image file, False otherwise.
    """
    ext = file_path.suffix.lower() if hasattr(file_path, 'suffix') else ''
    if not ext and hasattr(file_path, 'name'):
        parts = file_path.name.split('.')
        if len(parts) > 1:
            ext = f".{parts[-1].lower()}"
    return ext in IMAGE_EXTENSIONS

def get_model_for_file(file_path, provider="ollama"):
    """
    Selects the appropriate model for a file based on its extension and the specified provider.
    
    Args:
        file_path: File path to determine model from
        provider: AI provider name
        
    Returns:
        Model name as string
    """
    # Default to text model unless overridden
    provider = provider.lower()
    
    # Handle image files
    if is_image_extension(file_path):
        if provider == "ollama":
            return OLLAMA_IMAGE_MODEL
        elif provider == "xai":
            return XAI_IMAGE_MODEL 
        elif provider == "gemini":
            return GEMINI_IMAGE_MODEL
        elif provider == "openai":
            return DEFAULT_OPENAI_IMAGE_MODEL
        elif provider == "mistral":
            return DEFAULT_MISTRAL_IMAGE_MODEL
        else:
            # Default image model fallback
            return OLLAMA_IMAGE_MODEL
            
    # Handle code files (prioritize code models when available)
    if is_code_extension(file_path):
        if provider == "ollama":
            return OLLAMA_CODE_MODEL if 'OLLAMA_CODE_MODEL' in globals() else OLLAMA_TEXT_MODEL
        elif provider == "xai":
            return XAI_MODEL  # X.AI doesn't have a specific code model yet
        elif provider == "gemini":
            return GEMINI_MODEL  # Use the text model for code
        elif provider == "openai":
            return DEFAULT_OPENAI_MODEL  # Use the default model for code
        elif provider == "mistral":
            return DEFAULT_MISTRAL_MODEL  # No specific code model
        elif provider == "cohere":
            return DEFAULT_COHERE_MODEL  # No specific code model
        else:
            return DEFAULT_MODEL
    
    # Default model selection by provider for text/other files
    if provider == "ollama":
        return OLLAMA_TEXT_MODEL
    elif provider == "xai":
        return XAI_MODEL
    elif provider == "gemini":
        return GEMINI_MODEL
    elif provider == "openai":
        return DEFAULT_OPENAI_MODEL
    elif provider == "cohere":
        return DEFAULT_COHERE_MODEL
    elif provider == "mistral":
        return DEFAULT_MISTRAL_MODEL
    else:
        return DEFAULT_MODEL 