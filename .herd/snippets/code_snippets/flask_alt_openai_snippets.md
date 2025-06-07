# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_alt_openai.py

File: `toollama/API/--storage/processed-flask-chat/flask_alt_openai.py`  
Language: Python  
Extracted: 2025-06-07 05:17:53  

## Snippet 1
Lines 1-10

```Python
#!/usr/bin/env python
import sys
import os
import base64
import io
from datetime import datetime
from typing import Generator, List, Dict, Optional, Union
from PIL import Image
import tempfile
```

## Snippet 2
Lines 13-16

```Python
# -------------------------------------------------------------------

from openai import OpenAI
```

## Snippet 3
Lines 17-51

```Python
class OpenAIChat:
    # Default models in case API fetch fails
    DEFAULT_MODELS = {
        "gpt-4o-2024-11-20": {
            "id": "gpt-4o-2024-11-20",
            "context_length": 128000,
            "description": "GPT-4 Omega model",
            "capabilities": ["text", "function"]
        },
        "gpt-4-vision-preview": {
            "id": "gpt-4-vision-preview",
            "context_length": 128000,
            "description": "GPT-4 model with vision capabilities",
            "capabilities": ["text", "vision", "function"]
        },
        "gpt-4-0125-preview": {
            "id": "gpt-4-0125-preview",
            "context_length": 128000,
            "description": "GPT-4 preview model",
            "capabilities": ["text", "function"]
        },
        "gpt-4": {
            "id": "gpt-4",
            "context_length": 8192,
            "description": "GPT-4 base model",
            "capabilities": ["text", "function"]
        },
        "gpt-3.5-turbo-0125": {
            "id": "gpt-3.5-turbo-0125",
            "context_length": 16385,
            "description": "GPT-3.5 Turbo model",
            "capabilities": ["text", "function"]
        }
    }
```

## Snippet 4
Lines 57-62

```Python
def patched_init(self, api_key: str, **kwargs):
                kwargs.pop('proxies', None)
                original_init(self, api_key=api_key, **kwargs)
            OpenAI.__init__ = patched_init
            OpenAI._patched_no_proxies = True
```

## Snippet 5
Lines 63-70

```Python
self.client = OpenAI(api_key=api_key)
        self.models = self._fetch_models()
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
```

## Snippet 6
Lines 71-81

```Python
def _fetch_models(self) -> Dict:
        """
        Fetch available models from OpenAI API.

        Returns:
            Dict: Dictionary of available models with their details
        """
        try:
            models = {}
            response = self.client.models.list()
```

## Snippet 7
Lines 83-86

```Python
for model in response.data:
                model_id = model.id
                created = datetime.fromtimestamp(model.created)
```

## Snippet 8
Lines 103-107

```Python
elif "128k" in model_id or "vision" in model_id:
                        context_length = 128000

                    # Create model description
                    description = f"GPT {model_id}"
```

## Snippet 9
Lines 112-115

```Python
elif "16k" in model_id:
                        description += " with 16k context"

                    # Determine model generation and version
```

## Snippet 10
Lines 117-131

```Python
version = "preview" if "preview" in model_id else model_id.split('-')[-1] if '-' in model_id else None

                    models[model_id] = {
                        "id": model_id,
                        "context_length": context_length,
                        "description": description,
                        "capabilities": capabilities,
                        "capability_count": len(capabilities),
                        "created": created,
                        "created_str": created.strftime("%Y-%m-%d"),
                        "generation": generation,
                        "version": version,
                        "owned_by": model.owned_by
                    }
```

## Snippet 11
Lines 134-137

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return self.DEFAULT_MODELS
```

## Snippet 12
Lines 138-172

```Python
def list_models(
        self,
        sort_by: str = "created",
        reverse: bool = True,
        page: int = 1,
        page_size: int = 5,
        generation: Optional[str] = None
    ) -> List[Dict]:
        """
        Get available OpenAI models with sorting and pagination.

        Args:
            sort_by (str): Field to sort by ('created', 'context_length', 'id', 'capabilities')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            generation (Optional[str]): Filter by model generation ('4', '3.5', '3')

        Returns:
            List[Dict]: List of available models with their details
        """
        models_list = [
            {
                "id": info["id"],
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "capability_count": info["capability_count"],
                "created": info["created"],
                "created_str": info["created_str"],
                "generation": info["generation"],
                "version": info["version"],
                "owned_by": info["owned_by"]
            }
```

## Snippet 13
Lines 181-194

```Python
elif sort_by == "capabilities":
            models_list.sort(key=lambda x: (
                x["capability_count"],
                "images" in x["capabilities"],
                "text" in x["capabilities"]
            ), reverse=reverse)
        else:
            models_list.sort(key=lambda x: x["id"], reverse=reverse)

        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        return models_list[start_idx:end_idx]
```

## Snippet 14
Lines 195-202

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 15
Lines 204-211

```Python
"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 16
Lines 212-220

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
```

## Snippet 17
Lines 222-232

```Python
"""
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None
```

## Snippet 18
Lines 233-237

```Python
def create_test_file(self, content: str = None) -> str:
        """
        Create a test text file and return its base64 encoding.

        Args:
```

## Snippet 19
Lines 240-242

```Python
Returns:
            str: Base64 encoded file content
        """
```

## Snippet 20
Lines 243-246

```Python
if not content:
            content = "This is a test file.\nIt contains multiple lines.\nHello, GPT!"
        return base64.b64encode(content.encode('utf-8')).decode('utf-8')
```

## Snippet 21
Lines 247-254

```Python
def encode_file(self, file_path: str) -> Optional[str]:
        """
        Encode a file to base64.

        Args:
            file_path (str): Path to the file

        Returns:
```

## Snippet 22
Lines 256-263

```Python
"""
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding file: {e}", file=sys.stderr)
            return None
```

## Snippet 23
Lines 264-269

```Python
def format_message_with_image(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 24
Lines 280-292

```Python
if is_url:
                content.append({
                    "type": "image_url",
                    "image_url": img
                })
            else:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}"
                    }
                })
```

## Snippet 25
Lines 295-301

```Python
def format_message_with_attachments(
        self,
        message: str,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Union[str, List[Dict]]:
```

## Snippet 26
Lines 303-307

```Python
if not image_data and not file_data:
            return message

        content = [{"type": "text", "text": message}]
```

## Snippet 27
Lines 313-325

```Python
if is_url:
                    content.append({
                        "type": "image_url",
                        "image_url": img
                    })
                else:
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img}"
                        }
                    })
```

## Snippet 28
Lines 326-333

```Python
if file_data:
            content.append({
                "type": "text",
                "text": f"\nFile content:\n{base64.b64decode(file_data).decode('utf-8', errors='ignore')}"
            })

        return content
```

## Snippet 29
Lines 334-365

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = "gpt-3.5-turbo-0125",
        temperature: float = 0.7,
        image_data: Optional[Union[str, List[str]]] = None,
        file_data: Optional[str] = None,
        is_url: bool = False
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from OpenAI.

        Args:
            message (str): The user's input message
            model (str): The OpenAI model to use
            temperature (float): Response temperature (0.0 to 1.0)
            image_data (Optional[Union[str, List[str]]]): Image URL(s) or base64 data
            file_data (Optional[str]): Base64 encoded file data
            is_url (bool): Whether image_data contains URLs

        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            content = self.format_message_with_attachments(message, image_data, file_data, is_url)

            self.chat_history.append({
                "role": "user",
                "content": content
            })

            messages = []
```

## Snippet 30
Lines 367-374

```Python
if isinstance(msg["content"], list):
                    messages.append(msg)
                else:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
```

## Snippet 31
Lines 375-384

```Python
model_id = self.models[model]["id"] if model in self.models else model

            stream = self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            full_response = ""
```

## Snippet 32
Lines 386-390

```Python
if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield text
```

## Snippet 33
Lines 398-401

```Python
if self.chat_history:
                self.chat_history.pop()
            yield f"Error: {str(e)}"
```

## Snippet 34
Lines 402-408

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on providing accurate and detailed responses."
        }]
```

## Snippet 35
Lines 413-421

```Python
def display_models(
    models: List[Dict],
    current_page: int,
    total_pages: int,
    sort_by: str,
    generation: Optional[str] = None
) -> None:
    """Display available models in a formatted way."""
    print(f"\nAvailable OpenAI Models (Page {current_page}/{total_pages}):")
```

## Snippet 36
Lines 443-446

```Python
else:
        prompt = f"{prompt}: "

    response = input(prompt).strip()
```

## Snippet 37
Lines 449-459

```Python
def main_cli():
    """Main CLI interface."""
    api_key = "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"
    chat = OpenAIChat(api_key)

    page = 1
    page_size = 5
    sort_by = "created"
    generation = None
    capability_filter = None
```

## Snippet 38
Lines 471-484

```Python
display_models(models, page, total_pages, sort_by, generation)

        print("\nOptions:")
        print("1. Select model")
        print("2. Next page")
        print("3. Previous page")
        print("4. Sort by (created/context_length/id/capabilities)")
        print("5. Filter by generation (4/3.5/3/none)")
        print("6. Filter by capability (text/function/vision/none)")
        print("7. Change page size")
        print("8. Quit")

        choice = get_user_input("Select option", "1")
```

## Snippet 39
Lines 485-487

```Python
if choice == "1":
            try:
                selection = int(get_user_input("Select a model number", "1")) - 1
```

## Snippet 40
Lines 511-513

```Python
elif choice == "7":
            try:
                new_size = int(get_user_input("Enter page size", str(page_size)))
```

## Snippet 41
Lines 514-516

```Python
if new_size > 0:
                    page_size = new_size
                    page = 1
```

## Snippet 42
Lines 526-528

```Python
while True:
        supports_images = "vision" in chat.models[selected_model]["capabilities"]
        print("\nInput options:")
```

## Snippet 43
Lines 529-544

```Python
if not supports_images:
            print("[Note: Selected model does not support image understanding]")

        print("\nAttachment options:")
        print("1. Text only")
        print("2. Test image (colored square)")
        print("3. Load image from file")
        print("4. Image from URL")
        print("5. Test file (sample text)")
        print("6. Load file from disk")

        input_choice = get_user_input("Select input option", "1")
        image_data = None
        file_data = None
        is_url = False
```

## Snippet 44
Lines 545-550

```Python
if input_choice == "2" and supports_images:
            color = get_user_input("Enter color (e.g., red, blue, green)", "red")
            size_str = get_user_input("Enter size (width,height)", "100,100")
            try:
                width, height = map(int, size_str.split(","))
                image_data = chat.create_test_image(color=color, size=(width, height))
```

## Snippet 45
Lines 553-555

```Python
except ValueError:
                print("Invalid size format. Using default 100x100...")
                image_data = chat.create_test_image(color=color)
```

## Snippet 46
Lines 556-558

```Python
elif input_choice == "3" and supports_images:
            file_path = get_user_input("Enter image file path")
            image_data = chat.encode_image(file_path)
```

## Snippet 47
Lines 563-565

```Python
if url:
                image_data = url
                is_url = True
```

## Snippet 48
Lines 584-589

```Python
if get_user_input("\nContinue conversation? (y/n)", "y").lower() != 'y':
            print("\nClearing conversation history and exiting...")
            chat.clear_conversation()
            break
        print("\nContinuing conversation...\n")
```

## Snippet 49
Lines 592-607

```Python
# -------------------------------------------------------------------

from flask import Flask, request, render_template_string, Response

app = Flask(__name__)

# Add this before the Flask routes
DEFAULT_API_KEY = "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"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OpenAI Chat Interface</title>
  <style>
```

## Snippet 50
Lines 610-617

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

## Snippet 51
Lines 620-626

```Python
.model-capabilities { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
    .capability-tag {
      background: #e0e0e0;
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
    }
```

## Snippet 52
Lines 627-635

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

## Snippet 53
Lines 638-645

```Python
#modelError { color: red; margin: 1rem 0; }
    .model-info {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
      font-size: 0.9rem;
      color: #666;
    }
```

## Snippet 54
Lines 647-680

```Python
</head>
<body>
  <h1>OpenAI Chat Interface</h1>

  <div class="model-selector">
    <h2>Select Model</h2>
    <div class="controls">
      <select id="sortBy">
        <option value="created">Sort by Created Date</option>
        <option value="context_length">Sort by Context Length</option>
        <option value="capabilities">Sort by Capabilities</option>
        <option value="id">Sort by ID</option>
      </select>
      <select id="generation">
        <option value="none">All Generations</option>
        <option value="4">GPT-4 Only</option>
        <option value="3.5">GPT-3.5 Only</option>
        <option value="3">GPT-3 Only</option>
      </select>
      <select id="capability">
        <option value="none">All Capabilities</option>
        <option value="vision">Vision</option>
        <option value="function">Function Calling</option>
        <option value="text">Text</option>
      </select>
      <button onclick="refreshModels()">Refresh Models</button>
      <div class="loading" id="modelLoading">Loading models...</div>
    </div>
    <div id="modelError"></div>
    <div id="modelList"></div>
  </div>

  <form id="upload-form">
    <label for="image">Select Image (optional):</label>
```

## Snippet 55
Lines 683-685

```Python
<input type="text" id="prompt" name="prompt" size="80" value="Generate descriptive alt text for the visually impaired for social media"><br><br>
    <button type="submit">Submit</button>
    <div class="loading" id="generateLoading">Generating response...</div>
```

## Snippet 56
Lines 686-692

```Python
</form>
  <h2>Response:</h2>
  <div id="output"></div>

  <script>
    let selectedModel = null;
```

## Snippet 57
Lines 693-702

```Python
async function fetchModels() {
      const sortBy = document.getElementById('sortBy').value;
      const generation = document.getElementById('generation').value;
      const capability = document.getElementById('capability').value;

      try {
        document.getElementById('modelLoading').style.display = 'block';
        document.getElementById('modelError').textContent = '';

        const response = await fetch(`/models?sort_by=${sortBy}&generation=${generation}&capability=${capability}`);
```

## Snippet 58
Lines 703-724

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
            <div class="model-info">
```

## Snippet 59
Lines 725-727

```Python
<span>Context: ${model.context_length.toLocaleString()} tokens</span>
              <span>Released: ${model.created_str}</span>
              ${model.version ? `<span>Version: ${model.version}</span>` : ''}
```

## Snippet 60
Lines 740-746

```Python
function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelectorAll('.model-card').forEach(card => {
        card.classList.toggle('selected', card.querySelector('strong').textContent === modelId);
      });
    }
```

## Snippet 61
Lines 747-753

```Python
function refreshModels() {
      fetchModels();
    }

    document.getElementById("upload-form").addEventListener("submit", async function(e) {
      e.preventDefault();
```

## Snippet 62
Lines 754-764

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
```

## Snippet 63
Lines 765-775

```Python
if (imageInput.files[0]) {
        formData.append("image", imageInput.files[0]);
      }
      formData.append("prompt", promptInput.value);
      formData.append("model", selectedModel);

      try {
        const response = await fetch("/generate", {
          method: "POST",
          body: formData
        });
```

## Snippet 64
Lines 776-782

```Python
if (!response.ok) {
          document.getElementById("output").textContent = "Error: " + await response.text();
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
```

## Snippet 65
Lines 786-789

```Python
if (value) {
            const chunk = decoder.decode(value);
            document.getElementById("output").textContent += chunk;
          }
```

## Snippet 66
Lines 806-812

```Python
def get_models():
    """Endpoint to get available OpenAI models."""
    try:
        sort_by = request.args.get("sort_by", "created")
        generation = request.args.get("generation")
        capability = request.args.get("capability")
```

## Snippet 67
Lines 818-830

```Python
if not api_key:
            return "API key not set", 500

        chat = OpenAIChat(api_key)

        # Get models with the specified sorting and filtering
        models = chat.list_models(
            sort_by=sort_by,
            page=1,
            page_size=1000,  # Get all models
            generation=generation
        )
```

## Snippet 68
Lines 850-871

```Python
if "image" in request.files and request.files["image"].filename:
        image_file = request.files["image"]
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
        try:
            image_file.save(temp_file.name)
            temp_file.close()
            # Instantiate OpenAIChat and encode the image
            api_key = os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
            chat = OpenAIChat(api_key)
            image_data = chat.encode_image(temp_file.name)
        except Exception as e:
            return f"Error processing image: {str(e)}", 500
        finally:
            try:
                os.remove(temp_file.name)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)

    api_key = os.getenv("OPENAI_API_KEY", DEFAULT_API_KEY)
    chat = OpenAIChat(api_key)
```

## Snippet 69
Lines 885-890

```Python
if __name__ == "__main__":
    # To run CLI interface, call main_cli()
    # Uncomment the following line to test in terminal:
    # main_cli()
    # To run the Flask web server, simply run this file:
    app.run(debug=True, port=6003)
```

