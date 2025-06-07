"""
Proxy implementation for Anthropic Chat that communicates with the Flask server
"""

import os
import sys
import requests
from typing import Generator, List, Dict, Optional
from datetime import datetime
from base64 import b64encode
from PIL import Image, ImageDraw, ImageFont
import io
import json

ANTHROPIC_API_KEY = "test-key-local-dev-2024"


class AnthropicChat:
    def __init__(self, api_key: str):
        """Initialize the proxy client with API key for server authentication."""
        self.api_key = api_key
        self.base_url = "http://api.assisted.space"  # Update this to match your server
        self.headers = {
            "X-API-Key": "test-key-local-dev-2024",
            "Content-Type": "application/json"
        }
        self.conversation_history = []
        # Create fallback direct client
        self.direct_client = None
        try:
            import anthropic
            self.direct_client = anthropic.Client(api_key=api_key)
        except ImportError:
            print("Warning: anthropic package not installed, falling back to proxy only")

    def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """Query the server's model list endpoint with fallback to direct API."""
        try:
            # Try proxy server first
            params = {
                "sort_by": sort_by,
                "reverse": str(reverse).lower(),
                "page": page,
                "page_size": page_size
            }
            if capability_filter:
                params["capability"] = capability_filter

            response = requests.get(
                f"{self.base_url}/camina/anthropic/models",
                headers=self.headers,
                params=params,
                timeout=5  # Add timeout
            )
            
            if response.status_code == 200:
                return response.json()["models"]
            
        except requests.exceptions.RequestException as e:
            print(f"Warning: Proxy server unavailable ({e}), falling back to direct API")
        
        # Fall back to direct API if proxy fails
        if self.direct_client:
            try:
                return self._get_models_from_direct_api(
                    sort_by=sort_by,
                    reverse=reverse,
                    page=page,
                    page_size=page_size,
                    capability_filter=capability_filter
                )
            except Exception as e:
                print(f"Error accessing direct API: {e}", file=sys.stderr)
        
        # If all else fails, return hardcoded models
        return self._get_hardcoded_models(sort_by, reverse, page, page_size, capability_filter)

    def _get_models_from_direct_api(
        self,
        sort_by: str,
        reverse: bool,
        page: int,
        page_size: int,
        capability_filter: Optional[str]
    ) -> List[Dict]:
        """Get models directly from Anthropic API."""
        models = self.direct_client.models.list()
        processed_models = []
        for model in models.data:
            if not model.id.startswith("claude") or "claude-3" not in model.id:
                continue
            
            capabilities = ["text"]
            if "opus" in model.id.lower():
                capabilities.extend(["vision", "code", "analysis"])
            elif "sonnet" in model.id.lower():
                capabilities.extend(["vision", "code"])
            elif "haiku" in model.id.lower():
                capabilities.append("vision")
            
            if capability_filter and capability_filter not in capabilities:
                continue
            
            model_info = {
                "id": model.id,
                "name": model.id.replace("-", " ").title(),
                "description": f"Claude 3 {model.id.split('-')[-2].title()} - Advanced AI model",
                "capabilities": capabilities,
                "capability_count": len(capabilities),
                "owned_by": "anthropic"
            }
            processed_models.append(model_info)
        
        if sort_by == "capabilities":
            processed_models.sort(key=lambda x: x["capability_count"], reverse=reverse)
        else:  # sort by id
            processed_models.sort(key=lambda x: x["id"], reverse=reverse)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return processed_models[start_idx:end_idx]

    def _get_hardcoded_models(self, sort_by, reverse, page, page_size, capability_filter) -> List[Dict]:
        """Return hardcoded model list as last resort."""
        models = [
            {
                "id": "claude-3-opus-20240229",
                "name": "Claude 3 Opus",
                "description": "Claude 3 Opus - Most powerful model with vision, code, and analysis capabilities",
                "capabilities": ["text", "vision", "code", "analysis"],
                "capability_count": 4,
                "owned_by": "anthropic"
            },
            {
                "id": "claude-3-sonnet-20240229",
                "name": "Claude 3 Sonnet",
                "description": "Claude 3 Sonnet - Balanced model with vision and code capabilities",
                "capabilities": ["text", "vision", "code"],
                "capability_count": 3,
                "owned_by": "anthropic"
            },
            {
                "id": "claude-3-haiku-20240307",
                "name": "Claude 3 Haiku",
                "description": "Claude 3 Haiku - Fast and efficient model with vision capability",
                "capabilities": ["text", "vision"],
                "capability_count": 2,
                "owned_by": "anthropic"
            }
        ]
        
        if capability_filter:
            models = [m for m in models if capability_filter in m["capabilities"]]
        
        if sort_by == "capabilities":
            models.sort(key=lambda x: x["capability_count"], reverse=reverse)
        else:
            models.sort(key=lambda x: x["id"], reverse=reverse)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        return models[start_idx:end_idx]

    def create_test_image(self) -> str:
        """
        Create a test image with some shapes and text.
        Returns base64 encoded PNG image.
        """
        # Create a new image with a white background
        width, height = 400, 200
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes
        draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
        draw.ellipse([200, 50, 300, 150], fill='blue', outline='black')
        
        # Add text
        draw.text((150, 160), "Test Image", fill='black')
        
        # Convert to base64
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return b64encode(img_byte_arr).decode('utf-8')

    def create_test_file(self) -> str:
        """Create a simple test text file and return its base64 encoding."""
        test_content = "This is a test file content.\nIt has multiple lines.\nHello, Claude!"
        return b64encode(test_content.encode('utf-8')).decode('utf-8')

    def process_image(self, image_path: str) -> Optional[Dict]:
        """
        Process an image file and return it in the format required by Claude.
        Supports PNG, JPEG, GIF, and WEBP formats.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[Dict]: Image data formatted for Claude API or None if invalid
        """
        try:
            with Image.open(image_path) as img:
                # Convert format name to mime type
                format_to_mime = {
                    'PNG': 'image/png',
                    'JPEG': 'image/jpeg',
                    'GIF': 'image/gif',
                    'WEBP': 'image/webp'
                }
                
                if img.format not in format_to_mime:
                    print(f"Unsupported image format: {img.format}. Must be PNG, JPEG, GIF, or WEBP.", 
                          file=sys.stderr)
                    return None
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                img_byte_arr = img_byte_arr.getvalue()
                
                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": format_to_mime[img.format],
                        "data": b64encode(img_byte_arr).decode('utf-8')
                    }
                }
                
        except Exception as e:
            print(f"Error processing image: {e}", file=sys.stderr)
            return None

    def stream_chat_response(
        self,
        prompt: str,
        max_tokens: int = 1024,
        model: str = "claude-3-opus-20240229",
        image_path: Optional[str] = None,
        use_test_image: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Claude.
        
        Args:
            prompt (str): The user's input message
            max_tokens (int): Maximum number of tokens in the response
            model (str): The Claude model to use
            image_path (Optional[str]): Path to an image file (PNG, JPEG, GIF, or WEBP)
            use_test_image (bool): Whether to use the test image instead of image_path
            
        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Prepare the request data (payload)
            payload = {
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
            }
            if use_test_image or image_path:
                payload["image"] = {
                    "use_test": use_test_image,
                    "path": image_path if image_path else None
                }
            # Make a streaming POST call to the internal server that handles the Anthropic chat endpoint
            response = requests.post(
                f"{self.base_url}/camina/anthropic/chat",
                headers=self.headers,
                json=payload,
                stream=True
            )
            # Process and yield each chunk as it is received
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # Remove SSE prefix if present
                    if decoded_line.startswith("data: "):
                        chunk = decoded_line[6:]
                        yield chunk
                    else:
                        yield decoded_line
        except Exception as e:
            print(f"Error in chat stream: {e}", file=sys.stderr)
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []

def format_date(date_str: str) -> str:
    """Format the date string in a human-readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y")
    except:
        return date_str

def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    capability_filter: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable Claude Models (Page {current_page}/{total_pages}):")
    print(f"Sorting by: {sort_by}")
    if capability_filter:
        print(f"Filtering by capability: {capability_filter}")
    print("-" * 50)
    
    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Description: {model['description']}")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        # print(f"   Released: {model['created_at']}")
        print(f"   Owner: {model['owned_by']}")
        print()

def get_user_input(prompt: str, default: str = None) -> str:
    """Get user input with an optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    response = input(prompt).strip()
    return response if response else default

def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = os.getenv("ANTHROPIC_API_KEY") or "test-key-local-dev-2024"
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    chat = AnthropicChat(api_key)
    
    # Model browsing loop
    page = 1
    page_size = 5
    sort_by = "created"
    capability_filter = None
    
    # Get initial full list of models
    all_models = chat.list_models(
        sort_by=sort_by,
        page=1,
        page_size=1000,
        capability_filter=capability_filter
    )
    total_pages = (len(all_models) + page_size - 1) // page_size if all_models else 0
    
    if not all_models:
        print("Error: Could not fetch models. Please check your API key and connection.")
        sys.exit(1)
    
    while True:
        # Get current page of models
        models = chat.list_models(
            sort_by=sort_by,
            page=page,
            page_size=page_size,
            capability_filter=capability_filter
        )
        
        # Display models
        display_models(models, page, total_pages, sort_by, capability_filter)
        
        # Show options
        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (created/id/capabilities)")
        print("5. Filter by capability (vision/text/code/analysis/none)")
        print("6. Change page size")
        print("7. Quit")
        
        choice = get_user_input("Select option", "1")
        
        if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
                if 0 <= selection < len(models):
                    selected_model = models[selection]["id"]
                    break
                print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "2":
            # Next page
            if page < total_pages:
                page += 1
        elif choice == "3":
            # Previous page
            if page > 1:
                page -= 1
        elif choice == "4":
            # Sort by
            sort_by = get_user_input(
                "Sort by (created/id/capabilities)",
                "created"
            )
            # Refresh model list with new sorting
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "5":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (vision/text/code/analysis/none)",
                "none"
            ).lower()
            capability_filter = None if cap_choice == "none" else cap_choice
            # Refresh model list with new filter
            all_models = chat.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability_filter
            )
            total_pages = (len(all_models) + page_size - 1) // page_size
            page = 1  # Reset to first page
        elif choice == "6":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
                if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1  # Reset to first page
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "7":
            print("Exiting...")
            sys.exit(0)
        
        print()  # Add spacing between iterations

    # Start conversation loop
    while True:
        # Ask about including an image
        image_choice = get_user_input("Image options: (1) No image (2) Test image (3) Custom image path", "1")
        
        image_path = None
        use_test_image = False
        
        if image_choice == "2":
            use_test_image = True
        elif image_choice == "3":
            image_path = get_user_input("Enter image path", "")
        
        # Get prompt
        default_prompt = "What do you see in this image?" if (use_test_image or image_path) else "Hello! How can I help you today?"
        prompt = get_user_input("Enter your prompt", default_prompt)
        
        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
        for chunk in chat.stream_chat_response(prompt, 1024, selected_model, image_path, use_test_image):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 50)
        
        # Ask to continue
        if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")

if __name__ == "__main__":
    main() 