# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_alt_anthropic.py

File: `toollama/API/--storage/processed-flask-chat/flask_alt_anthropic.py`  
Language: Python  
Extracted: 2025-06-07 05:17:56  

## Snippet 1
Lines 1-12

```Python
#!/usr/bin/env python
import os
import sys
import tempfile
import io
from flask import Flask, request, render_template_string, Response
from typing import Generator, List, Dict, Optional
from datetime import datetime
from base64 import b64encode
from PIL import Image, ImageDraw, ImageFont
import anthropic
```

## Snippet 2
Lines 20-24

```Python
def __init__(self, api_key: str):
        """Initialize the Anthropic client with the provided API key."""
        self.client = anthropic.Client(api_key=api_key)
        self.conversation_history = []
```

## Snippet 3
Lines 25-59

```Python
def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve available Claude models with pagination.

        Args:
            sort_by (str): Field to sort by ('created', 'id', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter models by capability ('vision', 'text')

        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Make direct API call to list models
            response = self.client._client.get(
                "https://api.anthropic.com/v1/models",
                headers={
                    "x-api-key": self.client.api_key,
                    "anthropic-version": "2023-06-01"
                }
            )
            response.raise_for_status()
            models_data = response.json()

            # Process and enhance model data
            processed_models = []
```

## Snippet 4
Lines 74-89

```Python
if capability_filter and capability_filter not in capabilities:
                    continue

                # Create enhanced model info
                model_info = {
                    "id": model['id'],
                    "name": model.get('display_name', model['id'].replace("-", " ").title()),
                    "description": f"Claude 3 {model['id'].split('-')[-2].title()}",
                    "capabilities": capabilities,
                    "capability_count": len(capabilities),
                    "created": model['created_at'],
                    "created_at": format_date(model['created_at']),
                    "owned_by": "anthropic"
                }
                processed_models.append(model_info)
```

## Snippet 5
Lines 93-103

```Python
elif sort_by == "capabilities":
                processed_models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by id
                processed_models.sort(key=lambda x: x["id"], reverse=reverse)

            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            return processed_models[start_idx:end_idx]
```

## Snippet 6
Lines 104-107

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []
```

## Snippet 7
Lines 108-130

```Python
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
```

## Snippet 8
Lines 131-135

```Python
def create_test_file(self) -> str:
        """Create a simple test text file and return its base64 encoding."""
        test_content = "This is a test file content.\nIt has multiple lines.\nHello, Claude!"
        return b64encode(test_content.encode('utf-8')).decode('utf-8')
```

## Snippet 9
Lines 136-144

```Python
def process_image(self, image_path: str) -> Optional[Dict]:
        """
        Process an image file and return it in the format required by Claude.
        Supports PNG, JPEG, GIF, and WEBP formats.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 10
Lines 146-156

```Python
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
```

## Snippet 11
Lines 157-175

```Python
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
```

## Snippet 12
Lines 176-179

```Python
except Exception as e:
            print(f"Error processing image: {e}", file=sys.stderr)
            return None
```

## Snippet 13
Lines 180-204

```Python
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
            # Construct the message content
            message_content = [{"type": "text", "text": prompt}]
```

## Snippet 14
Lines 205-213

```Python
if use_test_image:
                message_content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": self.create_test_image()
                    }
                })
```

## Snippet 15
Lines 219-231

```Python
# Add the new message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message_content
            })

            # Stream the response
            with self.client.messages.stream(
                max_tokens=max_tokens,
                messages=self.conversation_history,
                model=model,
            ) as stream:
                response_text = ""
```

## Snippet 16
Lines 232-241

```Python
for text in stream.text_stream:
                    response_text += text
                    yield text

                # Add assistant's response to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response_text
                })
```

## Snippet 17
Lines 242-250

```Python
except anthropic.APIError as e:
            print(f"API Error: {e}", file=sys.stderr)
        except anthropic.APIConnectionError as e:
            print(f"Connection Error: {e}", file=sys.stderr)
        except anthropic.AuthenticationError as e:
            print(f"Authentication Error: Please check your API key", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
```

## Snippet 18
Lines 251-254

```Python
def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
```

## Snippet 19
Lines 255-262

```Python
def format_date(date_str: str) -> str:
    """Format the date string in a human-readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y")
    except:
        return date_str
```

## Snippet 20
Lines 263-272

```Python
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
```

## Snippet 21
Lines 273-276

```Python
if capability_filter:
        print(f"Filtering by capability: {capability_filter}")
    print("-" * 50)
```

## Snippet 22
Lines 277-285

```Python
for idx, model in enumerate(models, 1):
        print(f"{idx}. {model['name']}")
        print(f"   Model: {model['id']}")
        print(f"   Description: {model['description']}")
        print(f"   Capabilities: {', '.join(model['capabilities'])}")
        print(f"   Released: {model['created_at']}")
        print(f"   Owner: {model['owned_by']}")
        print()
```

## Snippet 23
Lines 290-293

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 24
Lines 296-300

```Python
def main():
    """Main CLI interface."""
    # Initialize with API key
    api_key = os.getenv("ANTHROPIC_API_KEY") or "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"
```

## Snippet 25
Lines 301-319

```Python
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
```

## Snippet 26
Lines 322-325

```Python
if not all_models:
        print("Error: Could not fetch models. Please check your API key and connection.")
        sys.exit(1)
```

## Snippet 27
Lines 326-349

```Python
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
```

## Snippet 28
Lines 350-353

```Python
if choice == "1":
            # Select model
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 29
Lines 368-382

```Python
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
```

## Snippet 30
Lines 383-388

```Python
elif choice == "5":
            # Filter by capability
            cap_choice = get_user_input(
                "Filter by capability (vision/text/code/analysis/none)",
                "none"
            ).lower()
```

## Snippet 31
Lines 389-398

```Python
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
```

## Snippet 32
Lines 399-402

```Python
elif choice == "6":
            # Change page size
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
```

## Snippet 33
Lines 403-406

```Python
if new_size > 0:
                    page_size = new_size
                    total_pages = (len(all_models) + page_size - 1) // page_size
                    page = 1  # Reset to first page
```

## Snippet 34
Lines 416-422

```Python
while True:
        # Ask about including an image
        image_choice = get_user_input("Image options: (1) No image (2) Test image (3) Custom image path", "1")

        image_path = None
        use_test_image = False
```

## Snippet 35
Lines 429-434

```Python
default_prompt = "What do you see in this image?" if (use_test_image or image_path) else "Hello! How can I help you today?"
        prompt = get_user_input("Enter your prompt", default_prompt)

        # Stream response
        print("\nStreaming response:")
        print("-" * 50)
```

## Snippet 36
Lines 440-445

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

## Snippet 37
Lines 448-456

```Python
# -------------------------------------------------------------------

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
```

## Snippet 38
Lines 461-468

```Python
.model-selector { margin-bottom: 1.5rem; }
    .model-card {
      border: 1px solid #ddd;
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 4px;
      cursor: pointer;
    }
```

## Snippet 39
Lines 471-477

```Python
.model-capabilities { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
    .capability-tag {
      background: #e0e0e0;
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
    }
```

## Snippet 40
Lines 478-486

```Python
.controls { display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem; }
    button {
      padding: 0.5rem 1rem;
      background: #2196f3;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
```

## Snippet 41
Lines 491-518

```Python
</head>
<body>
  <h1>Alt Text - Anthropic</h1>

  <div class="model-selector">
    <h2>Select Model</h2>
    <div class="controls">
      <select id="sortBy">
        <option value="created">Sort by Created Date</option>
        <option value="capabilities">Sort by Capabilities</option>
        <option value="id">Sort by ID</option>
      </select>
      <select id="filterCapability">
        <option value="none">No Capability Filter</option>
        <option value="vision">Vision</option>
        <option value="text">Text</option>
        <option value="code">Code</option>
        <option value="analysis">Analysis</option>
      </select>
      <button onclick="refreshModels()">Refresh Models</button>
      <div class="loading" id="modelLoading">Loading models...</div>
    </div>
    <div id="modelError"></div>
    <div id="modelList"></div>
  </div>

  <form id="upload-form">
    <label for="image">Select Image:</label>
```

## Snippet 42
Lines 521-523

```Python
<input type="text" id="prompt" name="prompt" size="80" value="Generate descriptive alt text for the visually impaired for social media"><br><br>
    <button type="submit">Generate Alt Text</button>
    <div class="loading" id="generateLoading">Generating response...</div>
```

## Snippet 43
Lines 524-530

```Python
</form>
  <h2>Response:</h2>
  <div id="output"></div>

  <script>
    let selectedModel = null;
```

## Snippet 44
Lines 531-539

```Python
async function fetchModels() {
      const sortBy = document.getElementById('sortBy').value;
      const filterCapability = document.getElementById('filterCapability').value;

      try {
        document.getElementById('modelLoading').style.display = 'block';
        document.getElementById('modelError').textContent = '';

        const response = await fetch(`/models?sort_by=${sortBy}&capability_filter=${filterCapability}`);
```

## Snippet 45
Lines 540-565

```Python
if (!response.ok) {
          throw new Error(await response.text());
        }

        const models = await response.json();
        const modelList = document.getElementById('modelList');
        modelList.innerHTML = '';

        models.forEach(model => {
          const modelCard = document.createElement('div');
          modelCard.className = `model-card${selectedModel === model.id ? ' selected' : ''}`;
          modelCard.onclick = () => selectModel(model.id);

          modelCard.innerHTML = `
            <strong>${model.name}</strong>
            <div>${model.description}</div>
            <div class="model-capabilities">
              ${model.capabilities.map(cap =>
                `<span class="capability-tag">${cap}</span>`
              ).join('')}
            </div>
            <small>Released: ${model.created_at}</small>
          `;

          modelList.appendChild(modelCard);
        });
```

## Snippet 46
Lines 573-579

```Python
function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelectorAll('.model-card').forEach(card => {
        card.classList.toggle('selected', card.querySelector('strong').textContent === modelId);
      });
    }
```

## Snippet 47
Lines 580-586

```Python
function refreshModels() {
      fetchModels();
    }

    document.getElementById("upload-form").addEventListener("submit", async function(e) {
      e.preventDefault();
```

## Snippet 48
Lines 587-606

```Python
if (!selectedModel) {
        alert('Please select a model first');
        return;
      }

      document.getElementById("output").textContent = "";
      document.getElementById("generateLoading").style.display = 'block';

      const formData = new FormData();
      const imageInput = document.getElementById("image");
      const promptInput = document.getElementById("prompt");
      formData.append("image", imageInput.files[0]);
      formData.append("prompt", promptInput.value);
      formData.append("model", selectedModel);

      try {
        const response = await fetch("/generate", {
          method: "POST",
          body: formData
        });
```

## Snippet 49
Lines 607-613

```Python
if (!response.ok) {
          document.getElementById("output").textContent = "Error: " + await response.text();
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
```

## Snippet 50
Lines 617-620

```Python
if (value) {
            const chunk = decoder.decode(value);
            document.getElementById("output").textContent += chunk;
          }
```

## Snippet 51
Lines 637-641

```Python
def get_models():
    """Endpoint to get available Claude models."""
    try:
        sort_by = request.args.get("sort_by", "created")
        capability_filter = request.args.get("capability_filter")
```

## Snippet 52
Lines 647-661

```Python
if not api_key:
            return "API key not set", 500

        chat = AnthropicChat(api_key)

        # Get models with the specified sorting and filtering
        models = chat.list_models(
            sort_by=sort_by,
            page=1,
            page_size=1000,  # Get all models
            capability_filter=capability_filter
        )

        return models
```

## Snippet 53
Lines 672-675

```Python
if "image" not in request.files:
        return "No image uploaded", 400

    image_file = request.files["image"]
```

## Snippet 54
Lines 676-687

```Python
prompt = request.form.get("prompt", "Generate descriptive alt text for the visually impaired for social media")
    model = request.form.get("model", "claude-3-opus-20240229")  # Get selected model

    # Save the uploaded image to a temporary file.
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
    try:
        image_file.save(temp_file.name)
        temp_file.close()

        # Instantiate the AnthropicChat with the API key from the environment.
        api_key = os.getenv("ANTHROPIC_API_KEY") or ANTHROPIC_API_KEY
```

## Snippet 55
Lines 688-692

```Python
if not api_key:
            return "API key not set", 500

        chat = AnthropicChat(api_key)
```

## Snippet 56
Lines 693-695

```Python
def generate_response():
            try:
                # Call the streaming chat response with the uploaded image.
```

## Snippet 57
Lines 698-706

```Python
except Exception as e:
                yield f"\nError: {str(e)}"
            finally:
                # Clean up the temporary file.
                try:
                    os.remove(temp_file.name)
                except Exception as cleanup_error:
                    print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)
```

