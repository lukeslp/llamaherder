#!/usr/bin/env python
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Keys and Constants
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "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"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY") or "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"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "n8R347515VqP48oDHwBeL9BS6nW1L8zY"
COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "8K2VDJ784DPHN57zYauE03mGuslFuaxBW1NUY1LO"
XAI_API_KEY = os.getenv("XAI_API_KEY") or "xai-8zAk5VIaL3Vxpu3fO3r2aiWqqeVAZ173X04VK2R1m425uYpWOIOQJM3puq1Q38xJ2sHfbq3mX4PBxJXC"

# Coze API Constants - Using the values from flask_chat_coze.py
COZE_AUTH_TOKEN = os.getenv("COZE_AUTH_TOKEN") or "pat_x43jhhVkypZ7CrKwnFwLGLdHOAegoEQqnhFO4kIqomnw6a3Zp4EaorAYfn6EMLz4"
COZE_BOT_ID = os.getenv("COZE_BOT_ID") or "7462296933429346310"  # Alt Text Generator bot ID
COZE_TTS_BOT_ID = os.getenv("COZE_TTS_BOT_ID") or "7463319430379470854"  # TTS Generator bot ID
COZE_SPACE_ID = os.getenv("COZE_SPACE_ID") or "7345427862138912773"
HF_API_KEY = os.getenv("HF_API_KEY") or "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"

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
# Ensure the host always has the http:// prefix
if OLLAMA_HOST and not (OLLAMA_HOST.startswith("http://") or OLLAMA_HOST.startswith("https://")):
    OLLAMA_HOST = f"http://{OLLAMA_HOST}"
    logger.info(f"Added http:// prefix to OLLAMA_HOST: {OLLAMA_HOST}")

# API Configuration
API_VERSION = "v2"
API_BASE_URL = f"/v2"  # Base path for Flask routes
API_DOMAIN = "api.assisted.space"
API_FULL_URL = f"https://{API_DOMAIN}{API_BASE_URL}"
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8435"))
API_DEBUG = os.getenv("API_DEBUG", "True").lower() in ("true", "1", "t")

# Security settings
API_KEY_HEADER = "X-API-Key"
# Ensure actuallyusefulai.com is explicitly included in allowed origins
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS_ENV == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = ALLOWED_ORIGINS_ENV.split(",")
    # Add actuallyusefulai.com if not already in the list
    if "https://actuallyusefulai.com" not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append("https://actuallyusefulai.com")

# File upload settings
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "/tmp/api_uploads")
# Evaluate the expression properly - 16MB
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))  # 16 * 1024 * 1024 = 16MB
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Create upload folder if it doesn't exist
try:
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
except Exception as e:
    logger.error(f"Failed to create upload folder: {e}")

# Import additional API keys from api_keys module
from api.config.api_keys import ADDITIONAL_API_KEYS

def get_config() -> Dict[str, Any]:
    """Return all configuration as a dictionary."""
    return {k: v for k, v in globals().items() if k.isupper()} 