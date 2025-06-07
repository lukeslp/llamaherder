# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_alt_unified.py

File: `toollama/API/--storage/processed-flask-chat/flask_alt_unified.py`  
Language: Python  
Extracted: 2025-06-07 05:17:48  

## Snippet 1
Lines 1-37

```Python
#!/usr/bin/env python
import os
import sys
import tempfile
import io
import json
import requests
from flask import Flask, request, render_template_string, Response, jsonify
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image
import anthropic
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Coze SDK
try:
    from cozepy import Coze, TokenAuth, Message, ChatEventType, MessageObjectString
except Exception as e:
    logger.error(f"Failed to import cozepy: {str(e)}")
    Coze = TokenAuth = Message = ChatEventType = MessageObjectString = None

# Import our provider-specific implementations
from flask_alt_anthropic import AnthropicChat
from flask_alt_openai import OpenAIChat
from flask_alt_ollama import OllamaChat
from flask_chat_perplexity import PerplexityChat
from flask_chat_mistral import MistralChat
from flask_chat_cohere import CohereChat
from flask_chat_xai import XAIChat
from flask_chat_coze import CozeChat, COZE_AUTH_TOKEN, COZE_BOT_ID, COZE_TTS_BOT_ID
```

## Snippet 2
Lines 40-51

```Python
# -------------------------------------------------------------------

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "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"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY") or "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"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "n8R347515VqP48oDHwBeL9BS6nW1L8zY"
COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "8K2VDJ784DPHN57zYauE03mGuslFuaxBW1NUY1LO"
XAI_API_KEY = os.getenv("XAI_API_KEY") or "xai-8zAk5VIaL3Vxpu3fO3r2aiWqqeVAZ173X04VK2R1m425uYpWOIOQJM3puq1Q38xJ2sHfbq3mX4PBxJXC"

# Initialize Coze client
coze_raw_client = None
try:
```

## Snippet 3
Lines 52-56

```Python
if Coze and TokenAuth and COZE_AUTH_TOKEN:
        try:
            logger.info("Initializing Coze client")
            coze_raw_client = Coze(auth=TokenAuth(token=COZE_AUTH_TOKEN))
            # Verify the client connection works by checking an attribute
```

## Snippet 4
Lines 57-60

```Python
if hasattr(coze_raw_client, 'conversations'):
                logger.info("Coze client initialized successfully")
            else:
                logger.warning("Coze client initialized but missing expected attributes")
```

## Snippet 5
Lines 61-63

```Python
except Exception as e:
            logger.error(f"Failed to initialize Coze client: {str(e)}")
            coze_raw_client = None
```

## Snippet 6
Lines 66-77

```Python
except Exception as e:
    logger.error(f"Unexpected error during Coze client setup: {str(e)}")
    coze_raw_client = None

# Initialize provider clients
anthropic_client = AnthropicChat(ANTHROPIC_API_KEY)
openai_client = OpenAIChat(OPENAI_API_KEY)
ollama_client = OllamaChat()
perplexity_client = PerplexityChat(PERPLEXITY_API_KEY)
mistral_client = MistralChat(MISTRAL_API_KEY)
cohere_client = CohereChat(COHERE_API_KEY)
xai_client = XAIChat(XAI_API_KEY)
```

## Snippet 7
Lines 82-123

```Python
# -------------------------------------------------------------------

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Unified LLM Interface</title>
  <style>
    :root {
      --bg-primary: #1a1a1a;
      --bg-secondary: #2d2d2d;
      --bg-tertiary: #383838;
      --text-primary: #e0e0e0;
      --text-secondary: #b0b0b0;
      --accent-primary: #2196f3;
      --accent-secondary: #1976d2;
      --border-color: #404040;
      --error-color: #f44336;
      --success-color: #4caf50;
    }

    body {
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem;
      background: var(--bg-primary);
      color: var(--text-primary);
    }

    #output {
      white-space: pre-wrap;
      border: 1px solid var(--border-color);
      padding: 1rem;
      margin-top: 1rem;
      background: var(--bg-secondary);
      border-radius: 4px;
    }
```

## Snippet 8
Lines 124-134

```Python
.model-selector { margin-bottom: 1.5rem; }

    .model-card {
      border: 1px solid var(--border-color);
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 4px;
      cursor: pointer;
      background: var(--bg-secondary);
    }
```

## Snippet 9
Lines 135-172

```Python
.model-card:hover { background: var(--bg-tertiary); }
    .model-card.selected {
      background: var(--accent-primary);
      border-color: var(--accent-secondary);
    }

    .model-capabilities {
      display: flex;
      gap: 0.5rem;
      margin-top: 0.5rem;
      flex-wrap: wrap;
    }

    .capability-tag {
      background: var(--bg-tertiary);
      padding: 0.2rem 0.5rem;
      border-radius: 12px;
      font-size: 0.8rem;
      color: var(--text-secondary);
    }

    .controls {
      display: flex;
      gap: 1rem;
      align-items: center;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    button {
      padding: 0.5rem 1rem;
      background: var(--accent-primary);
      color: var(--text-primary);
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
```

## Snippet 10
Lines 173-416

```Python
button:hover { background: var(--accent-secondary); }

    .loading {
      display: none;
      margin-left: 1rem;
      color: var(--text-secondary);
    }

    #modelError {
      color: var(--error-color);
      margin: 1rem 0;
    }

    .model-info {
      display: flex;
      justify-content: space-between;
      margin-top: 0.5rem;
      font-size: 0.9rem;
      color: var(--text-secondary);
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .provider-selector {
      margin-bottom: 2rem;
      padding: 1rem;
      background: var(--bg-secondary);
      border-radius: 4px;
    }

    .provider-btn {
      padding: 0.5rem 1rem;
      margin-right: 0.5rem;
      border: 2px solid transparent;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      cursor: pointer;
      border-radius: 4px;
    }

    .provider-btn.active {
      border-color: var(--accent-primary);
      background: var(--accent-primary);
    }

    .provider-info {
      margin-top: 1rem;
      font-size: 0.9rem;
      color: var(--text-secondary);
    }

    .mode-selector {
      margin-bottom: 1rem;
      padding: 1rem;
      background: var(--bg-secondary);
      border-radius: 4px;
    }

    .mode-btn {
      padding: 0.5rem 1rem;
      margin-right: 0.5rem;
      border: 2px solid transparent;
      background: var(--bg-tertiary);
      color: var(--text-primary);
      cursor: pointer;
      border-radius: 4px;
    }

    .mode-btn.active {
      border-color: var(--accent-primary);
      background: var(--accent-primary);
    }

    .chat-history {
      border: 1px solid var(--border-color);
      padding: 1rem;
      margin: 1rem 0;
      max-height: 400px;
      overflow-y: auto;
      border-radius: 4px;
      background: var(--bg-secondary);
    }

    .chat-message {
      margin: 0.5rem 0;
      padding: 0.5rem;
      border-radius: 4px;
    }

    .chat-message.user {
      background: var(--accent-primary);
      margin-left: 2rem;
      color: var(--text-primary);
    }

    .chat-message.assistant {
      background: var(--bg-tertiary);
      margin-right: 2rem;
      color: var(--text-primary);
    }

    select, input[type="text"] {
      background: var(--bg-tertiary);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      padding: 0.5rem;
      border-radius: 4px;
      width: 100%;
      max-width: 300px;
    }

    select:focus, input[type="text"]:focus {
      outline: none;
      border-color: var(--accent-primary);
    }

    input[type="file"] {
      color: var(--text-primary);
    }

    .chat-interface {
      display: none;
      flex-direction: column;
      height: 600px;
      background: var(--bg-secondary);
      border-radius: 4px;
      border: 1px solid var(--border-color);
      margin-top: 1rem;
    }

    .chat-interface.visible {
      display: flex;
    }

    .chat-history {
      flex-grow: 1;
      padding: 1rem;
      margin: 0;
      overflow-y: auto;
      border-radius: 4px 4px 0 0;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
    }

    .chat-input-area {
      padding: 1rem;
      background: var(--bg-tertiary);
      border-radius: 0 0 4px 4px;
      display: flex;
      gap: 1rem;
      align-items: center;
    }

    .chat-input-area input[type="text"] {
      flex-grow: 1;
      max-width: none;
    }

    .image-interface {
      display: none;
      padding: 1rem;
      background: var(--bg-secondary);
      border-radius: 4px;
      margin-top: 1rem;
      border: 1px solid var(--border-color);
    }

    .image-interface.visible {
      display: block;
    }

    .image-upload-area {
      border: 2px dashed var(--border-color);
      padding: 2rem;
      text-align: center;
      margin-bottom: 1rem;
      border-radius: 4px;
      background: var(--bg-tertiary);
      cursor: pointer;
    }

    .image-upload-area:hover {
      border-color: var(--accent-primary);
    }

    .image-preview {
      max-width: 100%;
      max-height: 300px;
      margin: 1rem 0;
      display: none;
    }

    .image-preview.visible {
      display: block;
    }

    .model-dropdown {
      position: relative;
      width: 100%;
      max-width: 300px;
    }

    .model-dropdown-btn {
      width: 100%;
      text-align: left;
      padding: 0.5rem;
      background: var(--bg-tertiary);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      border-radius: 4px;
      cursor: pointer;
    }

    .model-dropdown-content {
      display: none;
      position: absolute;
      top: 100%;
      left: 0;
      width: 100%;
      max-height: 400px;
      overflow-y: auto;
      background: var(--bg-tertiary);
      border: 1px solid var(--border-color);
      border-radius: 4px;
      z-index: 1000;
    }

    .model-dropdown-content.visible {
      display: block;
    }

    .model-option {
      padding: 0.5rem;
      cursor: pointer;
    }

    .model-option:hover {
      background: var(--bg-primary);
    }

    .model-option.selected {
      background: var(--accent-primary);
    }
```

## Snippet 11
Lines 429-452

```Python
</head>
<body>
  <h1>Unified LLM Interface</h1>

  <div class="mode-selector">
    <h2>Select Mode</h2>
    <button class="mode-btn active" data-mode="chat" onclick="selectMode('chat')">Chat</button>
    <button class="mode-btn" data-mode="image" onclick="selectMode('image')">Image Analysis</button>
  </div>

  <div class="provider-selector">
    <h2>Select Provider</h2>
    <div>
      <button class="provider-btn" data-provider="anthropic" onclick="selectProvider('anthropic')">Anthropic Claude</button>
      <button class="provider-btn" data-provider="openai" onclick="selectProvider('openai')">OpenAI GPT</button>
      <button class="provider-btn" data-provider="ollama" onclick="selectProvider('ollama')">Local Ollama</button>
      <button class="provider-btn" data-provider="perplexity" onclick="selectProvider('perplexity')">Perplexity</button>
      <button class="provider-btn" data-provider="mistral" onclick="selectProvider('mistral')">Mistral</button>
      <button class="provider-btn" data-provider="cohere" onclick="selectProvider('cohere')">Cohere</button>
      <button class="provider-btn" data-provider="xai" onclick="selectProvider('xai')">X.AI Grok</button>
      <button class="provider-btn" data-provider="coze" onclick="selectProvider('coze')">Coze Bots</button>
    </div>
    <div class="provider-info">
      <div id="anthropic-info" style="display: none">
```

## Snippet 12
Lines 454-461

```Python
</div>
      <div id="openai-info" style="display: none">
        Using OpenAI's GPT models with vision capabilities.
      </div>
      <div id="ollama-info" style="display: none">
        Using locally hosted Ollama models (requires Ollama to be running).
      </div>
      <div id="perplexity-info" style="display: none">
```

## Snippet 13
Lines 477-505

```Python
</div>

  <div class="model-selector">
    <h2>Select Model</h2>
    <div class="controls" id="provider-controls">
      <!-- Provider-specific controls will be inserted here -->
    </div>
    <div id="modelError"></div>
    <div class="model-dropdown">
      <button class="model-dropdown-btn" onclick="toggleModelDropdown()">Select a model...</button>
      <div class="model-dropdown-content" id="modelList"></div>
    </div>
  </div>

  <!-- Chat Interface -->
  <div class="chat-interface" id="chatInterface">
    <div class="chat-history" id="chatHistory"></div>
    <div class="chat-input-area">
      <input type="text" id="chatPrompt" placeholder="Enter your message or question here..." value="How can I help you today?">
      <button onclick="sendChatMessage()">Send</button>
      <button onclick="clearChat()">Clear Chat</button>
      <div class="loading" id="chatLoading">Generating response...</div>
    </div>
  </div>

  <!-- Image Analysis Interface -->
  <div class="image-interface" id="imageInterface">
    <div class="image-upload-area" onclick="triggerImageUpload()">
      <p>Click to upload an image or drag and drop here</p>
```

## Snippet 14
Lines 507-510

```Python
</div>
    <img id="imagePreview" class="image-preview" alt="Preview">
    <div style="margin-top: 1rem;">
      <label for="imagePrompt">Prompt:</label>
```

## Snippet 15
Lines 511-513

```Python
<input type="text" id="imagePrompt" value="Generate descriptive alt text for the visually impaired for social media" style="margin: 0.5rem 0; display: block;">
      <button onclick="analyzeImage()">Analyze Image</button>
      <div class="loading" id="imageLoading">Analyzing image...</div>
```

## Snippet 16
Lines 516-519

```Python
</div>

  <script>
    // Server-provided constants
```

## Snippet 17
Lines 521-575

```Python
const COZE_TTS_BOT_ID = "{{ COZE_TTS_BOT_ID }}";

    let selectedModel = null;
    let currentProvider = null;
    let currentMode = 'chat';

    const providerControls = {
      anthropic: `
        <select id="sortBy">
          <option value="created">Sort by Created Date</option>
          <option value="capabilities">Sort by Capabilities</option>
          <option value="id">Sort by ID</option>
        </select>
        <select id="capability">
          <option value="none">All Capabilities</option>
          <option value="vision">Vision</option>
          <option value="text">Text</option>
          <option value="code">Code</option>
          <option value="analysis">Analysis</option>
        </select>
      `,
      openai: `
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
        </select>
        <select id="capability">
          <option value="none">All Capabilities</option>
          <option value="vision">Vision</option>
          <option value="function">Function Calling</option>
          <option value="text">Text</option>
        </select>
      `,
      ollama: `
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
      `,
      perplexity: `
```

## Snippet 18
Lines 578-630

```Python
`,
      mistral: `
        <select id="sortBy">
          <option value="created">Sort by Created Date</option>
          <option value="context_length">Sort by Context Length</option>
          <option value="capabilities">Sort by Capabilities</option>
          <option value="id">Sort by ID</option>
        </select>
        <select id="capability">
          <option value="none">All Capabilities</option>
          <option value="chat">Chat</option>
          <option value="function">Function Calling</option>
          <option value="vision">Vision</option>
        </select>
        <select id="category">
          <option value="none">All Categories</option>
          <option value="mistral">Mistral</option>
          <option value="mixtral">Mixtral</option>
          <option value="pixtral">Pixtral</option>
        </select>
      `,
      cohere: `
        <select id="sortBy">
          <option value="created">Sort by Created Date</option>
          <option value="capabilities">Sort by Capabilities</option>
          <option value="id">Sort by ID</option>
        </select>
        <select id="capability">
          <option value="none">All Capabilities</option>
          <option value="chat">Chat</option>
          <option value="finetuned">Fine-tuned</option>
        </select>
      `,
      xai: `
        <select id="sortBy">
          <option value="created">Sort by Created Date</option>
          <option value="capabilities">Sort by Capabilities</option>
          <option value="id">Sort by ID</option>
        </select>
        <select id="capability">
          <option value="none">All Capabilities</option>
          <option value="images">Vision</option>
          <option value="text">Text</option>
          <option value="code">Code</option>
        </select>
      `,
      coze: `
        <select id="botType">
          <option value="all">All Bot Types</option>
          <option value="vision">Alt Text Generator</option>
          <option value="audio">TTS Generator</option>
        </select>
      `
```

## Snippet 19
Lines 633-645

```Python
// Default models for alt text mode
    const defaultAltTextModels = {
      anthropic: "claude-3-haiku-20240307",
      openai: "gpt-4o-mini",
      ollama: "coolhand/altllama:13b",
      mistral: "pixtral-large-2411",
      xai: "grok-2-vision-1212",
      coze: COZE_TTS_BOT_ID // Will be replaced with actual bot ID from server
    };

    // Track seen models to prevent duplicates
    let seenModelIds = new Set();
```

## Snippet 20
Lines 646-663

```Python
function selectMode(mode) {
      currentMode = mode;

      // Update UI
      document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mode === mode);
      });

      // Show/hide appropriate interface
      document.getElementById('chatInterface').classList.toggle('visible', mode === 'chat');
      document.getElementById('imageInterface').classList.toggle('visible', mode === 'image');

      // Clear existing content and history
      clearChat();
      document.getElementById('chatHistory').innerHTML = '';
      document.getElementById('chatPrompt').value = 'How can I help you today?';
      document.getElementById('imagePreview').classList.remove('visible');
      document.getElementById('imageOutput').textContent = '';
```

## Snippet 21
Lines 664-673

```Python
document.getElementById('imagePrompt').value = 'Generate descriptive alt text for the visually impaired for social media';
      document.getElementById('image').value = '';

      // Update provider buttons visibility
      document.querySelectorAll('.provider-btn').forEach(btn => {
        const provider = btn.dataset.provider;
        const supportsImages = ['anthropic', 'openai', 'ollama', 'xai', 'coze', 'mistral'].includes(provider);
        btn.style.display = (mode === 'image' && !supportsImages) ? 'none' : 'inline-block';
      });
```

## Snippet 22
Lines 677-680

```Python
} else if (currentProvider) {
        // Refresh models when mode changes with same provider
        fetchModels();
      }
```

## Snippet 23
Lines 683-715

```Python
function selectProvider(provider) {
      currentProvider = provider;

      // Update UI
      document.querySelectorAll('.provider-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.provider === provider);
      });

      // Update provider info
      document.querySelectorAll('[id$="-info"]').forEach(info => {
        info.style.display = 'none';
      });
      document.getElementById(`${provider}-info`).style.display = 'block';

      // Update controls
      document.getElementById('provider-controls').innerHTML = `
        ${providerControls[provider]}
        <button onclick="refreshModels()">Refresh Models</button>
        <div class="loading" id="modelLoading">Loading models...</div>
      `;

      // Clear existing content and history
      clearChat();
      document.getElementById('chatHistory').innerHTML = '';
      document.getElementById('chatPrompt').value = 'How can I help you today?';

      // Reset selection and fetch models
      selectedModel = null;
      // Reset seen models set
      seenModelIds = new Set();
      fetchModels();
    }
```

## Snippet 24
Lines 716-724

```Python
function appendMessage(role, content) {
      const chatHistory = document.getElementById('chatHistory');
      const messageDiv = document.createElement('div');
      messageDiv.className = `chat-message ${role}`;
      messageDiv.textContent = content;
      chatHistory.appendChild(messageDiv);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }
```

## Snippet 25
Lines 725-731

```Python
function clearChat() {
      document.getElementById('chatHistory').innerHTML = '';
      fetch('/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
```

## Snippet 26
Lines 737-752

```Python
if (!currentProvider) return;

      const sortBy = document.getElementById('sortBy')?.value || 'created';
      const capability = document.getElementById('capability')?.value;
      const generation = document.getElementById('generation')?.value;
      const category = document.getElementById('category')?.value;

      try {
        document.getElementById('modelLoading').style.display = 'block';
        document.getElementById('modelError').textContent = '';

        const params = new URLSearchParams({
          provider: currentProvider,
          sort_by: sortBy
        });
```

## Snippet 27
Lines 753-756

```Python
if (capability && capability !== 'none') {
          params.append('capability', capability);
        }
```

## Snippet 28
Lines 757-760

```Python
if (generation && generation !== 'none') {
          params.append('generation', generation);
        }
```

## Snippet 29
Lines 761-765

```Python
if (category && category !== 'none') {
          params.append('category', category);
        }

        // For image mode with Mistral, force Pixtral models only
```

## Snippet 30
Lines 766-771

```Python
if (currentMode === 'image' && currentProvider === 'mistral') {
          params.set('category', 'pixtral');
          params.set('capability', 'vision');
        }

        const response = await fetch(`/models?${params}`);
```

## Snippet 31
Lines 772-784

```Python
if (!response.ok) {
          throw new Error(await response.text());
        }

        const models = await response.json();
        const modelList = document.getElementById('modelList');
        modelList.innerHTML = '';

        // Reset seen model IDs
        seenModelIds = new Set();

        models.forEach(model => {
          // Skip duplicates
```

## Snippet 32
Lines 785-795

```Python
if (seenModelIds.has(model.id)) {
            return;
          }

          seenModelIds.add(model.id);

          const modelCard = document.createElement('div');
          modelCard.className = `model-card ${currentProvider}-provider${selectedModel === model.id ? ' selected' : ''}`;
          modelCard.onclick = () => selectModel(model.id);

          let modelInfo = '';
```

## Snippet 33
Lines 798-800

```Python
<span>Context: ${model.context_length?.toLocaleString()} tokens</span>
              <span>Released: ${model.created_str}</span>
              ${model.version ? `<span>Version: ${model.version}</span>` : ''}
```

## Snippet 34
Lines 802-808

```Python
} else if (currentProvider === 'ollama') {
            modelInfo = `
              <span>Family: ${model.family}</span>
              <span>Size: ${model.parameter_size}</span>
              <span>Format: ${model.format}</span>
              <span>Created: ${model.created_str}</span>
            `;
```

## Snippet 35
Lines 813-817

```Python
} else if (currentProvider === 'mistral') {
            modelInfo = `
              <span>Released: ${model.created_at}</span>
              <span>Owner: ${model.owned_by}</span>
            `;
```

## Snippet 36
Lines 818-840

```Python
} else {
            modelInfo = `
              <span>Released: ${model.created_at}</span>
              <span>Owner: ${model.owned_by}</span>
            `;
          }

          modelCard.innerHTML = `
            <strong>${model.name}</strong>
            <div>${model.description}</div>
            ${currentProvider !== 'perplexity' ? `
            <div class="model-capabilities">
              ${model.capabilities?.map(cap =>
                `<span class="capability-tag">${cap}</span>`
              ).join('') || ''}
            </div>
            ` : ''}
            <div class="model-info">
              ${modelInfo}
            </div>
          `;

          modelList.appendChild(modelCard);
```

## Snippet 37
Lines 857-860

```Python
} else if (models.length > 0) {
            // If default doesn't exist but we have models, select the first one
            selectModel(models[0].id);
          }
```

## Snippet 38
Lines 869-877

```Python
function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelector('.model-dropdown-btn').textContent = modelId;
      document.querySelectorAll('.model-option').forEach(option => {
        option.classList.toggle('selected', option.querySelector('strong').textContent === modelId);
      });
      document.querySelector('.model-dropdown-content').classList.remove('visible');
    }
```

## Snippet 39
Lines 878-881

```Python
function refreshModels() {
      fetchModels();
    }
```

## Snippet 40
Lines 882-885

```Python
function updateChatHistory(role, content, isPartial = false) {
      const chatHistory = document.getElementById('chatHistory');
      let messageDiv;
```

## Snippet 41
Lines 889-893

```Python
if (!messageDiv || !messageDiv.classList.contains(role)) {
          messageDiv = document.createElement('div');
          messageDiv.className = `chat-message ${role}`;
          chatHistory.appendChild(messageDiv);
        }
```

## Snippet 42
Lines 896-899

```Python
if (!chatHistory.lastElementChild || !chatHistory.lastElementChild.classList.contains(role)) {
          messageDiv = document.createElement('div');
          messageDiv.className = `chat-message ${role}`;
          chatHistory.appendChild(messageDiv);
```

## Snippet 43
Lines 909-915

```Python
function toggleModelDropdown() {
      const content = document.querySelector('.model-dropdown-content');
      content.classList.toggle('visible');
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
```

## Snippet 44
Lines 916-918

```Python
if (!e.target.closest('.model-dropdown')) {
        document.querySelector('.model-dropdown-content').classList.remove('visible');
      }
```

## Snippet 45
Lines 921-924

```Python
function triggerImageUpload() {
      document.getElementById('image').click();
    }
```

## Snippet 46
Lines 927-935

```Python
if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const preview = document.getElementById('imagePreview');
          preview.src = e.target.result;
          preview.classList.add('visible');
        };
        reader.readAsDataURL(file);
      }
```

## Snippet 47
Lines 938-953

```Python
// Drag and drop support for image upload
    const uploadArea = document.querySelector('.image-upload-area');

    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.style.borderColor = 'var(--accent-primary)';
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.style.borderColor = 'var(--border-color)';
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.style.borderColor = 'var(--border-color)';
      const file = e.dataTransfer.files[0];
```

## Snippet 48
Lines 954-956

```Python
if (file && file.type.startsWith('image/')) {
        const input = document.getElementById('image');
        input.files = e.dataTransfer.files;
```

## Snippet 49
Lines 962-979

```Python
if (!currentProvider || !selectedModel) {
        alert('Please select a provider and model first');
        return;
      }

      const promptInput = document.getElementById('chatPrompt');
      const prompt = promptInput.value;
      updateChatHistory('user', prompt);
      promptInput.value = '';

      document.getElementById('chatLoading').style.display = 'block';

      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('model', selectedModel);
      formData.append('provider', currentProvider);
      formData.append('mode', 'chat');
```

## Snippet 50
Lines 981-985

```Python
if (currentProvider === 'coze') {
        formData.append('user_id', 'user_' + Date.now());
      }

      await processResponse(formData, 'chat');
```

## Snippet 51
Lines 989-994

```Python
if (!currentProvider || !selectedModel) {
        alert('Please select a provider and model first');
        return;
      }

      const imageInput = document.getElementById('image');
```

## Snippet 52
Lines 995-1013

```Python
if (!imageInput.files[0]) {
        alert('Please upload an image first');
        return;
      }

      const promptInput = document.getElementById('imagePrompt');
      const prompt = promptInput.value;

      document.getElementById('imageLoading').style.display = 'block';
      document.getElementById('imageOutput').textContent = '';

      const formData = new FormData();
      formData.append('image', imageInput.files[0]);
      formData.append('prompt', prompt);
      formData.append('model', selectedModel);
      formData.append('provider', currentProvider);
      formData.append('mode', 'image');

      await processResponse(formData, 'image');
```

## Snippet 53
Lines 1016-1022

```Python
async function processResponse(formData, mode) {
      try {
        const response = await fetch('/generate', {
          method: 'POST',
          body: formData
        });
```

## Snippet 54
Lines 1023-1030

```Python
if (!response.ok) {
          throw new Error(await response.text());
        }

        let responseText = '';
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
```

## Snippet 55
Lines 1033-1041

```Python
if (done) break;

          const chunk = decoder.decode(value, {stream: true});

          // Create the line separator regex dynamically
          const lineSeparator = new RegExp('\\n|\\r\\n');
          // Split the chunk into lines to handle multiple JSON objects
          const lines = chunk.split(lineSeparator).filter(line => line.trim());
```

## Snippet 56
Lines 1042-1046

```Python
for (const line of lines) {
            try {
              // Try to parse as JSON
              const jsonData = JSON.parse(line);
```

## Snippet 57
Lines 1047-1051

```Python
if (jsonData.error) {
                throw new Error(jsonData.error);
              }

              // Handle different types of responses
```

## Snippet 58
Lines 1052-1054

```Python
if (jsonData.type === 'delta' && jsonData.content) {
                // Handle delta updates (streaming content)
                responseText += jsonData.content;
```

## Snippet 59
Lines 1055-1057

```Python
} else if (jsonData.type === 'complete') {
                // Handle completion message
                console.log('Response complete. Total tokens:', jsonData.tokens);
```

## Snippet 60
Lines 1058-1060

```Python
} else if (jsonData.type === 'start') {
                // Handle start message
                console.log('Streaming started');
```

## Snippet 61
Lines 1061-1063

```Python
} else {
                // Handle other JSON formats
                const chunkContent = jsonData.content || jsonData.text || jsonData;
```

## Snippet 62
Lines 1073-1075

```Python
if (line.trim()) {
                responseText += line;
              }
```

## Snippet 63
Lines 1112-1120

```Python
def get_models():
    """Endpoint to get available models from the selected provider."""
    try:
        provider = request.args.get("provider", "anthropic")
        sort_by = request.args.get("sort_by", "created")
        capability = request.args.get("capability")
        generation = request.args.get("generation")
        category = request.args.get("category")
```

## Snippet 64
Lines 1129-1135

```Python
if provider == "anthropic":
            models = anthropic_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
```

## Snippet 65
Lines 1136-1142

```Python
elif provider == "openai":
            models = openai_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                generation=generation
            )
```

## Snippet 66
Lines 1147-1154

```Python
elif provider == "mistral":
            models = mistral_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability,
                category_filter=category
            )
```

## Snippet 67
Lines 1155-1161

```Python
elif provider == "cohere":
            models = cohere_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
```

## Snippet 68
Lines 1162-1168

```Python
elif provider == "xai":
            models = xai_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
```

## Snippet 69
Lines 1170-1174

```Python
if not coze_client:
                return jsonify([
                    {
                        "id": "coze-service-unavailable",
                        "name": "Coze Service Unavailable",
```

## Snippet 70
Lines 1185-1194

```Python
else:  # ollama
            models = ollama_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )

        return jsonify(models)
```

## Snippet 71
Lines 1199-1203

```Python
def index():
    return render_template_string(HTML_TEMPLATE,
                                 COZE_BOT_ID=COZE_BOT_ID,
                                 COZE_TTS_BOT_ID=COZE_TTS_BOT_ID)
```

## Snippet 72
Lines 1205-1216

```Python
def generate():
    provider = request.form.get("provider", "anthropic")
    prompt = request.form.get("prompt", "How can I help you today?")
    model = request.form.get("model")
    mode = request.form.get("mode", "chat")
    current_user_id = request.form.get("user_id", "default_user")
    image_data = None
    image_path = None
    file_id = None

    logger.info(f"Generate request: provider={provider}, model={model}, mode={mode}")
```

## Snippet 73
Lines 1217-1226

```Python
if mode == "image" and "image" in request.files and request.files["image"].filename:
        image_file = request.files["image"]
        logger.info(f"Processing image: {image_file.filename}")
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
        try:
            image_file.save(temp_file.name)
            temp_file.close()
            logger.info(f"Saved image to temporary file: {temp_file.name}")
```

## Snippet 74
Lines 1253-1257

```Python
if not coze_raw_client:
                    raise Exception("Coze client not initialized properly")

                # Upload file to Coze using direct HTTP request (matching the working implementation)
                try:
```

## Snippet 75
Lines 1262-1268

```Python
logger.info(f"Uploading file {image_file.filename} to Coze")
                    upload_response = requests.post(
                        'https://api.coze.com/v1/files/upload',
                        files=files,
                        headers=headers
                    )
```

## Snippet 76
Lines 1269-1276

```Python
if not upload_response.ok:
                        raise Exception(f"Upload failed: {upload_response.text}")

                    upload_data = upload_response.json()
                    logger.info(f"Upload response: {upload_data}")

                    # Extract file ID according to documented response format
                    # Response format: {"code": 0, "data": {"id": "xxx", ...}, "msg": ""}
```

## Snippet 77
Lines 1280-1283

```Python
if not file_id:
                        raise Exception("No file_id in response")

                    logger.info(f"File uploaded successfully, ID: {file_id}")
```

## Snippet 78
Lines 1287-1289

```Python
except Exception as e:
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500
        finally:
```

## Snippet 79
Lines 1292-1297

```Python
if provider != "anthropic" and 'temp_file' in locals() and temp_file and temp_file.name:
                try:
                    os.remove(temp_file.name)
                except Exception as cleanup_error:
                    print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)
```

## Snippet 80
Lines 1300-1302

```Python
if provider == "anthropic":
                # For Anthropic, we pass the image_path
                logger.info(f"Generating response with Anthropic: model={model}, image_path={image_path is not None}")
```

## Snippet 81
Lines 1305-1307

```Python
elif provider == "openai":
                # For OpenAI, we pass the image_data
                logger.info(f"Generating response with OpenAI: model={model}, image_data={image_data is not None}")
```

## Snippet 82
Lines 1314-1316

```Python
elif provider == "mistral":
                # For Mistral, we pass the image_data
                logger.info(f"Generating response with Mistral: model={model}, image_data={image_data is not None}")
```

## Snippet 83
Lines 1325-1327

```Python
elif provider == "xai":
                # For X.AI, we pass the image as image_data
                logger.info(f"Generating response with X.AI: model={model}, image={image_data is not None}")
```

## Snippet 84
Lines 1332-1339

```Python
if not coze_client or not coze_raw_client:
                    yield format_chunk("Coze client not initialized properly", is_error=True)
                    return

                try:
                    # Store necessary request values to avoid accessing request object in the generator
                    user_id = current_user_id
```

## Snippet 85
Lines 1340-1344

```Python
if not hasattr(coze_client, "conversation_store"):
                        yield format_chunk("Coze client doesn't have conversation store", is_error=True)
                        return

                    # Ensure user exists in conversation store
```

## Snippet 86
Lines 1349-1358

```Python
if model not in coze_client.conversation_store[user_id]:
                        # Initialize conversation outside of the generator
                        initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
                        conversation = coze_raw_client.conversations.create(messages=[initial_message])
                        coze_client.conversation_store[user_id][model] = conversation.id

                    conversation_id = coze_client.conversation_store[user_id][model]

                    # Prepare messages based on whether we have a file ID
                    messages = []
```

## Snippet 87
Lines 1359-1384

```Python
if file_id:
                        messages.append(
                            Message.build_user_question_objects([
                                MessageObjectString.build_text(prompt or "Please describe this image"),
                                MessageObjectString.build_image(file_id=file_id)
                            ])
                        )
                    else:
                        messages.append(Message.build_user_question_text(prompt))

                    # Store all streaming parameters to avoid accessing request context during streaming
                    stream_params = {
                        "bot_id": model,
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "additional_messages": messages
                    }

                    # Stream the response with stored parameters
                    total_tokens = 0
                    # Copy the coze_raw_client to a local variable to avoid accessing global state during streaming
                    client = coze_raw_client

                    # Send a start event to initialize the client-side
                    yield format_chunk({"type": "start", "content": ""})
```

## Snippet 88
Lines 1388-1395

```Python
if content:  # Only send if there's actual content
                                total_tokens += len(content.split())
                                response = {
                                    'type': 'delta',
                                    'content': content,
                                    'tokens': total_tokens
                                }
                                yield format_chunk(response)
```

## Snippet 89
Lines 1396-1401

```Python
elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                            response = {
                                'type': 'complete',
                                'tokens': total_tokens
                            }
                            yield format_chunk(response)
```

## Snippet 90
Lines 1402-1404

```Python
except Exception as e:
                    logger.error(f"Error with Coze streaming: {str(e)}")
                    yield format_chunk(f"Error with Coze: {str(e)}", is_error=True)
```

## Snippet 91
Lines 1409-1412

```Python
except Exception as e:
            yield format_chunk(str(e), is_error=True)
        finally:
            # Clean up Anthropic image file after response is generated
```

## Snippet 92
Lines 1413-1418

```Python
if provider == "anthropic" and image_path:
                try:
                    os.remove(image_path)
                except Exception as cleanup_error:
                    print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)
```

## Snippet 93
Lines 1426-1429

```Python
if isinstance(chunk, dict):
        # Make sure each chunk ends with a newline to ensure proper separation
        return json.dumps(chunk) + "\n"
```

## Snippet 94
Lines 1456-1461

```Python
if coze_client:
            try:
                # Capture all necessary data from the request here
                user_id = data.get("user_id", "default_user")
                bot_id = data.get("bot_id", COZE_BOT_ID)
```

## Snippet 95
Lines 1469-1473

```Python
else:  # ollama
        ollama_client.clear_conversation()

    return "", 204
```

