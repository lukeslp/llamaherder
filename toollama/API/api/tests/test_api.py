#!/usr/bin/env python3

# =====================================================
# Camina Chat API Testing Script (Python Version)
# =====================================================
# This script tests all endpoints of the Camina Chat API
# including Anthropic, Mistral, Ollama, OpenAI, Cohere, X.AI (Grok), Coze, Perplexity, and MLX providers.
# 
# Author: Luke Steuber
# Date: August 23, 2024
# Updated: February 25, 2025 - Added Perplexity provider tests
# Updated: February 26, 2025 - Added MLX provider tests
# Based on the original bash script from February 25, 2024
# =====================================================

import os
import sys
import json
import base64
import requests
import tempfile
import logging
import argparse
from pathlib import Path
from io import BytesIO
from datetime import datetime
import time
import urllib.parse
import hmac
import hashlib
import uuid
import mimetypes

# Add the parent directory to sys.path to allow importing API modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import API keys from config
from api.config import OPENAI_API_KEY, XAI_API_KEY, ADDITIONAL_API_KEYS

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("PIL library is required. Please install with 'pip install Pillow'")
    sys.exit(1)

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("ReportLab library not found. PDF testing will be limited. Install with 'pip install reportlab'")

# Set up variables
API_HOST = "localhost"
API_PORT = "8435"
API_BASE_URL = f"http://api.assisted.space/v2"
TEST_IMAGE = "test_image.png"
TEST_PDF = "test_document.pdf"
OUTPUT_DIR = "test_results"

# Text formatting (ANSI color codes)
BOLD = "\033[1m"
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(OUTPUT_DIR, "test_api.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Available providers
PROVIDERS = {
    "anthropic": "Anthropic Claude",
    "mistral": "Mistral AI",
    "ollama": "Ollama (Local models)",
    "openai": "OpenAI",
    "cohere": "Cohere",
    "xai": "X.AI (Grok)",
    "coze": "Coze",
    "perplexity": "Perplexity AI",
    "mlx": "MLX",
    "gemini": "Google Gemini"
}

# Available research endpoints
RESEARCH_ENDPOINTS = {
    "semantic-scholar": "Semantic Scholar",
    "arxiv": "arXiv",
    "pubmed": "PubMed",
    "google-scholar": "Google Scholar"
}

def create_test_image():
    """Create a test image if it doesn't exist"""
    if not os.path.exists(TEST_IMAGE):
        logger.info(f"Creating test image...")
        try:
            # Create a new image with a white background
            img = Image.new('RGB', (400, 200), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw some shapes
            draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
            draw.ellipse([200, 50, 300, 150], fill='blue', outline='black')
            
            # Add text
            draw.text((150, 160), 'Test Image', fill='black')
            
            # Save the image
            img.save(TEST_IMAGE)
            logger.info("Test image created successfully")
        except Exception as e:
            logger.error(f"Error creating test image: {e}")
            logger.warning("Make sure PIL is installed with: pip install Pillow")
            sys.exit(1)

def create_test_pdf():
    """Create a test PDF document if it doesn't exist"""
    if os.path.exists(TEST_PDF):
        return
        
    logger.info(f"Creating test PDF document...")
    
    if not HAS_REPORTLAB:
        # Create a simple text file with .pdf extension if ReportLab is not available
        try:
            with open(TEST_PDF, 'w') as f:
                f.write("This is a test PDF document.\n\n")
                f.write("It contains text that can be processed by AI models.\n")
                f.write("This is a fallback because ReportLab is not installed.\n")
            logger.info("Created simple text file with .pdf extension (ReportLab not available)")
        except Exception as e:
            logger.error(f"Error creating simple PDF alternative: {e}")
        return
        
    try:
        # Create a proper PDF with ReportLab
        c = canvas.Canvas(TEST_PDF, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(72, height - 72, "Test PDF Document")
        
        # Add content
        c.setFont("Helvetica", 12)
        c.drawString(72, height - 100, "This is a test PDF document created for API testing.")
        c.drawString(72, height - 120, "It contains text that can be processed by AI models.")
        c.drawString(72, height - 140, "This document was created with ReportLab.")
        
        # Add a simple shape
        c.rect(72, height - 200, 100, 50, fill=0)
        
        # Add page number
        c.setFont("Helvetica", 10)
        c.drawString(width/2, 30, "Page 1")
        
        c.save()
        logger.info("Test PDF document created successfully")
    except Exception as e:
        logger.error(f"Error creating PDF document: {e}")
        logger.warning("Make sure ReportLab is installed with: pip install reportlab")

def print_header(title):
    """Print a formatted section header"""
    print(f"\n{BOLD}{BLUE}{title}{NC}")
    print(f"{BLUE}{'=' * 50}{NC}\n")
    logger.info(f"SECTION: {title}")

def print_result(status, message):
    """Print a test result with appropriate color"""
    if status:
        print(f"{GREEN}✓ {message}{NC}")
        logger.info(f"SUCCESS: {message}")
    else:
        print(f"{RED}✗ {message}{NC}")
        logger.error(f"FAILED: {message}")

def test_endpoint(endpoint, method="GET", data=None):
    """Test an API endpoint and save the response"""
    output_file = os.path.join(OUTPUT_DIR, endpoint.replace("/", "_") + ".json")
    
    logger.info(f"Testing {method} {API_BASE_URL}{endpoint}")
    print(f"{YELLOW}Testing {method} {API_BASE_URL}{endpoint}{NC}")
    
    try:
        headers = {"Content-Type": "application/json"}
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}")
        elif method == "DELETE":
            response = requests.delete(f"{API_BASE_URL}{endpoint}", headers=headers, data=data)
        else:  # POST or other methods
            response = requests.post(f"{API_BASE_URL}{endpoint}", headers=headers, data=data)
        
        if hasattr(response, 'text'):
            response_text = response.text
            # Save response to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            # Print the response to the console
            print(response_text)
            
            status = True
            
            # Return the response text for further processing
            return response_text
        else:
            status = False
            return None
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        status = False
        return None
    
    print_result(status, f"{method} {endpoint}")
    return None

def test_upload_endpoint(endpoint, provider, model, prompt="Generate descriptive alt text for this image"):
    """Test a file upload endpoint"""
    output_file = os.path.join(OUTPUT_DIR, f"{endpoint.replace('/', '_')}_{provider}.json")
    
    logger.info(f"Testing POST {API_BASE_URL}{endpoint} (provider: {provider}, model: {model})")
    print(f"{YELLOW}Testing POST {API_BASE_URL}{endpoint} (provider: {provider}, model: {model}){NC}")
    
    try:
        with open(TEST_IMAGE, 'rb') as img_file:
            files = {'image': img_file}
            data = {
                'prompt': prompt,
                'model': model,
                'stream': 'false'
            }
            response = requests.post(f"{API_BASE_URL}{endpoint}/{provider}", files=files, data=data)
        
        if hasattr(response, 'text'):
            response_text = response.text
            # Save response to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            # Print the response to the console
            print(response_text)
            
            status = True
        else:
            status = False
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        status = False
    
    print_result(status, f"POST {endpoint}/{provider}")
    return status

def test_coze_upload_endpoint():
    """Test Coze file upload endpoint"""
    output_file = os.path.join(OUTPUT_DIR, "upload_coze.json")
    
    logger.info("Testing Coze file upload using direct API call to api.coze.com")
    print(f"{YELLOW}Testing Coze file upload using direct API call to api.coze.com{NC}")
    
    try:
        # Create a temporary file for the upload
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        # Copy the test image to the temporary file
        with open(TEST_IMAGE, 'rb') as src, open(temp_file_path, 'wb') as dst:
            dst.write(src.read())
        
        # Use the exact same endpoint and auth token as in flask_chat_coze.py
        # Note: In a production environment, this token should be stored securely
        # and not hardcoded in the script
        COZE_AUTH_TOKEN = "pat_x43jhhVkypZ7CrKwnFwLGLdHOAegoEQqnhFO4kIqomnw6a3Zp4EaorAYfn6EMLz4"
        COZE_BOT_ID = "7462296933429346310"
        
        # Upload file using exact same endpoint as in flask_chat_coze.py
        logger.info("Uploading file directly to Coze API...")
        print(f"{YELLOW}Uploading file directly to Coze API...{NC}")
        
        headers = {
            "Authorization": f"Bearer {COZE_AUTH_TOKEN}"
        }
        
        with open(temp_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                "https://api.coze.com/v1/files/upload",
                headers=headers,
                files=files
            )
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        upload_response = response.text
        
        # Save response to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(upload_response)
        
        # Print the response for debugging
        print(f"{YELLOW}Response from Coze API: {NC}{upload_response}")
        logger.info(f"Response from Coze API: {upload_response}")
        
        # Extract file_id according to documented response format
        try:
            response_json = json.loads(upload_response)
            if response_json.get('code') == 0 and 'data' in response_json and 'id' in response_json['data']:
                file_id = response_json['data']['id']
                logger.info(f"Successfully uploaded file to Coze. File ID: {file_id}")
                print(f"{GREEN}Successfully uploaded file to Coze. File ID: {file_id}{NC}")
                print_result(True, "POST to api.coze.com/v1/files/upload")
                return file_id
            else:
                raise ValueError("Invalid response format")
        except Exception as e:
            logger.error(f"Failed to extract file_id from response: {e}")
            print(f"{RED}Failed to extract file_id from response: {e}{NC}")
            print_result(False, "POST to api.coze.com/v1/files/upload")
            return None
    except Exception as e:
        logger.error(f"Error uploading file to Coze: {e}")
        print(f"{RED}Error uploading file to Coze: {e}{NC}")
        print_result(False, "POST to api.coze.com/v1/files/upload")
        return None

def test_coze_alt_text(model, prompt="Generate descriptive alt text for this image"):
    """Test Coze alt text generation using file ID"""
    output_file = os.path.join(OUTPUT_DIR, "_alt_coze.json")
    
    logger.info(f"Testing Coze Alt Text Generation with model: {model}")
    print(f"{YELLOW}Testing Coze Alt Text Generation with model: {model}{NC}")
    
    # First upload the file to get a file_id using the direct API
    file_id = test_coze_upload_endpoint()
    
    if not file_id:
        logger.error("Failed to upload file for Coze alt text generation")
        print(f"{RED}Failed to upload file for Coze alt text generation{NC}")
        print_result(False, "Coze Alt Text Generation")
        return False
    
    # Now use the file_id to request alt text generation
    logger.info(f"Testing POST {API_BASE_URL}/chat/coze with file_id={file_id}")
    print(f"{YELLOW}Testing POST {API_BASE_URL}/chat/coze with file_id={file_id}{NC}")
    
    request_data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 500,
        "stream": False,
        "file_id": file_id
    }
    
    # Show the exact request we're sending
    logger.info(f"Request data: {json.dumps(request_data, indent=2)}")
    print(f"{YELLOW}Request data: {NC}")
    print(json.dumps(request_data, indent=2))
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{API_BASE_URL}/chat/coze",
            headers=headers,
            json=request_data
        )
        
        response_text = response.text
        
        # Save response to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        
        # Print the response to the console
        print(response_text)
        
        print_result(True, "POST /chat/coze (with file_id for alt text)")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        print_result(False, "POST /chat/coze (with file_id for alt text)")
        return False

def test_xai_alt_text():
    """Test X.AI alt text generation"""
    logger.info(f"Testing POST {API_BASE_URL}/alt/xai (provider: xai, model: grok-2-vision-1212)")
    print(f"{YELLOW}Testing POST {API_BASE_URL}/alt/xai (provider: xai, model: grok-2-vision-1212){NC}")
    
    output_file = os.path.join(OUTPUT_DIR, "_alt_xai.json")
    
    try:
        # Convert image to base64 inline to avoid form-data upload issues
        with open(TEST_IMAGE, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Send request with image data in the JSON payload instead of form upload
        headers = {"Content-Type": "application/json"}
        data = {
            "model": "grok-2-vision-1212",
            "prompt": "Describe what's in this image in detail",
            "image_data": image_base64
        }
        
        response = requests.post(
            f"{API_BASE_URL}/alt/xai",
            headers=headers,
            json=data
        )
        
        response_text = response.text
        
        # Save response to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        
        # Print the response to the console
        print(response_text)
        
        print_result(True, "POST /alt/xai")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        print_result(False, "POST /alt/xai")
        return False

def test_streaming_endpoint(endpoint, provider, model, data):
    """Test a streaming endpoint"""
    output_file = os.path.join(OUTPUT_DIR, f"{endpoint.replace('/', '_')}_{provider}_stream.txt")
    
    logger.info(f"Testing POST {API_BASE_URL}{endpoint}/{provider} (streaming)")
    print(f"{YELLOW}Testing POST {API_BASE_URL}{endpoint}/{provider} (streaming){NC}")
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{API_BASE_URL}{endpoint}/{provider}",
            headers=headers,
            json=json.loads(data) if isinstance(data, str) else data,
            stream=True
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in response.iter_content(decode_unicode=True):
                if chunk:
                    f.write(chunk)
                    print(chunk, end='')
                    logger.debug(f"Stream chunk: {chunk}")
            
            # Add a newline after streaming content
            print()
        
        print_result(True, f"POST {endpoint}/{provider} (streaming)")
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        print_result(False, f"POST {endpoint}/{provider} (streaming)")
        return False

def run_api_info_tests():
    """Run API info endpoint tests"""
    print_header("Testing API Info Endpoints")
    
    # Test 1: API Info Endpoint
    print_header("1. Testing API Info Endpoint")
    test_endpoint("/")
    
    # Test 2: Health Check Endpoint
    print_header("2. Testing Health Check Endpoint")
    test_endpoint("/health")

def run_models_tests(selected_providers=None):
    """Run models endpoint tests for specified providers"""
    providers = selected_providers or PROVIDERS.keys()
    
    print_header("Testing Models Endpoints")
    
    test_num = 1
    for provider in providers:
        print_header(f"{test_num}. Testing Models Endpoint - {PROVIDERS[provider]}")
        test_endpoint(f"/models/{provider}")
        test_num += 1

def run_chat_tests(streaming=False, selected_providers=None):
    """Run chat endpoint tests for specified providers"""
    providers = selected_providers or PROVIDERS.keys()
    
    test_type = "Streaming" if streaming else "Non-streaming"
    print_header(f"Testing Chat Endpoints ({test_type})")
    
    chat_configs = {
        "anthropic": {
            "model": "claude-3-haiku-20240307",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming
        },
        "mistral": {
            "model": "mistral-tiny",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming
        },
        "ollama": {
            "model": "llama3.2:1b",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming
        },
        "openai": {
            "model": "gpt-3.5-turbo-0125",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming
        },
        "cohere": {
            "model": "command-light",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming
        },
        "xai": {
            "model": "grok-2-1212",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming,
            "image_data": None
        },
        "coze": {
            "model": "7462296933429346310",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming
        },
        "gemini": {
            "model": "gemini-2.0-flash-exp",
            "prompt": "Write a short poem about AI" if streaming else "Hello, how are you today?",
            "max_tokens": 100,
            "stream": streaming,
            "image_data": None
        }
    }
    
    test_num = 1
    for provider in providers:
        print_header(f"{test_num}. Testing Chat Endpoint - {PROVIDERS[provider]} ({test_type})")
        
        if streaming:
            test_streaming_endpoint("/chat", provider, chat_configs[provider]["model"], chat_configs[provider])
        else:
            test_endpoint(f"/chat/{provider}", "POST", json.dumps(chat_configs[provider]))
        
        test_num += 1

def run_alt_text_tests(selected_providers=None):
    """Run alt text generation tests for specified providers"""
    # Define defaults for providers that support alt text
    alt_text_configs = {
        "anthropic": {
            "model": "claude-3-haiku-20240307",
            "prompt": "Generate descriptive alt text for this image"
        },
        "mistral": {
            "model": "pixtral-large-2411",
            "prompt": "Generate descriptive alt text for this image"
        },
        "ollama": [
            {
                "model": "coolhand/altllama:13b", 
                "prompt": "Describe this image in detail. What do you see?",
                "note": "Vision model"
            },
            {
                "model": "llama3.2:1b",
                "prompt": "Generate alt text for this image. Describe what you think it might contain.",
                "note": "Non-vision model"
            }
        ],
        "openai": {
            "model": "gpt-4o-mini",
            "prompt": "Generate detailed alt text for this image"
        },
        "xai": {
            "model": "grok-2-vision-1212",
            "prompt": "Describe what's in this image in detail"
        },
        "coze": {
            "model": "7462296933429346310",
            "prompt": "Describe this image in detail. Generate descriptive alt text for accessibility purposes."
        },
        "gemini": {
            "model": "gemini-2.0-flash-exp",
            "prompt": "Generate descriptive alt text for this image that follows accessibility best practices"
        }
    }
    
    # Filter to only selected providers
    providers = selected_providers or ["anthropic", "mistral", "ollama", "openai", "xai", "coze", "gemini"]
    
    # Remove providers that don't support alt text
    if "cohere" in providers:
        providers.remove("cohere")
    if "perplexity" in providers:
        providers.remove("perplexity")
    
    print_header("Testing Alt Text Generation")
    
    test_num = 1
    for provider in providers:
        if provider == "ollama":
            # Ollama has two models to test (vision and non-vision)
            for i, config in enumerate(alt_text_configs[provider]):
                print_header(f"{test_num}. Testing Alt Text Generation - Ollama ({config['note']})")
                test_upload_endpoint("/alt", "ollama", config["model"], config["prompt"])
                test_num += 1
        elif provider == "cohere":
            print_header(f"{test_num}. Testing Alt Text Generation - Cohere")
            print(f"{YELLOW}Note: Cohere does not support vision capabilities. Skipping alt text generation test for Cohere.{NC}")
            logger.info("Cohere vision test skipped (provider does not support vision)")
            with open(os.path.join(OUTPUT_DIR, "_alt_cohere_skipped.txt"), 'w') as f:
                f.write("Cohere vision test skipped")
            print(f"{BLUE}Cohere vision test skipped{NC}")
            print_result(True, "Skipped: Cohere vision test (provider does not support vision)")
            test_num += 1
        elif provider == "perplexity":
            print_header(f"{test_num}. Testing Alt Text Generation - Perplexity")
            print(f"{YELLOW}Note: Perplexity does not support vision capabilities. Skipping alt text generation test for Perplexity.{NC}")
            logger.info("Perplexity vision test skipped (provider does not support vision)")
            with open(os.path.join(OUTPUT_DIR, "_alt_perplexity_skipped.txt"), 'w') as f:
                f.write("Perplexity vision test skipped")
            print(f"{BLUE}Perplexity vision test skipped{NC}")
            print_result(True, "Skipped: Perplexity vision test (provider does not support vision)")
            test_num += 1
        elif provider == "xai":
            print_header(f"{test_num}. Testing Alt Text Generation - X.AI")
            test_xai_alt_text()
            test_num += 1
        elif provider == "coze":
            print_header(f"{test_num}. Testing Alt Text Generation - Coze")
            test_coze_alt_text(alt_text_configs[provider]["model"], alt_text_configs[provider]["prompt"])
            test_num += 1
        elif provider == "gemini":
            print_header(f"{test_num}. Testing Alt Text Generation - Gemini")
            test_upload_endpoint("/alt", "gemini", alt_text_configs[provider]["model"], alt_text_configs[provider]["prompt"])
            test_num += 1
        else:
            # For all other providers
            print_header(f"{test_num}. Testing Alt Text Generation - {PROVIDERS[provider]}")
            test_upload_endpoint("/alt", provider, alt_text_configs[provider]["model"], alt_text_configs[provider]["prompt"])
            test_num += 1

def run_tool_calling_tests(selected_providers=None):
    """Run tool calling tests for specified providers"""
    providers = selected_providers or PROVIDERS.keys()
    
    print_header("Testing Tool Calling")
    
    # Standard tool definition for weather
    weather_tool = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The unit of temperature to use"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    # Provider-specific configurations
    tool_configs = {
        "anthropic": {
            "model": "claude-3-opus-20240229",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200
        },
        "mistral": {
            "model": "mistral-small",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200
        },
        "ollama": {
            "model": "llama3.2:1b",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200
        },
        "openai": {
            "model": "gpt-4-0125-preview",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200
        },
        "cohere": {
            "model": "command-r-plus-08-2024",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200
        },
        "xai": {
            "model": "grok-2-1212",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200,
            "image_data": None
        },
        "coze": {
            "model": "7462296933429346310",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200
        },
        "gemini": {
            "model": "gemini-2.0-flash-exp",
            "prompt": "What is the weather in Seattle?",
            "tools": weather_tool,
            "max_tokens": 200,
            "image_data": None
        }
    }
    
    test_num = 1
    for provider in providers:
        print_header(f"{test_num}. Testing Tool Calling - {PROVIDERS[provider]}")
        test_endpoint(f"/tools/{provider}", "POST", json.dumps(tool_configs[provider]))
        test_num += 1

def run_clear_conversation_tests(selected_providers=None):
    """Run clear conversation tests for specified providers"""
    providers = selected_providers or PROVIDERS.keys()
    
    print_header("Testing Clear Conversation")
    
    test_num = 1
    for provider in providers:
        print_header(f"{test_num}. Testing Clear Conversation - {PROVIDERS[provider]}")
        test_endpoint(f"/chat/{provider}/clear", "POST", json.dumps({}))
        test_num += 1

def run_dreamwalker_tests():
    """Run tests for the Dreamwalker endpoints"""
    print_header("Testing Dreamwalker Framework")
    
    # Test 1: Start a search workflow
    print_header("1. Testing Dreamwalker Search Endpoint")
    test_data = json.dumps({
        "query": "What are the latest developments in quantum computing?",
        "workflow_type": "swarm",
        "model": "coolhand/camina-search:24b"
    })
    response = test_endpoint(f"/dreamwalker/search", "POST", test_data)
    
    # Extract workflow_id from the response if available
    workflow_id = None
    try:
        if response:
            response_data = json.loads(response)
            workflow_id = response_data.get("workflow_id")
            if workflow_id:
                print(f"Workflow ID: {workflow_id}")
                logger.info(f"Successfully created workflow with ID: {workflow_id}")
            else:
                logger.warning("No workflow_id found in response")
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
    
    # Test 2: Check workflow status
    if workflow_id:
        print_header("2. Testing Dreamwalker Status Endpoint")
        status_response = test_endpoint(f"/dreamwalker/status/{workflow_id}")
        
        # Parse the status response
        try:
            if status_response:
                status_data = json.loads(status_response)
                print(f"Status: {status_data.get('status')}")
                print(f"Progress: {status_data.get('progress')}%")
                print(f"Step description: {status_data.get('step_description')}")
                
                # Wait a bit for the workflow to progress
                print("Waiting 10 seconds for the workflow to progress...")
                time.sleep(10)
                
                # Check status again
                updated_status_response = test_endpoint(f"/dreamwalker/status/{workflow_id}")
                if updated_status_response:
                    updated_status_data = json.loads(updated_status_response)
                    
                    # Check if progress has been made
                    if updated_status_data.get('progress', 0) > status_data.get('progress', 0):
                        print(f"{GREEN}Progress has been made: {updated_status_data.get('progress')}%{NC}")
                        logger.info(f"Workflow progress increased from {status_data.get('progress')}% to {updated_status_data.get('progress')}%")
                    else:
                        print(f"{YELLOW}No progress detected. This might be normal if the workflow is still initializing.{NC}")
                        logger.warning(f"No progress detected. Initial: {status_data.get('progress')}%, Current: {updated_status_data.get('progress')}%")
        except Exception as e:
            logger.error(f"Error parsing status response: {e}")
    else:
        print(f"{RED}Skipping status check - no workflow ID available{NC}")
    
    # Test 3: Test with a different query
    print_header("3. Testing Dreamwalker Search with Different Query")
    test_data = json.dumps({
        "query": "Explain the impact of artificial intelligence on healthcare",
        "workflow_type": "swarm"
    })
    response = test_endpoint(f"/dreamwalker/search", "POST", test_data)
    
    # Extract workflow_id from the response
    second_workflow_id = None
    try:
        if response:
            response_data = json.loads(response)
            second_workflow_id = response_data.get("workflow_id")
            if second_workflow_id:
                print(f"Second Workflow ID: {second_workflow_id}")
                logger.info(f"Successfully created second workflow with ID: {second_workflow_id}")
    except Exception as e:
        logger.error(f"Error parsing response for second workflow: {e}")
    
    # Test 4: List workflows
    print_header("4. Testing Dreamwalker List Endpoint")
    list_response = test_endpoint(f"/dreamwalker/list")
    
    # Parse the list response
    try:
        if list_response:
            list_data = json.loads(list_response)
            workflow_count = len(list_data)
            print(f"Found {workflow_count} workflows")
            logger.info(f"Listed {workflow_count} workflows")
            
            # Check if our workflows are in the list
            workflow_ids_in_list = [w.get("workflow_id") for w in list_data]
            if workflow_id and workflow_id in workflow_ids_in_list:
                print(f"{GREEN}First workflow found in list{NC}")
                logger.info(f"First workflow {workflow_id} found in list")
            if second_workflow_id and second_workflow_id in workflow_ids_in_list:
                print(f"{GREEN}Second workflow found in list{NC}")
                logger.info(f"Second workflow {second_workflow_id} found in list")
    except Exception as e:
        logger.error(f"Error parsing list response: {e}")
    
    # Test 5: List workflows with filters
    print_header("5. Testing Dreamwalker List Endpoint with Filters")
    filtered_list_response = test_endpoint(f"/dreamwalker/list?status=running&limit=5")
    
    # Parse the filtered list response
    try:
        if filtered_list_response:
            filtered_list_data = json.loads(filtered_list_response)
            filtered_workflow_count = len(filtered_list_data)
            print(f"Found {filtered_workflow_count} running workflows (limit 5)")
            logger.info(f"Listed {filtered_workflow_count} running workflows (limit 5)")
    except Exception as e:
        logger.error(f"Error parsing filtered list response: {e}")
    
    # Test 6: Cancel workflows
    if workflow_id:
        print_header("6. Testing Dreamwalker Cancel Endpoint - First Workflow")
        cancel_response = test_endpoint(f"/dreamwalker/cancel/{workflow_id}", "DELETE")
        
        # Parse the cancel response
        try:
            if cancel_response:
                cancel_data = json.loads(cancel_response)
                if cancel_data.get("status") == "cancelled":
                    print(f"{GREEN}Successfully cancelled workflow{NC}")
                    logger.info(f"Successfully cancelled workflow {workflow_id}")
                else:
                    print(f"{YELLOW}Workflow not cancelled. Status: {cancel_data.get('status')}{NC}")
                    logger.warning(f"Workflow {workflow_id} not cancelled. Status: {cancel_data.get('status')}")
        except Exception as e:
            logger.error(f"Error parsing cancel response: {e}")
    else:
        print(f"{RED}Skipping cancel test for first workflow - no workflow ID available{NC}")
    
    if second_workflow_id:
        print_header("7. Testing Dreamwalker Cancel Endpoint - Second Workflow")
        cancel_response = test_endpoint(f"/dreamwalker/cancel/{second_workflow_id}", "DELETE")
        
        # Parse the cancel response
        try:
            if cancel_response:
                cancel_data = json.loads(cancel_response)
                if cancel_data.get("status") == "cancelled":
                    print(f"{GREEN}Successfully cancelled second workflow{NC}")
                    logger.info(f"Successfully cancelled second workflow {second_workflow_id}")
                else:
                    print(f"{YELLOW}Second workflow not cancelled. Status: {cancel_data.get('status')}{NC}")
                    logger.warning(f"Second workflow {second_workflow_id} not cancelled. Status: {cancel_data.get('status')}")
        except Exception as e:
            logger.error(f"Error parsing cancel response for second workflow: {e}")
    else:
        print(f"{RED}Skipping cancel test for second workflow - no workflow ID available{NC}")
    
    # Test 8: Cleanup workflows
    print_header("8. Testing Dreamwalker Cleanup Endpoint")
    cleanup_response = test_endpoint(f"/dreamwalker/cleanup", "DELETE")
    
    # Parse the cleanup response
    try:
        if cleanup_response and not cleanup_response.startswith('<!doctype html>'):
            cleanup_data = json.loads(cleanup_response)
            removed_count = cleanup_data.get("removed_count", 0)
            remaining_count = cleanup_data.get("remaining_count", 0)
            print(f"Removed {removed_count} workflows, {remaining_count} remaining")
            logger.info(f"Cleanup removed {removed_count} workflows, {remaining_count} remaining")
        else:
            print(f"{YELLOW}Cleanup endpoint returned HTML or empty response. This might indicate a method not allowed error.{NC}")
            logger.warning("Cleanup endpoint returned HTML or empty response")
    except Exception as e:
        logger.error(f"Error parsing cleanup response: {e}")
    
    # Test 9: Test with invalid workflow ID
    print_header("9. Testing Dreamwalker Status with Invalid Workflow ID")
    invalid_id = "invalid-workflow-id-12345"
    invalid_response = test_endpoint(f"/dreamwalker/status/{invalid_id}")
    
    # Check if we got a 404 error
    try:
        if invalid_response:
            invalid_data = json.loads(invalid_response)
            if "error" in invalid_data:
                print(f"{GREEN}Correctly received error for invalid workflow ID{NC}")
                logger.info(f"Correctly received error for invalid workflow ID: {invalid_data.get('error')}")
            else:
                print(f"{RED}Did not receive expected error for invalid workflow ID{NC}")
                logger.warning(f"Did not receive expected error for invalid workflow ID")
    except Exception as e:
        logger.error(f"Error parsing invalid ID response: {e}")
    
    # Test 10: Test with invalid workflow type
    print_header("10. Testing Dreamwalker Search with Invalid Workflow Type")
    invalid_type_data = json.dumps({
        "query": "What is quantum computing?",
        "workflow_type": "invalid_type"
    })
    invalid_type_response = test_endpoint(f"/dreamwalker/search", "POST", invalid_type_data)
    
    # Check if we got an error
    try:
        if invalid_type_response:
            invalid_type_data = json.loads(invalid_type_response)
            if "error" in invalid_type_data:
                print(f"{GREEN}Correctly received error for invalid workflow type{NC}")
                logger.info(f"Correctly received error for invalid workflow type: {invalid_type_data.get('error')}")
            else:
                print(f"{RED}Did not receive expected error for invalid workflow type{NC}")
                logger.warning(f"Did not receive expected error for invalid workflow type")
    except Exception as e:
        logger.error(f"Error parsing invalid type response: {e}")
    
    print_header("Dreamwalker Tests Completed")
    print(f"{BOLD}Note: Some tests may show as failed if the server is not running or if the Dreamwalker framework is not properly configured.{NC}")
    print(f"{BOLD}Check the logs for more details.{NC}")

def run_research_tests(selected_endpoints=None):
    """Run tests for the Research endpoints"""
    endpoints = selected_endpoints or RESEARCH_ENDPOINTS.keys()
    
    print_header("Testing Research Endpoints")
    
    test_num = 1
    for endpoint in endpoints:
        print_header(f"{test_num}. Testing Research Endpoint - {RESEARCH_ENDPOINTS[endpoint]}")
        
        # Test GET endpoint
        query = "machine learning"
        if endpoint == "arxiv":
            get_endpoint = f"/research/{endpoint}?query={urllib.parse.quote(query)}&max_results=2"
            if endpoint == "arxiv":
                get_endpoint += "&category=cs.AI"
        elif endpoint == "pubmed":
            get_endpoint = f"/research/{endpoint}?query={urllib.parse.quote('covid vaccination')}&max_results=2"
        elif endpoint == "semantic-scholar":
            get_endpoint = f"/research/{endpoint}?query={urllib.parse.quote(query)}&limit=2&year=2023"
        else:  # google-scholar
            get_endpoint = f"/research/{endpoint}?query={urllib.parse.quote('natural language processing')}&max_results=2"
            
        test_endpoint(get_endpoint)
        
        # Test POST endpoint with JSON body
        post_data = None
        if endpoint == "arxiv":
            post_data = json.dumps({
                "query": "quantum computing",
                "max_results": 2,
                "category": "quant-ph",
                "sort_by": "relevance",
                "sort_order": "descending"
            })
        elif endpoint == "pubmed":
            post_data = json.dumps({
                "query": "covid vaccination",
                "max_results": 2,
                "sort": "relevance",
                "date_range": "2022/01/01:2023/01/01"
            })
        elif endpoint == "semantic-scholar":
            post_data = json.dumps({
                "query": "machine learning",
                "limit": 2,
                "fields": "url,abstract,authors,title,venue,year",
                "fieldsOfStudy": "Computer Science",
                "year": "2023"
            })
        else:  # google-scholar
            post_data = json.dumps({
                "query": "natural language processing",
                "max_results": 2
            })
            
        test_endpoint(f"/research/{endpoint}", "POST", post_data)
        test_num += 1

def test_file_upload_endpoint(provider, model, file_paths, prompt="Analyze this file and summarize its contents"):
    """Test a file upload endpoint"""
    # Convert to list if a single file path is provided
    if isinstance(file_paths, str):
        file_paths = [file_paths]
        
    # Create a descriptive name for the output file based on file types
    file_types = "_".join([os.path.splitext(os.path.basename(path))[1][1:] for path in file_paths])
    output_file = os.path.join(OUTPUT_DIR, f"file_upload_{provider}_{file_types}.json")
    
    logger.info(f"Testing POST {API_BASE_URL}/chat/{provider} with {len(file_paths)} files: {file_paths} (model: {model})")
    print(f"{YELLOW}Testing POST {API_BASE_URL}/chat/{provider} with {len(file_paths)} files (model: {model}){NC}")
    
    try:
        # For OpenAI, we'll use the dedicated endpoint
        if provider == "openai":
            data = {
                'prompt': prompt,
                'model': model,
                'stream': 'false'
            }
            
            # Print request details for debugging
            print(f"{YELLOW}Sending files to {API_BASE_URL}/chat/openai:{NC}")
            for file_path in file_paths:
                print(f"  - {os.path.basename(file_path)} ({os.path.getsize(file_path)} bytes)")
            
            # Important: Read files into memory first and keep handles open
            file_tuples = []
            file_handles = []
            
            try:
                # Open all files first
                for file_path in file_paths:
                    # Open the file
                    f = open(file_path, 'rb')
                    file_handles.append(f)
                    # Create the tuple with file already open
                    file_tuples.append(
                        ('file', (os.path.basename(file_path), f, 'application/octet-stream'))
                    )
                
                # Make the request with all files open
                response = requests.post(
                    f"{API_BASE_URL}/chat/openai", 
                    data=data,
                    files=file_tuples
                )
            finally:
                # Close all file handles after request is complete
                for f in file_handles:
                    f.close()
        else:
            # For other providers that might not support direct file upload yet
            print(f"{YELLOW}Note: File upload for {provider} might not be fully implemented yet.{NC}")
            return False
        
        if hasattr(response, 'text'):
            response_text = response.text
            # Save response to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            
            # Print the response to the console
            print(response_text)
            
            # Check if there was an error in the response
            try:
                response_json = json.loads(response_text)
                if "error" in response_json:
                    print(f"{RED}Error in response: {response_json['error']}{NC}")
                    logger.error(f"Error in response: {response_json['error']}")
                    status = False
                else:
                    status = True
            except json.JSONDecodeError:
                # If it's not JSON, just check for success status code
                status = response.status_code == 200
        else:
            status = False
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        status = False
    
    print_result(status, f"POST file upload to /chat/{provider}")
    return status

def test_openai_responses_endpoint(model, file_paths, prompt="Please analyze this document and summarize the key points.", web_search=False, file_search=False, tools=None, computer_use=False):
    """
    Test the OpenAI Responses API endpoint for document processing.
    
    Args:
        model (str): The model to use for processing.
        file_paths (list): List of paths to document files.
        prompt (str): The prompt to use for processing the document.
        web_search (bool): Whether to enable web search.
        file_search (bool): Whether to enable file search.
        tools (list): List of tools to use for function calling.
        computer_use (bool): Whether to enable computer use.
        
    Returns:
        dict: The response from the API.
    """
    print(f"Testing POST {API_BASE_URL}/responses with {len(file_paths)} files (model: {model})")
    print(f"Sending documents to {API_BASE_URL}/responses:")
    
    try:
        # Prepare the files for upload
        files = []
        for file_path in file_paths:
            file_size = os.path.getsize(file_path)
            print(f"  - {os.path.basename(file_path)} ({file_size} bytes)")
            files.append(
                ('file', (os.path.basename(file_path), open(file_path, 'rb'), get_mime_type(file_path)))
            )

        # Prepare the form data
        form_data = {
            'model': model,
            'prompt': prompt,
            'max_tokens': 1024,
            'temperature': 0.7,
        }
        
        # Add web search if enabled
        if web_search:
            form_data['web_search'] = True
        
        # Add file search if enabled
        if file_search:
            form_data['file_search'] = True
        
        # Add tools if provided
        if tools:
            form_data['tools'] = json.dumps(tools)
        
        # Add computer use if enabled
        if computer_use:
            form_data['computer_use'] = True
        
        # Make the request
        response = requests.post(
            f"{API_BASE_URL}/responses",
            files=files,
            data=form_data,
            timeout=30
        )
        
        # Print the response content
        print(response.text)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print_result(True, "POST to /responses endpoint")
            
            # If we got a response_id, try to retrieve the response
            if 'response_id' in data:
                response_id = data['response_id']
                status = data.get('status', '')
                
                print(f"\nGot response_id: {response_id}, status: {status}")
                
                if status != "completed":
                    print("Response is still processing. Waiting a moment and then retrieving...")
                    time.sleep(5)  # Wait a moment before trying to retrieve
                    
                    # Retrieve the response
                    retrieve_url = f"{API_BASE_URL}/responses/{response_id}"
                    print(f"Retrieving response from: {retrieve_url}")
                    
                    retrieve_response = requests.get(retrieve_url, timeout=30)
                    print(retrieve_response.text)
                    
                    if retrieve_response.status_code == 200:
                        print_result(True, f"GET from /responses/{response_id}")
                        retrieve_data = retrieve_response.json()
                        
                        if 'content' in retrieve_data:
                            print("\nContent retrieved successfully!")
                            return retrieve_data
                        else:
                            print(f"\nNo content available yet. Status: {retrieve_data.get('status', 'unknown')}")
                            return retrieve_data
                    else:
                        print_result(False, f"GET from /responses/{response_id}")
                        return {"error": f"Failed to retrieve response: {retrieve_response.text}"}
                else:
                    # If the response was completed immediately
                    print("\nResponse was completed immediately!")
                    return data
            else:
                # If no response_id was returned but the request was successful
                return data
        else:
            print_result(False, "POST to /responses endpoint")
            return {"error": f"Request failed with status code {response.status_code}: {response.text}"}
    
    except Exception as e:
        print_result(False, f"Error in test_openai_responses_endpoint: {str(e)}")
        return {"error": str(e)}
    finally:
        # Close all opened files
        for file_tuple in files:
            try:
                file_tuple[2].close()
            except:
                pass

def run_openai_responses_tests():
    """Run tests for OpenAI Responses API with additional capabilities."""
    print_header("Testing OpenAI Responses API with Advanced Capabilities")
    
    pdf_path = os.path.join(os.path.dirname(__file__), "test_document.pdf")
    text_path = os.path.join(os.path.dirname(__file__), "test_document.txt")
    
    # Test 1: Basic PDF processing
    print_header("1. Basic PDF Processing")
    test_openai_responses_endpoint("gpt-4o-mini", [pdf_path])
    
    # Test 2: Web Search Enabled
    print_header("2. Web Search Enabled")
    test_openai_responses_endpoint(
        "gpt-4o-mini", 
        [text_path],
        prompt="Summarize recent news related to this document.",
        web_search=True
    )
    
    # Test 3: File Search Enabled
    print_header("3. File Search Enabled")
    test_openai_responses_endpoint(
        "gpt-4o-mini", 
        [pdf_path],
        prompt="Find and summarize relevant information from this document.",
        file_search=True
    )
    
    # Test 4: Function Calling Enabled
    print_header("4. Function Calling Enabled")
    weather_tool = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    test_openai_responses_endpoint(
        "gpt-4o-mini", 
        [text_path],
        prompt="What's the weather like in Seattle?",
        tools=weather_tool
    )
    
    # Test 5: Computer Use Enabled
    print_header("5. Computer Use Enabled")
    test_openai_responses_endpoint(
        "gpt-4o-mini", 
        [pdf_path],
        prompt="Analyze this document and perform any necessary calculations.",
        computer_use=True
    )

def run_file_upload_tests(selected_providers=None):
    """Run file upload tests for specified providers"""
    # Filter to only providers that might support file uploads
    providers = selected_providers or ["openai"]
    
    # Make sure we have the test files
    create_test_image()
    create_test_pdf()
    
    print_header("Testing File Upload Capabilities")
    
    test_num = 1
    for provider in providers:
        if provider == "openai":
            # Test 1: Image upload
            print_header(f"{test_num}. Testing Image Upload - OpenAI")
            test_file_upload_endpoint(
                "openai", 
                "gpt-4o-mini", 
                TEST_IMAGE, 
                "Describe what's in this image in detail"
            )
            test_num += 1
            
            # Test 2: PDF upload
            print_header(f"{test_num}. Testing PDF Upload - OpenAI")
            test_file_upload_endpoint(
                "openai", 
                "gpt-4o-mini", 
                TEST_PDF, 
                "Summarize the contents of this PDF document"
            )
            test_num += 1
            
            # Test 3: Multiple files (Image + PDF)
            print_header(f"{test_num}. Testing Multiple File Upload - OpenAI")
            test_file_upload_endpoint(
                "openai", 
                "gpt-4o-mini", 
                [TEST_IMAGE, TEST_PDF], 
                "Analyze these files and describe what you see in both the image and the PDF"
            )
            test_num += 1
        else:
            print_header(f"{test_num}. Testing File Upload - {PROVIDERS[provider]}")
            print(f"{YELLOW}Note: File upload for {provider} is not implemented yet.{NC}")
            logger.info(f"{provider} file upload test skipped (not implemented)")
            test_num += 1

def test_image_generation(provider, model=None, prompt="A beautiful sunset over mountains with a lake"):
    """Test image generation for a provider"""
    output_file = os.path.join(OUTPUT_DIR, f"image_generation_{provider}.json")
    
    # Default models for each provider
    default_models = {
        "openai": "dall-e-3",
        "gemini": "gemini-2.0-flash-exp-image-generation",
        "xai": "grok-2-image"
    }
    
    # Use default model if not specified
    if not model:
        model = default_models.get(provider, "")
    
    logger.info(f"Testing POST {API_BASE_URL}/generate/{provider} (model: {model})")
    print(f"{YELLOW}Testing POST {API_BASE_URL}/generate/{provider} (model: {model}){NC}")
    print(f"{YELLOW}Prompt: {prompt}{NC}")
    
    try:
        # Prepare request data
        data = {
            "prompt": prompt,
            "model": model,
            "n": 1,
            "size": "1024x1024",
            "response_format": "url"
        }
        
        # Add provider-specific parameters
        if provider == "xai":
            data["seed"] = 42  # Example seed for deterministic output
            # Get API key from environment variable if available
            xai_api_key = os.environ.get("XAI_API_KEY")
            if xai_api_key:
                data["api_key"] = xai_api_key
                print(f"{YELLOW}Using X.AI API key from environment variable{NC}")
            elif "XAI_API_KEY" in globals():
                data["api_key"] = XAI_API_KEY
                print(f"{YELLOW}Using X.AI API key from global variable{NC}")
            else:
                print(f"{YELLOW}No X.AI API key found{NC}")
        
        # Add quality and style for OpenAI
        if provider == "openai":
            data["quality"] = "standard"
            data["style"] = "vivid"
            # Get API key from environment variable if available
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if openai_api_key:
                data["api_key"] = openai_api_key
                print(f"{YELLOW}Using OpenAI API key from environment variable{NC}")
            elif "OPENAI_API_KEY" in globals():
                data["api_key"] = OPENAI_API_KEY
                print(f"{YELLOW}Using OpenAI API key from global variable{NC}")
            else:
                print(f"{YELLOW}No OpenAI API key found{NC}")
        
        # Add Gemini API key if available
        if provider == "gemini":
            gemini_api_key = os.environ.get("GOOGLE_API_KEY")
            if gemini_api_key:
                data["api_key"] = gemini_api_key
                print(f"{YELLOW}Using Gemini API key from environment variable{NC}")
            elif "GOOGLE_API_KEY" in globals():
                data["api_key"] = GOOGLE_API_KEY
                print(f"{YELLOW}Using Gemini API key from global variable{NC}")
            else:
                print(f"{YELLOW}No Gemini API key found{NC}")
        
        # Log request data (excluding API keys)
        safe_data = data.copy()
        if "api_key" in safe_data:
            safe_data["api_key"] = "***"
        logger.info(f"Request data: {json.dumps(safe_data)}")
        print(f"{YELLOW}Request data: {json.dumps(safe_data, indent=2)}{NC}")
        
        # Set headers
        headers = {"Content-Type": "application/json"}
        
        # Send request
        print(f"{YELLOW}Sending request to {API_BASE_URL}/generate/{provider}...{NC}")
        response = requests.post(
            f"{API_BASE_URL}/generate/{provider}",
            headers=headers,
            json=data
        )
        
        # Process response
        print(f"{YELLOW}Response status code: {response.status_code}{NC}")
        
        try:
            response_json = response.json()
            
            # Save response to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(response_json, f, indent=2)
            
            if response.status_code == 200:
                # Print success message
                if "data" in response_json and isinstance(response_json["data"], list) and len(response_json["data"]) > 0:
                    image_count = len(response_json["data"])
                    print(f"{GREEN}Successfully generated {image_count} image(s){NC}")
                    
                    for i, img_data in enumerate(response_json["data"]):
                        print(f"{GREEN}Image {i+1}:{NC}")
                        if "url" in img_data:
                            url = img_data["url"]
                            print(f"  URL: {url[:60]}..." if len(url) > 60 else f"  URL: {url}")
                        if "b64_json" in img_data:
                            print(f"  Base64 data: {len(img_data['b64_json'])} characters")
                        if "revised_prompt" in img_data:
                            print(f"  Revised prompt: {img_data['revised_prompt']}")
                    
                    print_result(True, f"POST /generate/{provider}")
                    return True
                else:
                    print(f"{YELLOW}Response received but format unexpected: {json.dumps(response_json)[:200]}...{NC}")
                    logger.warning(f"Response format unexpected: {json.dumps(response_json)}")
                    print_result(False, f"POST /generate/{provider}")
                    return False
            else:
                # Handle error response
                error_msg = response_json.get("error", "Unknown error")
                logger.error(f"Error response ({response.status_code}): {error_msg}")
                print(f"{RED}Error ({response.status_code}): {error_msg}{NC}")
                print_result(False, f"POST /generate/{provider}")
                return False
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response: {response.text}")
            print(f"{RED}Invalid JSON response: {response.text[:200]}...{NC}")
            print_result(False, f"POST /generate/{provider}")
            return False
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"{RED}Error: {e}{NC}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"{RED}{traceback.format_exc()}{NC}")
        print_result(False, f"POST /generate/{provider}")
        return False

def print_test_summary():
    """Print a summary of the test results"""
    print_header("Test Summary")
    print(f"{BOLD}All test results have been saved to the '{OUTPUT_DIR}' directory.{NC}")
    print(f"{BOLD}Check the JSON files for detailed responses.{NC}")
    print(f"\n{BOLD}Test Coverage Highlights:{NC}")
    print("• API endpoints for all providers (Anthropic, Mistral, Ollama, OpenAI, X.AI, Cohere, Coze, Perplexity, MLX)")
    print("• Chat capabilities (streaming and non-streaming)")
    print("• Alt text generation with both vision and non-vision models")
    print("• Tool calling functionality")
    print("• Conversation management")
    print("• Dreamwalker framework for advanced multi-step AI workflows")
    print("  - Search workflow with query expansion")
    print("  - Workflow status tracking and management")
    print("  - Workflow cancellation and cleanup")
    print("• Web Search capabilities")
    print("  - DuckDuckGo search integration")
    print("• Academic Research capabilities")
    print("  - Semantic Scholar integration")
    print("  - arXiv integration")
    print("  - PubMed integration")
    print("  - Google Scholar integration (via Semantic Scholar)\n")
    print(f"\n{GREEN}Testing completed!{NC}\n")
    logger.info("Test summary displayed - Testing completed")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test the Camina Chat API")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--info", action="store_true", help="Run API info tests")
    parser.add_argument("--models", action="store_true", help="Run models tests")
    parser.add_argument("--chat", action="store_true", help="Run chat tests (non-streaming)")
    parser.add_argument("--stream", action="store_true", help="Run streaming chat tests")
    parser.add_argument("--alt", action="store_true", help="Run alt text generation tests")
    parser.add_argument("--tools", action="store_true", help="Run tool calling tests")
    parser.add_argument("--clear", action="store_true", help="Run clear conversation tests")
    parser.add_argument("--dreamwalker", action="store_true", help="Run Dreamwalker tests")
    parser.add_argument("--web", action="store_true", help="Run Web Search tests")
    parser.add_argument("--research", action="store_true", help="Run Research tests")
    parser.add_argument("--file-upload", action="store_true", help="Run File Upload tests")
    parser.add_argument("--responses", action="store_true", help="Run OpenAI Responses API tests")
    parser.add_argument("--image-generation", action="store_true", help="Run Image Generation tests")
    parser.add_argument("--image-providers", nargs="+", choices=["openai", "gemini", "xai"],
                        help="Specify which image generation providers to test (space-separated list)")
    parser.add_argument("--providers", nargs="+", choices=PROVIDERS.keys(), 
                        help="Specify which providers to test (space-separated list)")
    parser.add_argument("--research-endpoints", nargs="+", choices=RESEARCH_ENDPOINTS.keys(),
                        help="Specify which research endpoints to test (space-separated list)")
    return parser.parse_args()

def main():
    """Main function to run API tests"""
    # Create test files
    create_test_image()
    create_test_pdf()
    
    # Parse command line arguments
    args = parse_args()
    
    # If command-line arguments are provided, run specific tests
    if any([args.all, args.info, args.models, args.chat, args.stream, args.alt, args.tools, args.clear, args.dreamwalker, args.web, args.research, args.file_upload, args.responses, args.image_generation]):
        if args.all:
            logger.info("Running all tests based on command line argument")
            run_api_info_tests()
            run_models_tests(args.providers)
            run_chat_tests(streaming=False, selected_providers=args.providers)
            run_chat_tests(streaming=True, selected_providers=args.providers)
            run_alt_text_tests(args.providers)
            run_tool_calling_tests(args.providers)
            run_clear_conversation_tests(args.providers)
            run_dreamwalker_tests()
            run_web_search_tests()
            run_research_tests(args.research_endpoints)
            run_file_upload_tests(args.providers)
            run_openai_responses_tests()
            run_image_generation_tests(args.image_providers)
            print_test_summary()
        else:
            if args.info:
                logger.info("Running API info tests based on command line argument")
                run_api_info_tests()
            if args.models:
                logger.info(f"Running models tests for {args.providers or 'all providers'}")
                run_models_tests(args.providers)
            if args.chat:
                logger.info(f"Running chat tests for {args.providers or 'all providers'}")
                run_chat_tests(streaming=False, selected_providers=args.providers)
            if args.stream:
                logger.info(f"Running streaming chat tests for {args.providers or 'all providers'}")
                run_chat_tests(streaming=True, selected_providers=args.providers)
            if args.alt:
                logger.info(f"Running alt text generation tests for {args.providers or 'all providers'}")
                run_alt_text_tests(args.providers)
            if args.tools:
                logger.info(f"Running tool calling tests for {args.providers or 'all providers'}")
                run_tool_calling_tests(args.providers)
            if args.clear:
                logger.info(f"Running clear conversation tests for {args.providers or 'all providers'}")
                run_clear_conversation_tests(args.providers)
            if args.dreamwalker:
                logger.info("Running Dreamwalker tests")
                run_dreamwalker_tests()
            if args.web:
                logger.info("Running Web Search tests")
                run_web_search_tests()
            if args.research:
                logger.info(f"Running Research tests for {args.research_endpoints or 'all endpoints'}")
                run_research_tests(args.research_endpoints)
            if args.file_upload:
                logger.info(f"Running File Upload tests for {args.providers or 'all providers'}")
                run_file_upload_tests(args.providers)
            if args.responses:
                logger.info("Running OpenAI Responses API tests")
                run_openai_responses_tests()
            if args.image_generation:
                logger.info(f"Running Image Generation tests for {args.image_providers or 'default providers'}")
                run_image_generation_tests(args.image_providers)
            print_test_summary()
    else:
        # No specific tests mentioned, show interactive menu
        show_main_menu()

def get_mime_type(file_path):
    """
    Get the MIME type of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The MIME type of the file
    """
    # Initialize mimetypes if needed
    if not mimetypes.inited:
        mimetypes.init()
        
    # Get mime type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Default to application/octet-stream if type couldn't be determined
    if mime_type is None:
        mime_type = "application/octet-stream"
        
    return mime_type

def select_image_providers():
    """Let the user select which image generation providers to test"""
    print_header("Select Image Generation Providers to Test")
    print("Available image providers:")
    
    IMAGE_PROVIDERS = {
        "openai": "OpenAI (DALL-E)",
        "gemini": "Google Gemini",
        "xai": "X.AI (Grok)"
    }
    
    for i, (key, name) in enumerate(IMAGE_PROVIDERS.items(), 1):
        print(f"{i}. {name} ({key})")
    
    print(f"{len(IMAGE_PROVIDERS) + 1}. All image providers")
    print(f"{len(IMAGE_PROVIDERS) + 2}. Return to main menu")
    
    while True:
        try:
            choice = input("\nEnter the number(s) of the image providers to test (comma-separated): ")
            
            # Return to main menu
            if choice.strip() == str(len(IMAGE_PROVIDERS) + 2):
                return []
            
            # All providers
            if choice.strip() == str(len(IMAGE_PROVIDERS) + 1):
                return list(IMAGE_PROVIDERS.keys())
            
            # Parse comma-separated list
            selected_indices = [int(x.strip()) for x in choice.split(",")]
            if any(idx < 1 or idx > len(IMAGE_PROVIDERS) for idx in selected_indices):
                print(f"{RED}Invalid selection. Please enter numbers between 1 and {len(IMAGE_PROVIDERS)}.{NC}")
                continue
            
            # Convert indices to provider keys
            selected_providers = [list(IMAGE_PROVIDERS.keys())[idx-1] for idx in selected_indices]
            
            # Confirm selection
            print(f"\nYou selected: {', '.join([IMAGE_PROVIDERS[p] for p in selected_providers])}")
            confirm = input("Is this correct? (y/n): ").lower()
            if confirm.startswith('y'):
                return selected_providers
        except (ValueError, IndexError) as e:
            print(f"{RED}Invalid input: {e}. Please try again.{NC}")

def show_main_menu():
    """Display the main menu and get user selection"""
    while True:
        print_header("Camina Chat API Testing Script")
        print("Select a test category:")
        print("1. API Info Tests (endpoints, health)")
        print("2. Models Tests")
        print("3. Chat Tests (non-streaming)")
        print("4. Chat Tests (streaming)")
        print("5. Alt Text Generation Tests")
        print("6. Tool Calling Tests")
        print("7. Clear Conversation Tests")
        print("8. Dreamwalker Tests")
        print("9. Web Search Tests")
        print("10. Research Tests")
        print("11. File Upload Tests")
        print("12. OpenAI Responses API Tests")
        print("13. Image Generation Tests")
        print("14. Run All Tests")
        print("15. Exit")
        
        try:
            choice = input("\nEnter your choice (1-15): ")
            
            if choice == "1":
                run_api_info_tests()
            elif choice == "2":
                providers = select_providers()
                if providers:
                    run_models_tests(providers)
            elif choice == "3":
                providers = select_providers()
                if providers:
                    run_chat_tests(streaming=False, selected_providers=providers)
            elif choice == "4":
                providers = select_providers()
                if providers:
                    run_chat_tests(streaming=True, selected_providers=providers)
            elif choice == "5":
                providers = select_providers()
                if providers:
                    run_alt_text_tests(providers)
            elif choice == "6":
                providers = select_providers()
                if providers:
                    run_tool_calling_tests(providers)
            elif choice == "7":
                providers = select_providers()
                if providers:
                    run_clear_conversation_tests(providers)
            elif choice == "8":
                run_dreamwalker_tests()
            elif choice == "9":
                run_web_search_tests()
            elif choice == "10":
                endpoints = select_research_endpoints()
                if endpoints:
                    run_research_tests(endpoints)
            elif choice == "11":
                providers = select_providers()
                if providers:
                    run_file_upload_tests(providers)
            elif choice == "12":
                run_openai_responses_tests()
            elif choice == "13":
                providers = select_providers()
                if providers:
                    run_image_generation_tests(providers)
            elif choice == "14":
                # Run all tests
                print_header("Running All Tests")
                confirm = input(f"{YELLOW}Warning: This will run all tests, including potentially expensive ones like image generation, alt text generation and Dreamwalker workflows. Continue? (y/n): {NC}").lower()
                if confirm.startswith('y'):
                    run_api_info_tests()
                    run_models_tests()
                    run_chat_tests(streaming=False)
                    run_chat_tests(streaming=True)
                    run_alt_text_tests()
                    run_tool_calling_tests()
                    run_clear_conversation_tests()
                    run_dreamwalker_tests()
                    run_web_search_tests()
                    run_research_tests()
                    run_file_upload_tests()
                    run_openai_responses_tests()
                    run_image_generation_tests(["gemini"])  # Default to just Gemini which is known to work
                    print_test_summary()
            elif choice == "15":
                print("Exiting...")
                break
            else:
                print(f"{RED}Invalid choice. Please enter a number between 1 and 15.{NC}")
            
            # Pause before showing the menu again
            input("\nPress Enter to return to the main menu...")
        except Exception as e:
            logger.error(f"Error in menu handling: {e}")
            print(f"{RED}An error occurred: {e}{NC}")
            input("\nPress Enter to return to the main menu...")

def select_providers():
    """Let the user select which providers to test"""
    print_header("Select Providers to Test")
    print("Available providers:")
    
    for i, (key, name) in enumerate(PROVIDERS.items(), 1):
        print(f"{i}. {name} ({key})")
    
    print(f"{len(PROVIDERS) + 1}. All providers")
    print(f"{len(PROVIDERS) + 2}. Return to main menu")
    
    while True:
        try:
            choice = input("\nEnter the number(s) of the providers to test (comma-separated): ")
            
            # Return to main menu
            if choice.strip() == str(len(PROVIDERS) + 2):
                return []
            
            # All providers
            if choice.strip() == str(len(PROVIDERS) + 1):
                return list(PROVIDERS.keys())
            
            # Parse comma-separated list
            selected_indices = [int(x.strip()) for x in choice.split(",")]
            if any(idx < 1 or idx > len(PROVIDERS) for idx in selected_indices):
                print(f"{RED}Invalid selection. Please enter numbers between 1 and {len(PROVIDERS)}.{NC}")
                continue
            
            # Convert indices to provider keys
            selected_providers = [list(PROVIDERS.keys())[idx-1] for idx in selected_indices]
            
            # Confirm selection
            print(f"\nYou selected: {', '.join([PROVIDERS[p] for p in selected_providers])}")
            confirm = input("Is this correct? (y/n): ").lower()
            if confirm.startswith('y'):
                return selected_providers
        except (ValueError, IndexError) as e:
            print(f"{RED}Invalid input: {e}. Please try again.{NC}")

def select_research_endpoints():
    """Let the user select which research endpoints to test"""
    print_header("Select Research Endpoints to Test")
    print("Available endpoints:")
    
    for i, (key, name) in enumerate(RESEARCH_ENDPOINTS.items(), 1):
        print(f"{i}. {name} ({key})")
    
    print(f"{len(RESEARCH_ENDPOINTS) + 1}. All endpoints")
    print(f"{len(RESEARCH_ENDPOINTS) + 2}. Return to main menu")
    
    while True:
        try:
            choice = input("\nEnter the number(s) of the endpoints to test (comma-separated): ")
            
            # Return to main menu
            if choice.strip() == str(len(RESEARCH_ENDPOINTS) + 2):
                return []
            
            # All endpoints
            if choice.strip() == str(len(RESEARCH_ENDPOINTS) + 1):
                return list(RESEARCH_ENDPOINTS.keys())
            
            # Parse comma-separated list
            selected_indices = [int(x.strip()) for x in choice.split(",")]
            if any(idx < 1 or idx > len(RESEARCH_ENDPOINTS) for idx in selected_indices):
                print(f"{RED}Invalid selection. Please enter numbers between 1 and {len(RESEARCH_ENDPOINTS)}.{NC}")
                continue
            
            # Convert indices to endpoint keys
            selected_endpoints = [list(RESEARCH_ENDPOINTS.keys())[idx-1] for idx in selected_indices]
            
            # Confirm selection
            print(f"\nYou selected: {', '.join([RESEARCH_ENDPOINTS[p] for p in selected_endpoints])}")
            confirm = input("Is this correct? (y/n): ").lower()
            if confirm.startswith('y'):
                return selected_endpoints
        except (ValueError, IndexError) as e:
            print(f"{RED}Invalid input: {e}. Please try again.{NC}")

def run_web_search_tests():
    """Run tests for the Web Search endpoints"""
    print_header("Testing Web Search Endpoints")
    
    # Test 1: DuckDuckGo GET endpoint
    print_header("1. Testing DuckDuckGo Search (GET)")
    test_endpoint("/web/duckduckgo?query=python%20flask%20api&max_results=3")
    
    # Test 2: DuckDuckGo POST endpoint
    print_header("2. Testing DuckDuckGo Search (POST)")
    post_data = json.dumps({
        "query": "accessibility web design",
        "max_results": 2,
        "region": "us-en",
        "safesearch": "moderate"
    })
    test_endpoint("/web/duckduckgo", "POST", post_data)

if __name__ == "__main__":
    main() 