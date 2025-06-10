#!/usr/bin/env python
import os
import sys
import json
import requests
from datetime import datetime

# Base URL for the API
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.assisted.space/v2")

# Colors for terminal output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color

# Create output directory for test results
OUTPUT_DIR = "test_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# API Keys (replace with your actual keys or use environment variables)
XAI_API_KEY = os.environ.get("XAI_API_KEY", "xai-IxAzklP9jWAhmKaE3pz9PBfcTAowVgNAd9fx1iWwYHNL7kowydC3MAmrMweXROg1q19dq5lye3NG6nmK")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "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")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAXLsdBC6qYhW9djaep-gCWQasszLHfi8U")

def print_header(text):
    """Print a formatted header for test sections."""
    print(f"\n{BLUE}{'='*80}{NC}")
    print(f"{BLUE}= {text}{NC}")
    print(f"{BLUE}{'='*80}{NC}\n")

def test_image_generation(provider, model=None, prompt="A beautiful sunset over mountains with a lake"):
    """Test image generation for a provider."""
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
            # Remove the seed parameter which is causing errors
            # data["seed"] = 42  # Example seed for deterministic output
            data["api_key"] = XAI_API_KEY
            print(f"{YELLOW}Using X.AI API key from script variable{NC}")
        
        # Add quality and style for OpenAI
        if provider == "openai":
            data["quality"] = "standard"
            data["style"] = "vivid"
            data["api_key"] = OPENAI_API_KEY
            print(f"{YELLOW}Using OpenAI API key from script variable{NC}")
        
        # Add Gemini API key
        if provider == "gemini":
            data["api_key"] = GEMINI_API_KEY
            print(f"{YELLOW}Using Gemini API key from script variable{NC}")
        
        # Log request data (excluding API keys)
        safe_data = data.copy()
        if "api_key" in safe_data:
            safe_data["api_key"] = "***"
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
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print(f"{GREEN}Success! Status code: {response.status_code}{NC}")
            
            # Save the complete response to a file
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"{GREEN}Response saved to {output_file}{NC}")
            
            # Print the image URL(s) if available
            if "data" in result and isinstance(result["data"], list):
                for i, img_data in enumerate(result["data"]):
                    if "url" in img_data:
                        print(f"{GREEN}Image {i+1} URL: {img_data['url'][:100]}...{NC}")
            else:
                print(f"{YELLOW}No image data found in response{NC}")
                
            return True
        else:
            print(f"{RED}Error! Status code: {response.status_code}{NC}")
            try:
                error = response.json()
                print(f"{RED}Error response: {json.dumps(error, indent=2)}{NC}")
            except:
                print(f"{RED}Error response: {response.text}{NC}")
            return False
            
    except Exception as e:
        print(f"{RED}Exception occurred: {str(e)}{NC}")
        return False

def main():
    """Run tests for all providers."""
    print_header("Image Generation Tests")
    
    # Define a list of providers and optional custom prompts
    tests = [
        {"provider": "openai", "prompt": "A cute baby sea otter"},
        {"provider": "gemini", "prompt": "A beautiful sunset over mountains with a lake"},
        {"provider": "xai", "prompt": "A cyberpunk city at night with neon lights and flying vehicles"}
    ]
    
    success_count = 0
    for i, test in enumerate(tests):
        print_header(f"Test {i+1}: {test['provider'].upper()}")
        if test_image_generation(test["provider"], prompt=test["prompt"]):
            success_count += 1
    
    print_header("Test Results")
    print(f"{GREEN if success_count == len(tests) else YELLOW}Tests completed: {success_count}/{len(tests)} successful{NC}")
    
    return 0 if success_count == len(tests) else 1

if __name__ == "__main__":
    sys.exit(main()) 