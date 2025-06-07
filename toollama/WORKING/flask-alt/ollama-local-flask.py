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

# -------------------------------------------------------------------
# Ollama Chat Implementation
# -------------------------------------------------------------------

class OllamaChat:
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize the Ollama client with the host URL."""
        self.host = host.rstrip('/')
        self.conversation_history = []
        
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
            if not response.ok:
                raise Exception(f"Failed to fetch models: {response.text}")
            
            models_data = response.json().get('models', [])
            processed_models = []
            
            # Process each model
            for model in models_data:
                try:
                    # Get detailed model info
                    details_response = requests.post(
                        f"{self.host}/api/show",
                        json={"name": model['name']}
                    )
                    if not details_response.ok:
                        continue
                        
                    details = details_response.json()
                    model_details = details.get('details', {})
                    
                    # Determine capabilities based on families
                    capabilities = ["text"]  # All models support text
                    families = model_details.get('families', [])
                    if "clip" in families:
                        capabilities.append("vision")
                    
                    # Skip if doesn't match capability filter
                    if capability_filter and capability_filter not in capabilities:
                        continue
                    
                    # Create enhanced model info
                    model_info = {
                        "id": model['name'],
                        "name": model['name'],
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
                    }
                    processed_models.append(model_info)
                except Exception as e:
                    print(f"Error processing model {model['name']}: {e}", file=sys.stderr)
                    continue
            
            # Sort models
            if sort_by == "created":
                processed_models.sort(key=lambda x: x["created"], reverse=reverse)
            elif sort_by == "family":
                processed_models.sort(key=lambda x: x["family"], reverse=reverse)
            elif sort_by == "size":
                processed_models.sort(key=lambda x: x["parameter_size"], reverse=reverse)
            elif sort_by == "capabilities":
                processed_models.sort(key=lambda x: x["capability_count"], reverse=reverse)
            else:  # sort by name
                processed_models.sort(key=lambda x: x["name"], reverse=reverse)
            
            # Calculate pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return processed_models[start_idx:end_idx]
            
        except Exception as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return []

    def encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image file to base64.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[str]: Base64 encoded image data or None if encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                return b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}", file=sys.stderr)
            return None

    def create_test_image(self, color: str = 'red', size: tuple = (100, 100)) -> Optional[str]:
        """
        Create a test image and return its base64 encoding.
        
        Args:
            color (str): Color of the test image
            size (tuple): Size of the image in pixels (width, height)
            
        Returns:
            Optional[str]: Base64 encoded image data or None if creation fails
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
            
            # Add image if provided
            if image_data:
                data["images"] = [image_data]
            
            # Make streaming request
            response = requests.post(
                f"{self.host}/api/generate",
                json=data,
                stream=True
            )
            
            if not response.ok:
                raise Exception(f"API request failed: {response.text}")
            
            # Process streaming response
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            yield chunk["response"]
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            print(f"Error in stream_chat_response: {e}", file=sys.stderr)
            yield f"Error: {str(e)}"

    def clear_conversation(self):
        """Clear the conversation history."""
        self.conversation_history = []

# -------------------------------------------------------------------
# Flask Web UX Integration
# -------------------------------------------------------------------

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Ollama Chat Interface</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 2rem; }
    #output { white-space: pre-wrap; border: 1px solid #ccc; padding: 1rem; margin-top: 1rem; }
    .model-selector { margin-bottom: 1.5rem; }
    .model-card {
      border: 1px solid #ddd;
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 4px;
      cursor: pointer;
    }
    .model-card:hover { background-color: #f5f5f5; }
    .model-card.selected { background-color: #e3f2fd; border-color: #2196f3; }
    .model-capabilities { display: flex; gap: 0.5rem; margin-top: 0.5rem; }
    .capability-tag {
      background: #e0e0e0;
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
    }
    .controls { display: flex; gap: 1rem; align-items: center; margin-bottom: 1rem; }
    button { 
      padding: 0.5rem 1rem; 
      background: #2196f3; 
      color: white; 
      border: none; 
      border-radius: 4px;
      cursor: pointer;
    }
    button:hover { background: #1976d2; }
    .loading { display: none; margin-left: 1rem; }
    #modelError { color: red; margin: 1rem 0; }
    .model-info {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
      font-size: 0.9rem;
      color: #666;
    }
  </style>
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
    <input type="file" id="image" name="image" accept="image/*"><br><br>
    <label for="prompt">Prompt:</label>
    <input type="text" id="prompt" name="prompt" size="80" value="Generate descriptive alt text for the visually impaired for social media"><br><br>
    <button type="submit">Submit</button>
    <div class="loading" id="generateLoading">Generating response...</div>
  </form>
  <h2>Response:</h2>
  <div id="output"></div>

  <script>
    let selectedModel = null;
    
    async function fetchModels() {
      const sortBy = document.getElementById('sortBy').value;
      const capability = document.getElementById('capability').value;
      
      try {
        document.getElementById('modelLoading').style.display = 'block';
        document.getElementById('modelError').textContent = '';
        
        const response = await fetch(`/models?sort_by=${sortBy}&capability=${capability}`);
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
      } catch (err) {
        document.getElementById('modelError').textContent = `Error loading models: ${err.message}`;
      } finally {
        document.getElementById('modelLoading').style.display = 'none';
      }
    }
    
    function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelectorAll('.model-card').forEach(card => {
        card.classList.toggle('selected', card.querySelector('strong').textContent === modelId);
      });
    }
    
    function refreshModels() {
      fetchModels();
    }
    
    document.getElementById("upload-form").addEventListener("submit", async function(e) {
      e.preventDefault();
      
      if (!selectedModel) {
        alert('Please select a model first');
        return;
      }
      
      document.getElementById("output").textContent = "";
      document.getElementById("generateLoading").style.display = 'block';
      
      const formData = new FormData();
      const imageInput = document.getElementById("image");
      const promptInput = document.getElementById("prompt");
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
        if (!response.ok) {
          document.getElementById("output").textContent = "Error: " + await response.text();
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        while (!done) {
          const {value, done: doneReading} = await reader.read();
          done = doneReading;
          if (value) {
            const chunk = decoder.decode(value);
            document.getElementById("output").textContent += chunk;
          }
        }
      } catch (err) {
        document.getElementById("output").textContent = "Error: " + err;
      } finally {
        document.getElementById("generateLoading").style.display = 'none';
      }
    });
    
    // Initial load
    fetchModels();
  </script>
</body>
</html>
"""

@app.route("/models", methods=["GET"])
def get_models():
    """Endpoint to get available Ollama models."""
    try:
        sort_by = request.args.get("sort_by", "created")
        capability = request.args.get("capability")
        
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
        
    except Exception as e:
        return str(e), 500

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.form.get("prompt", "Generate descriptive alt text for the visually impaired for social media")
    model = request.form.get("model", "llava")  # Get selected model
    image_data = None

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

    def generate_response():
        try:
            for chunk in chat.stream_chat_response(prompt, model=model, image_data=image_data):
                yield chunk
        except Exception as e:
            yield f"\nError: {str(e)}"

    return Response(generate_response(), mimetype="text/plain")

if __name__ == "__main__":
    app.run(debug=True, port=5086) 