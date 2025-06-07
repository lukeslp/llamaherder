# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_chat_mistral.py

File: `toollama/API/--storage/processed-flask-chat/flask_chat_mistral.py`  
Language: Python  
Extracted: 2025-06-07 05:17:50  

## Snippet 1
Lines 1-10

```Python
import os
import sys
import io
import json
import base64
import requests
from datetime import datetime
from PIL import Image
from flask import Flask, request, Response, render_template_string, stream_with_context
```

## Snippet 2
Lines 15-28

```Python
def __init__(self, api_key: str):
        """Initialize the Mistral client with the provided API key."""
        self.api_key = api_key
        self.api_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Initialize with system message
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 3
Lines 29-44

```Python
def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 5,
        capability_filter: str = None,
        category_filter: str = None
    ):
        """
        Retrieve available Mistral models with pagination.
        In case of API failure, fallback models are returned.
        """
        try:
            response = requests.get(f"{self.api_url}/models", headers=self.headers)
            response.raise_for_status()
            models = []
```

## Snippet 4
Lines 56-59

```Python
elif "pixtral" in model_id:
                    category = "pixtral"
                else:
                    category = "mistral"
```

## Snippet 5
Lines 62-66

```Python
if category_filter and category_filter != category:
                    continue
                models.append({
                    "id": model["id"],
                    "name": model["name"] or model["id"].replace("-", " ").title(),
```

## Snippet 6
Lines 67-74

```Python
"description": model["description"] or f"Mistral {model['id']} model",
                    "context_length": model["max_context_length"],
                    "created_at": datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                    "created": model["created"],
                    "capabilities": capabilities,
                    "category": category,
                    "owned_by": model["owned_by"],
                    "deprecated_at": model.get("deprecation")
```

## Snippet 7
Lines 78-84

```Python
elif sort_by == "context_length":
                models.sort(key=lambda x: x["context_length"], reverse=True)
            else:
                models.sort(key=lambda x: x["id"], reverse=True)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
```

## Snippet 8
Lines 85-118

```Python
except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            # Fallback models
            fallback_models = [{
                "id": "mistral-tiny",
                "name": "Mistral Tiny",
                "description": "Mistral Tiny model",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat"],
                "category": "mistral",
                "owned_by": "mistralai"
            }, {
                "id": "mistral-small",
                "name": "Mistral Small",
                "description": "Mistral Small model",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
            }, {
                "id": "mistral-medium",
                "name": "Mistral Medium",
                "description": "Mistral Medium model",
                "context_length": 32768,
                "created_at": "2024-03-01",
                "created": datetime.now().timestamp(),
                "capabilities": ["chat", "functions"],
                "category": "mistral",
                "owned_by": "mistralai"
            }]
```

## Snippet 9
Lines 123-126

```Python
start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return fallback_models[start_idx:end_idx]
```

## Snippet 10
Lines 127-137

```Python
def create_test_image(self, color: str = 'red', size: tuple = (100, 100)):
        """Create a test image and return its base64 encoding."""
        try:
            img = Image.new('RGB', size, color=color)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error creating test image: {e}", file=sys.stderr)
            return None
```

## Snippet 11
Lines 138-141

```Python
def load_image_from_file(self, file_path: str):
        """Load an image from a file and return its base64 encoding."""
        try:
            with Image.open(file_path) as img:
```

## Snippet 12
Lines 142-144

```Python
if img.format not in ['PNG', 'JPEG', 'WEBP', 'GIF']:
                    print(f"Unsupported image format: {img.format}.", file=sys.stderr)
                    return None
```

## Snippet 13
Lines 145-147

```Python
if img.format == 'GIF' and getattr(img, 'is_animated', False):
                    print("Animated GIFs are not supported.", file=sys.stderr)
                    return None
```

## Snippet 14
Lines 152-154

```Python
if img_byte_arr.tell() > 10 * 1024 * 1024:
                    print("Image file size exceeds 10MB limit.", file=sys.stderr)
                    return None
```

## Snippet 15
Lines 155-161

```Python
if img.size[0] > 1024 or img.size[1] > 1024:
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0]*ratio), int(img.size[1]*ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format)
                return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
```

## Snippet 16
Lines 162-165

```Python
except Exception as e:
            print(f"Error loading image: {e}", file=sys.stderr)
            return None
```

## Snippet 17
Lines 166-170

```Python
def format_message_with_image(self, message: str, image_data=None, is_url: bool = False):
        """
        Format a message with optional image data.
        If image_data is provided, returns a list of content objects.
        """
```

## Snippet 18
Lines 177-182

```Python
if len(image_data) > 8:
            print("Warning: Maximum 8 images per request. Using first 8 images.", file=sys.stderr)
            image_data = image_data[:8]

        content = [{"type": "text", "text": message}]
```

## Snippet 19
Lines 184-195

```Python
if is_url:
                content.append({"type": "image_url", "image_url": img})
            else:
                # For base64 encoded images, use data URI format
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img}",
                        "detail": "high"
                    }
                })
```

## Snippet 20
Lines 199-202

```Python
def format_message_with_file(self, message: str, file_data=None):
        """
        Format a message with optional file data.
        """
```

## Snippet 21
Lines 208-211

```Python
for file_id in file_data:
            content.append({"type": "file", "file_id": file_id})
        return content
```

## Snippet 22
Lines 212-229

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = "mistral-tiny",
        temperature: float = 0.7,
        max_tokens: int = None,
        top_p: float = 1.0,
        safe_prompt: bool = True,
        image_data=None,
        is_url: bool = False,
        file_data=None
    ):
        """
        Stream a chat response from Mistral.
        """
        try:
            # Format message content based on whether we have images or files
            content = message
```

## Snippet 23
Lines 230-232

```Python
if image_data:
                print(f"Processing message with image data (is_url={is_url})")
                content = self.format_message_with_image(message, image_data, is_url)
```

## Snippet 24
Lines 233-249

```Python
elif file_data:
                print(f"Processing message with file data")
                content = self.format_message_with_file(message, file_data)

            # Add user message to history
            self.conversation_history.append({"role": "user", "content": content})

            # Prepare API payload
            payload = {
                "model": model,
                "messages": self.conversation_history,
                "stream": True,
                "temperature": temperature,
                "top_p": top_p,
                "safe_prompt": safe_prompt
            }
```

## Snippet 25
Lines 250-254

```Python
if max_tokens:
                payload["max_tokens"] = max_tokens

            # Print debug info
            print(f"Sending request to Mistral API with model: {model}")
```

## Snippet 26
Lines 255-265

```Python
if image_data:
                print(f"Request includes image data")

            # Make API request
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True
            )
```

## Snippet 27
Lines 283-287

```Python
if line_text == "[DONE]":
                        continue
                    try:
                        data = json.loads(line_text)
                        content_chunk = data['choices'][0]['delta'].get('content', '')
```

## Snippet 28
Lines 288-290

```Python
if content_chunk:
                            full_response += content_chunk
                            yield content_chunk
```

## Snippet 29
Lines 291-296

```Python
except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 30
Lines 304-310

```Python
except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            self.conversation_history.pop()
            yield f"Error: {str(e)}"
```

## Snippet 31
Lines 311-317

```Python
def clear_conversation(self):
        """Clear conversation history (keeping only the system prompt)."""
        self.conversation_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 32
Lines 318-329

```Python
def upload_file(self, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                upload_headers = {"Authorization": f"Bearer {self.api_key}"}
                response = requests.post(f"{self.api_url}/files", headers=upload_headers, files=files)
                response.raise_for_status()
                return response.json().get("id")
        except Exception as e:
            print(f"Error uploading file: {e}", file=sys.stderr)
            return None
```

## Snippet 33
Lines 332-335

```Python
params = {"purpose": purpose} if purpose else {}
            response = requests.get(f"{self.api_url}/files", headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()["data"]
```

## Snippet 34
Lines 336-339

```Python
except Exception as e:
            print(f"Error listing files: {e}", file=sys.stderr)
            return []
```

## Snippet 35
Lines 340-348

```Python
def retrieve_file(self, file_id: str):
        try:
            response = requests.get(f"{self.api_url}/files/{file_id}", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error retrieving file: {e}", file=sys.stderr)
            return None
```

## Snippet 36
Lines 349-357

```Python
def delete_file(self, file_id: str):
        try:
            response = requests.delete(f"{self.api_url}/files/{file_id}", headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}", file=sys.stderr)
            return False
```

## Snippet 37
Lines 358-366

```Python
def get_file_content(self, file_id: str):
        try:
            response = requests.get(f"{self.api_url}/files/{file_id}/content", headers=self.headers)
            response.raise_for_status()
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}", file=sys.stderr)
            return None
```

## Snippet 38
Lines 367-375

```Python
def get_file_url(self, file_id: str):
        try:
            response = requests.post(f"{self.api_url}/files/{file_id}/download_url", headers=self.headers)
            response.raise_for_status()
            return response.json()["download_url"]
        except Exception as e:
            print(f"Error getting file URL: {e}", file=sys.stderr)
            return None
```

## Snippet 39
Lines 378-383

```Python
Encode an image file to base64 for use with the Mistral API.

        Args:
            file_path (str): Path to the image file

        Returns:
```

## Snippet 40
Lines 385-387

```Python
"""
        try:
            with Image.open(file_path) as img:
```

## Snippet 41
Lines 393-397

```Python
if img.size[0] > 1024 or img.size[1] > 1024:
                    ratio = min(1024/img.size[0], 1024/img.size[1])
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
```

## Snippet 42
Lines 398-406

```Python
# Save as JPEG for consistency
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=95)
                img_byte_arr.seek(0)

                # Encode to base64
                encoded = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
                print(f"Successfully encoded image, length: {len(encoded)}")
                return encoded
```

## Snippet 43
Lines 407-412

```Python
except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return None
```

## Snippet 44
Lines 415-421

```Python
# -------------------------------
app = Flask(__name__)

# Use your Mistral API key here or set the environment variable "MISTRAL_API_KEY"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "n8R347515VqP48oDHwBeL9BS6nW1L8zY")
chat_client = MistralChat(MISTRAL_API_KEY)
```

## Snippet 45
Lines 422-429

```Python
# HTML template (using render_template_string for self-containment)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Mistral Streaming Chat</title>
  <style>
```

## Snippet 46
Lines 436-441

```Python
</head>
<body>
  <h1>Mistral Streaming Chat</h1>
  <div>
    <label for="model">Select Model:</label>
    <select id="model">
```

## Snippet 47
Lines 446-449

```Python
</div>
  <div id="chat"></div>
  <form id="chat-form">
    <textarea id="message" rows="3" cols="60" placeholder="Enter your message"></textarea><br>
```

## Snippet 48
Lines 450-452

```Python
<input type="file" id="image" accept="image/*"><br>
    <button type="submit">Send</button>
    <button type="button" id="clear">Clear Chat</button>
```

## Snippet 49
Lines 453-462

```Python
</form>

  <script>
    const chatDiv = document.getElementById("chat");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message");
    const modelSelect = document.getElementById("model");
    const imageInput = document.getElementById("image");
    const clearButton = document.getElementById("clear");
```

## Snippet 50
Lines 463-473

```Python
function appendMessage(sender, text) {
      const msgDiv = document.createElement("div");
      msgDiv.className = "message " + sender;
      msgDiv.textContent = sender + ": " + text;
      chatDiv.appendChild(msgDiv);
      chatDiv.scrollTop = chatDiv.scrollHeight;
    }

    chatForm.addEventListener("submit", function(e) {
      e.preventDefault();
      const message = messageInput.value;
```

## Snippet 51
Lines 474-482

```Python
if (!message) return;

      appendMessage("user", message);
      messageInput.value = "";

      const model = modelSelect.value;
      const formData = new FormData();
      formData.append("message", message);
      formData.append("model", model);
```

## Snippet 52
Lines 483-486

```Python
if (imageInput.files[0]) {
        formData.append("image", imageInput.files[0]);
      }
```

## Snippet 53
Lines 487-490

```Python
fetch("/chat", { method: "POST", body: formData })
      .then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
```

## Snippet 54
Lines 493-496

```Python
if (done) return;
            const chunk = decoder.decode(value);
            appendMessage("assistant", chunk);
            read();
```

## Snippet 55
Lines 500-503

```Python
})
      .catch(error => {
        appendMessage("assistant", "Error: " + error);
      });
```

## Snippet 56
Lines 504-506

```Python
});

    clearButton.addEventListener("click", function() {
```

## Snippet 57
Lines 517-520

```Python
# Get a list of available models (using a larger page size for convenience)
    models = chat_client.list_models(page=1, page_size=100)
    return render_template_string(HTML_TEMPLATE, models=models)
```

## Snippet 58
Lines 522-527

```Python
def chat():
    message = request.form.get("message")
    model = request.form.get("model", "mistral-tiny")
    image_file = request.files.get("image")
    image_data = None
    is_url = False
```

## Snippet 59
Lines 528-532

```Python
if image_file:
        try:
            image_bytes = image_file.read()
            # Process image using Pillow
            img = Image.open(io.BytesIO(image_bytes))
```

## Snippet 60
Lines 533-537

```Python
if img.mode != "RGB":
                img = img.convert("RGB")
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format="PNG")
            image_data = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
```

## Snippet 61
Lines 547-550

```Python
def clear():
    chat_client.clear_conversation()
    return ("", 204)
```

