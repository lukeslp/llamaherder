# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_alt_ollama.py

File: `toollama/API/--storage/processed-flask-chat/flask_alt_ollama.py`  
Language: Python  
Extracted: 2025-06-07 05:17:51  

## Snippet 1
Lines 1-13

```Python
#!/usr/bin/env python
import os
import sys
import tempfile
import io
import json
import requests
from flask import Flask, request, render_template_string, Response
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image
```

## Snippet 2
Lines 19-23

```Python
def __init__(self, host: str = "http://localhost:11434"):
        """Initialize the Ollama client with the host URL."""
        self.host = host.rstrip('/')
        self.conversation_history = []
```

## Snippet 3
Lines 24-47

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
        Get available Ollama models with sorting and pagination.

        Args:
            sort_by (str): Field to sort by ('created', 'name', 'family', 'size')
            reverse (bool): Whether to reverse sort order
            page (int): Page number (1-based)
            page_size (int): Number of items per page
            capability_filter (Optional[str]): Filter by capability ('vision', 'text', etc)

        Returns:
            List[Dict]: List of available models with their details
        """
        try:
            # Get list of models
            response = requests.get(f"{self.host}/api/tags")
```

## Snippet 4
Lines 48-54

```Python
if not response.ok:
                raise Exception(f"Failed to fetch models: {response.text}")

            models_data = response.json().get('models', [])
            processed_models = []

            # Process each model
```

## Snippet 5
Lines 55-61

```Python
for model in models_data:
                try:
                    # Get detailed model info
                    details_response = requests.post(
                        f"{self.host}/api/show",
                        json={"name": model['name']}
                    )
```

## Snippet 6
Lines 62-70

```Python
if not details_response.ok:
                        continue

                    details = details_response.json()
                    model_details = details.get('details', {})

                    # Determine capabilities based on families
                    capabilities = ["text"]  # All models support text
                    families = model_details.get('families', [])
```

## Snippet 7
Lines 75-81

```Python
if capability_filter and capability_filter not in capabilities:
                        continue

                    # Create enhanced model info
                    model_info = {
                        "id": model['name'],
                        "name": model['name'],
```

## Snippet 8
Lines 82-91

```Python
"description": f"Ollama {model_details.get('family', '').upper()} model - {model_details.get('parameter_size', 'Unknown')} parameters",
                        "capabilities": capabilities,
                        "capability_count": len(capabilities),
                        "created": model.get('modified_at', ""),
                        "created_str": datetime.fromisoformat(model.get('modified_at', "").replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S"),
                        "family": model_details.get('family', ''),
                        "parameter_size": model_details.get('parameter_size', ''),
                        "quantization": model_details.get('quantization_level', ''),
                        "format": model_details.get('format', ''),
                        "owned_by": "ollama"
```

## Snippet 9
Lines 94-97

```Python
except Exception as e:
                    print(f"Error processing model {model['name']}: {e}", file=sys.stderr)
                    continue
```

## Snippet 10
Lines 105-115

```Python
elif sort_by == "capabilities":
                processed_models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by name
                processed_models.sort(key=lambda x: x["name"], reverse=reverse)

            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size

            return processed_models[start_idx:end_idx]
```

## Snippet 11
Lines 116-119

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []
```

## Snippet 12
Lines 120-127

```Python
def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.

        Args:
            image_path (str): Path to the image file

        Returns:
```

## Snippet 13
Lines 129-136

```Python
"""
        try:
            with open(image_path, "rb") as image_file:
                return b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None
```

## Snippet 14
Lines 137-145

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.

        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)

        Returns:
```

## Snippet 15
Lines 147-157

```Python
"""
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None
```

## Snippet 16
Lines 158-189

```Python
def stream_chat_response(
        self,
        prompt: str,
        model: str = "llava",
        image_data: Optional[str] = None,
        temperature: float = 0.7,
        options: Optional[Dict] = None
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Ollama.

        Args:
            prompt (str): The user's input message
            model (str): The Ollama model to use
            image_data (Optional[str]): Base64 encoded image data
            temperature (float): Response temperature (0.0 to 1.0)
            options (Optional[Dict]): Additional model options

        Yields:
            str: Chunks of the response text as they arrive
        """
        try:
            # Prepare the request data
            data = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": options or {
                    "temperature": temperature
                }
            }
```

## Snippet 17
Lines 191-200

```Python
if image_data:
                data["images"] = [image_data]

            # Make streaming request
            response = requests.post(
                f"{self.host}/api/generate",
                json=data,
                stream=True
            )
```

## Snippet 18
Lines 201-204

```Python
if not response.ok:
                raise Exception(f"API request failed: {response.text}")

            # Process streaming response
```

## Snippet 19
Lines 206-208

```Python
if line:
                    try:
                        chunk = json.loads(line)
```

## Snippet 20
Lines 214-217

```Python
except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)
            yield f"Error: {str(e)}"
```

## Snippet 21
Lines 218-221

```Python
def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []
```

## Snippet 22
Lines 224-234

```Python
# -------------------------------------------------------------------

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Ollama Chat Interface</title>
  <style>
```

## Snippet 23
Lines 237-244

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

## Snippet 24
Lines 247-253

```Python
.model-capabilities { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
    .capability-tag {
      background: #e0e0e0;
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
    }
```

## Snippet 25
Lines 254-262

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

## Snippet 26
Lines 265-272

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

## Snippet 27
Lines 274-301

```Python
</head>
<body>
  <h1>Ollama Chat Interface</h1>

  <div class="model-selector">
    <h2>Select Model</h2>
    <div class="controls">
      <select id="sortBy">
        <option value="created">Sort by Created Date</option>
        <option value="name">Sort by Name</option>
        <option value="family">Sort by Family</option>
        <option value="size">Sort by Size</option>
        <option value="capabilities">Sort by Capabilities</option>
      </select>
      <select id="capability">
        <option value="none">All Capabilities</option>
        <option value="vision">Vision</option>
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

## Snippet 28
Lines 304-306

```Python
<input type="text" id="prompt" name="prompt" size="80" value="Generate descriptive alt text for the visually impaired for social media"><br><br>
    <button type="submit">Submit</button>
    <div class="loading" id="generateLoading">Generating response...</div>
```

## Snippet 29
Lines 307-313

```Python
</form>
  <h2>Response:</h2>
  <div id="output"></div>

  <script>
    let selectedModel = null;
```

## Snippet 30
Lines 314-322

```Python
async function fetchModels() {
      const sortBy = document.getElementById('sortBy').value;
      const capability = document.getElementById('capability').value;

      try {
        document.getElementById('modelLoading').style.display = 'block';
        document.getElementById('modelError').textContent = '';

        const response = await fetch(`/models?sort_by=${sortBy}&capability=${capability}`);
```

## Snippet 31
Lines 323-353

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
              <span>Family: ${model.family}</span>
              <span>Size: ${model.parameter_size}</span>
              <span>Format: ${model.format}</span>
              <span>Created: ${model.created_str}</span>
            </div>
          `;

          modelList.appendChild(modelCard);
        });
```

## Snippet 32
Lines 361-367

```Python
function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelectorAll('.model-card').forEach(card => {
        card.classList.toggle('selected', card.querySelector('strong').textContent === modelId);
      });
    }
```

## Snippet 33
Lines 368-374

```Python
function refreshModels() {
      fetchModels();
    }

    document.getElementById("upload-form").addEventListener("submit", async function(e) {
      e.preventDefault();
```

## Snippet 34
Lines 375-385

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

## Snippet 35
Lines 386-396

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

## Snippet 36
Lines 397-403

```Python
if (!response.ok) {
          document.getElementById("output").textContent = "Error: " + await response.text();
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
```

## Snippet 37
Lines 407-410

```Python
if (value) {
            const chunk = decoder.decode(value);
            document.getElementById("output").textContent += chunk;
          }
```

## Snippet 38
Lines 427-432

```Python
def get_models():
    """Endpoint to get available Ollama models."""
    try:
        sort_by = request.args.get("sort_by", "created")
        capability = request.args.get("capability")
```

## Snippet 39
Lines 433-448

```Python
if capability == "none":
            capability = None

        # Initialize OllamaChat
        chat = OllamaChat()

        # Get models with the specified sorting and filtering
        models = chat.list_models(
            sort_by=sort_by,
            page=1,
            page_size=1000,  # Get all models
            capability_filter=capability
        )

        return models
```

## Snippet 40
Lines 462-481

```Python
if "image" in request.files and request.files["image"].filename:
        image_file = request.files["image"]
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
        try:
            image_file.save(temp_file.name)
            temp_file.close()
            # Encode the image
            chat = OllamaChat()
            image_data = chat.encode_image(temp_file.name)
        except Exception as e:
            return f"Error processing image: {str(e)}", 500
        finally:
            try:
                os.remove(temp_file.name)
            except Exception as cleanup_error:
                print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)

    chat = OllamaChat()
```

