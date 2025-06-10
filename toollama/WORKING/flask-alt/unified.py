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

# -------------------------------------------------------------------
# API Keys and Constants
# -------------------------------------------------------------------

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "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"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "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"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY") or "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"
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") or "n8R347515VqP48oDHwBeL9BS6nW1L8zY"
COHERE_API_KEY = os.getenv("COHERE_API_KEY") or "8K2VDJ784DPHN57zYauE03mGuslFuaxBW1NUY1LO"
XAI_API_KEY = os.getenv("XAI_API_KEY") or "xai-IxAzklP9jWAhmKaE3pz9PBfcTAowVgNAd9fx1iWwYHNL7kowydC3MAmrMweXROg1q19dq5lye3NG6nmK"

# Initialize Coze client
coze_raw_client = None
try:
    if Coze and TokenAuth and COZE_AUTH_TOKEN:
        try:
            logger.info("Initializing Coze client")
            coze_raw_client = Coze(auth=TokenAuth(token=COZE_AUTH_TOKEN))
            # Verify the client connection works by checking an attribute
            if hasattr(coze_raw_client, 'conversations'):
                logger.info("Coze client initialized successfully")
            else:
                logger.warning("Coze client initialized but missing expected attributes")
        except Exception as e:
            logger.error(f"Failed to initialize Coze client: {str(e)}")
            coze_raw_client = None
    else:
        logger.warning("Skipping Coze client initialization due to missing dependencies or auth token")
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
coze_client = CozeChat(coze_client=coze_raw_client, auth_token=COZE_AUTH_TOKEN) if coze_raw_client else None

# -------------------------------------------------------------------
# Flask Web UX Integration
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
    
    .model-selector { margin-bottom: 1.5rem; }
    
    .model-card {
      border: 1px solid var(--border-color);
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 4px;
      cursor: pointer;
      background: var(--bg-secondary);
    }
    
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
    
    h1, h2 { color: var(--text-primary); }
    
    /* Provider-specific borders */
    .provider-anthropic { border-left: 4px solid #9c27b0; }
    .provider-openai { border-left: 4px solid #4caf50; }
    .provider-ollama { border-left: 4px solid #ff9800; }
    .provider-perplexity { border-left: 4px solid #673ab7; }
    .provider-mistral { border-left: 4px solid #e91e63; }
    .provider-cohere { border-left: 4px solid #ff5722; }
    .provider-xai { border-left: 4px solid #2196f3; }
    .provider-coze { border-left: 4px solid #00bcd4; }
  </style>
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
        Using Anthropic's Claude models for advanced reasoning and vision tasks.
      </div>
      <div id="openai-info" style="display: none">
        Using OpenAI's GPT models with vision capabilities.
      </div>
      <div id="ollama-info" style="display: none">
        Using locally hosted Ollama models (requires Ollama to be running).
      </div>
      <div id="perplexity-info" style="display: none">
        Using Perplexity's Sonar models for chat and reasoning.
      </div>
      <div id="mistral-info" style="display: none">
        Using Mistral's Pixtral models for vision tasks and alt text generation. Only Pixtral models will be shown in image mode.
      </div>
      <div id="cohere-info" style="display: none">
        Using Cohere's command models for chat and reasoning.
      </div>
      <div id="xai-info" style="display: none">
        Using X.AI's Grok models for advanced reasoning and vision tasks.
      </div>
      <div id="coze-info" style="display: none">
        Using Coze's specialized bots for alt text generation and text-to-speech.
      </div>
    </div>
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
      <input type="file" id="image" accept="image/*" style="display: none" onchange="handleImageUpload(event)">
    </div>
    <img id="imagePreview" class="image-preview" alt="Preview">
    <div style="margin-top: 1rem;">
      <label for="imagePrompt">Prompt:</label>
      <input type="text" id="imagePrompt" value="Generate descriptive alt text for the visually impaired for social media" style="margin: 0.5rem 0; display: block;">
      <button onclick="analyzeImage()">Analyze Image</button>
      <div class="loading" id="imageLoading">Analyzing image...</div>
    </div>
    <div id="imageOutput" style="margin-top: 1rem;"></div>
  </div>

  <script>
    // Server-provided constants
    const COZE_BOT_ID = "{{ COZE_BOT_ID }}";
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
        <!-- No sorting/filtering needed for Perplexity as it has a fixed set of models -->
        <div>Fixed set of models with predefined capabilities</div>
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
    };
    
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
      document.getElementById('imagePrompt').value = 'Generate descriptive alt text for the visually impaired for social media';
      document.getElementById('image').value = '';
      
      // Update provider buttons visibility
      document.querySelectorAll('.provider-btn').forEach(btn => {
        const provider = btn.dataset.provider;
        const supportsImages = ['anthropic', 'openai', 'ollama', 'xai', 'coze', 'mistral'].includes(provider);
        btn.style.display = (mode === 'image' && !supportsImages) ? 'none' : 'inline-block';
      });
      
      // If current provider is not valid for new mode, switch to default
      if (mode === 'image' && !['anthropic', 'openai', 'ollama', 'xai', 'coze', 'mistral'].includes(currentProvider)) {
        selectProvider('anthropic');
      } else if (currentProvider) {
        // Refresh models when mode changes with same provider
        fetchModels();
      }
    }
    
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
    
    function appendMessage(role, content) {
      const chatHistory = document.getElementById('chatHistory');
      const messageDiv = document.createElement('div');
      messageDiv.className = `chat-message ${role}`;
      messageDiv.textContent = content;
      chatHistory.appendChild(messageDiv);
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    function clearChat() {
      document.getElementById('chatHistory').innerHTML = '';
      fetch('/clear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ provider: currentProvider })
      });
    }
    
    async function fetchModels() {
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
        
        if (capability && capability !== 'none') {
          params.append('capability', capability);
        }
        
        if (generation && generation !== 'none') {
          params.append('generation', generation);
        }
        
        if (category && category !== 'none') {
          params.append('category', category);
        }
        
        // For image mode with Mistral, force Pixtral models only
        if (currentMode === 'image' && currentProvider === 'mistral') {
          params.set('category', 'pixtral');
          params.set('capability', 'vision');
        }
        
        const response = await fetch(`/models?${params}`);
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
          if (seenModelIds.has(model.id)) {
            return;
          }
          
          seenModelIds.add(model.id);
          
          const modelCard = document.createElement('div');
          modelCard.className = `model-card ${currentProvider}-provider${selectedModel === model.id ? ' selected' : ''}`;
          modelCard.onclick = () => selectModel(model.id);
          
          let modelInfo = '';
          if (currentProvider === 'openai') {
            modelInfo = `
              <span>Context: ${model.context_length?.toLocaleString()} tokens</span>
              <span>Released: ${model.created_str}</span>
              ${model.version ? `<span>Version: ${model.version}</span>` : ''}
            `;
          } else if (currentProvider === 'ollama') {
            modelInfo = `
              <span>Family: ${model.family}</span>
              <span>Size: ${model.parameter_size}</span>
              <span>Format: ${model.format}</span>
              <span>Created: ${model.created_str}</span>
            `;
          } else if (currentProvider === 'perplexity') {
            modelInfo = `
              <span>Context Length: ${model.context_length.toLocaleString()} tokens</span>
            `;
          } else if (currentProvider === 'mistral') {
            modelInfo = `
              <span>Released: ${model.created_at}</span>
              <span>Owner: ${model.owned_by}</span>
            `;
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
        });
        
        // Display error message if Coze service is unavailable
        if (currentProvider === 'coze' && models.length === 1 && models[0].id === 'coze-service-unavailable') {
          document.getElementById('modelError').textContent = 'Coze service is unavailable. Please check the server logs for details.';
        }
        
        // Set default model for alt text mode if we're in image mode
        if (currentMode === 'image' && defaultAltTextModels[currentProvider]) {
          const defaultModel = defaultAltTextModels[currentProvider];
          
          // Check if the default model exists in our fetched models
          const modelExists = models.some(model => model.id === defaultModel);
          
          if (modelExists) {
            selectModel(defaultModel);
          } else if (models.length > 0) {
            // If default doesn't exist but we have models, select the first one
            selectModel(models[0].id);
          }
        }
      } catch (err) {
        document.getElementById('modelError').textContent = `Error loading models: ${err.message}`;
      } finally {
        document.getElementById('modelLoading').style.display = 'none';
      }
    }
    
    function selectModel(modelId) {
      selectedModel = modelId;
      document.querySelector('.model-dropdown-btn').textContent = modelId;
      document.querySelectorAll('.model-option').forEach(option => {
        option.classList.toggle('selected', option.querySelector('strong').textContent === modelId);
      });
      document.querySelector('.model-dropdown-content').classList.remove('visible');
    }
    
    function refreshModels() {
      fetchModels();
    }

    function updateChatHistory(role, content, isPartial = false) {
      const chatHistory = document.getElementById('chatHistory');
      let messageDiv;
      
      if (isPartial) {
        // Update existing message if it's a partial update
        messageDiv = chatHistory.lastElementChild;
        if (!messageDiv || !messageDiv.classList.contains(role)) {
          messageDiv = document.createElement('div');
          messageDiv.className = `chat-message ${role}`;
          chatHistory.appendChild(messageDiv);
        }
      } else {
        // Only create new message if not updating an existing one
        if (!chatHistory.lastElementChild || !chatHistory.lastElementChild.classList.contains(role)) {
          messageDiv = document.createElement('div');
          messageDiv.className = `chat-message ${role}`;
          chatHistory.appendChild(messageDiv);
        } else {
          messageDiv = chatHistory.lastElementChild;
        }
      }
      
      messageDiv.textContent = content;
      chatHistory.scrollTop = chatHistory.scrollHeight;
    }
    
    function toggleModelDropdown() {
      const content = document.querySelector('.model-dropdown-content');
      content.classList.toggle('visible');
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.model-dropdown')) {
        document.querySelector('.model-dropdown-content').classList.remove('visible');
      }
    });
    
    function triggerImageUpload() {
      document.getElementById('image').click();
    }
    
    function handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
          const preview = document.getElementById('imagePreview');
          preview.src = e.target.result;
          preview.classList.add('visible');
        };
        reader.readAsDataURL(file);
      }
    }
    
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
      if (file && file.type.startsWith('image/')) {
        const input = document.getElementById('image');
        input.files = e.dataTransfer.files;
        handleImageUpload({ target: input });
      }
    });
    
    async function sendChatMessage() {
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
      
      // Include user ID for consistent conversation tracking
      if (currentProvider === 'coze') {
        formData.append('user_id', 'user_' + Date.now());
      }
      
      await processResponse(formData, 'chat');
    }
    
    async function analyzeImage() {
      if (!currentProvider || !selectedModel) {
        alert('Please select a provider and model first');
        return;
      }
      
      const imageInput = document.getElementById('image');
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
    }
    
    async function processResponse(formData, mode) {
      try {
        const response = await fetch('/generate', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error(await response.text());
        }
        
        let responseText = '';
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const {value, done} = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, {stream: true});
          
          // Create the line separator regex dynamically
          const lineSeparator = new RegExp('\\n|\\r\\n');
          // Split the chunk into lines to handle multiple JSON objects
          const lines = chunk.split(lineSeparator).filter(line => line.trim());
          
          for (const line of lines) {
            try {
              // Try to parse as JSON
              const jsonData = JSON.parse(line);
              
              if (jsonData.error) {
                throw new Error(jsonData.error);
              }
              
              // Handle different types of responses
              if (jsonData.type === 'delta' && jsonData.content) {
                // Handle delta updates (streaming content)
                responseText += jsonData.content;
              } else if (jsonData.type === 'complete') {
                // Handle completion message
                console.log('Response complete. Total tokens:', jsonData.tokens);
              } else if (jsonData.type === 'start') {
                // Handle start message
                console.log('Streaming started');
              } else {
                // Handle other JSON formats
                const chunkContent = jsonData.content || jsonData.text || jsonData;
                if (typeof chunkContent === 'string') {
                  responseText += chunkContent;
                } else {
                  responseText += JSON.stringify(chunkContent);
                }
              }
            } catch (e) {
              console.error('Error parsing JSON chunk:', e, line);
              // If not valid JSON, treat as raw text (but only if not an empty line)
              if (line.trim()) {
                responseText += line;
              }
            }
          }
          
          // Update UI with current response text
          if (mode === 'chat') {
            updateChatHistory('assistant', responseText, true);
          } else {
            document.getElementById('imageOutput').textContent = responseText;
          }
        }
        
      } catch (err) {
        const errorMessage = `Error: ${err.message}`;
        if (mode === 'chat') {
          updateChatHistory('assistant', errorMessage);
        } else {
          document.getElementById('imageOutput').textContent = errorMessage;
        }
      } finally {
        document.getElementById(`${mode}Loading`).style.display = 'none';
      }
    }
    
    // Update placeholder text for chat and image generation
    document.getElementById('chatPrompt').placeholder = 'Enter your message or question here...';
    document.getElementById('imagePrompt').placeholder = 'Describe the image or ask for alt text...';

    // Start with chat mode and Anthropic selected
    selectMode('chat');
    selectProvider('anthropic');
  </script>
</body>
</html>
"""

@app.route("/models", methods=["GET"])
def get_models():
    """Endpoint to get available models from the selected provider."""
    try:
        provider = request.args.get("provider", "anthropic")
        sort_by = request.args.get("sort_by", "created")
        capability = request.args.get("capability")
        generation = request.args.get("generation")
        category = request.args.get("category")
        
        if capability == "none":
            capability = None
        if generation == "none":
            generation = None
        if category == "none":
            category = None
            
        # Initialize appropriate chat client
        if provider == "anthropic":
            models = anthropic_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
        elif provider == "openai":
            models = openai_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                generation=generation
            )
            if capability and capability != "none":
                models = [model for model in models if capability in model["capabilities"]]
        elif provider == "perplexity":
            models = perplexity_client.list_models()
        elif provider == "mistral":
            models = mistral_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability,
                category_filter=category
            )
        elif provider == "cohere":
            models = cohere_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
        elif provider == "xai":
            models = xai_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
        elif provider == "coze":
            if not coze_client:
                return jsonify([
                    {
                        "id": "coze-service-unavailable",
                        "name": "Coze Service Unavailable",
                        "description": "The Coze service is currently unavailable. Please check the logs for details.",
                        "capabilities": [],
                        "created_at": datetime.now().strftime("%Y-%m-%d"),
                        "owned_by": "coze"
                    }
                ])
            
            models = coze_client.list_models(
                capability_filter=capability
            )
        else:  # ollama
            models = ollama_client.list_models(
                sort_by=sort_by,
                page=1,
                page_size=1000,
                capability_filter=capability
            )
        
        return jsonify(models)
        
    except Exception as e:
        return str(e), 500

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, 
                                 COZE_BOT_ID=COZE_BOT_ID,
                                 COZE_TTS_BOT_ID=COZE_TTS_BOT_ID)

@app.route("/generate", methods=["POST"])
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

    if mode == "image" and "image" in request.files and request.files["image"].filename:
        image_file = request.files["image"]
        logger.info(f"Processing image: {image_file.filename}")
        temp_dir = tempfile.gettempdir()
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
        try:
            image_file.save(temp_file.name)
            temp_file.close()
            logger.info(f"Saved image to temporary file: {temp_file.name}")
            
            if provider == "anthropic":
                # For Anthropic, we need to keep the file path
                image_path = temp_file.name
                logger.info(f"Using file path for Anthropic: {image_path}")
            elif provider in ["openai", "ollama", "xai", "mistral"]:
                # For OpenAI, Ollama, X.AI, and Mistral, we need to encode the image to base64
                if provider == "openai":
                    chat = openai_client
                elif provider == "xai":
                    chat = xai_client
                elif provider == "mistral":
                    chat = mistral_client
                    logger.info(f"Using Mistral client for image encoding")
                else:  # ollama
                    chat = ollama_client
                
                # Encode the image to base64
                logger.info(f"Encoding image for {provider}")
                image_data = chat.encode_image(temp_file.name)
                if not image_data:
                    error_msg = f"Failed to encode image for {provider}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                logger.info(f"Successfully encoded image, length: {len(image_data) if image_data else 0}")
            elif provider == "coze":
                # Skip if Coze client is not initialized
                if not coze_raw_client:
                    raise Exception("Coze client not initialized properly")
                
                # Upload file to Coze using direct HTTP request (matching the working implementation)
                try:
                    # Prepare the file for multipart upload
                    files = {'file': (image_file.filename, open(temp_file.name, 'rb'), 'image/png')}
                    headers = {'Authorization': f'Bearer {COZE_AUTH_TOKEN}'}
                    
                    logger.info(f"Uploading file {image_file.filename} to Coze")
                    upload_response = requests.post(
                        'https://api.coze.com/v1/files/upload',
                        files=files,
                        headers=headers
                    )
                    
                    if not upload_response.ok:
                        raise Exception(f"Upload failed: {upload_response.text}")
                        
                    upload_data = upload_response.json()
                    logger.info(f"Upload response: {upload_data}")
                    
                    # Extract file ID according to documented response format
                    # Response format: {"code": 0, "data": {"id": "xxx", ...}, "msg": ""}
                    if upload_data.get('code') == 0:
                        file_id = upload_data.get('data', {}).get('id')
                    
                    if not file_id:
                        raise Exception("No file_id in response")
                    
                    logger.info(f"File uploaded successfully, ID: {file_id}")
                except Exception as e:
                    raise Exception(f"Error uploading to Coze: {str(e)}")
                
        except Exception as e:
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500
        finally:
            # Clean up temporary files for non-Anthropic providers
            # For Anthropic, we need to keep the file until the response is generated
            if provider != "anthropic" and 'temp_file' in locals() and temp_file and temp_file.name:
                try:
                    os.remove(temp_file.name)
                except Exception as cleanup_error:
                    print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)

    def generate_response():
        try:
            if provider == "anthropic":
                # For Anthropic, we pass the image_path
                logger.info(f"Generating response with Anthropic: model={model}, image_path={image_path is not None}")
                for chunk in anthropic_client.stream_chat_response(prompt, model=model, image_path=image_path):
                    yield format_chunk(chunk)
            elif provider == "openai":
                # For OpenAI, we pass the image_data
                logger.info(f"Generating response with OpenAI: model={model}, image_data={image_data is not None}")
                for chunk in openai_client.stream_chat_response(prompt, model=model, image_data=image_data):
                    yield format_chunk(chunk)
            elif provider == "perplexity":
                logger.info(f"Generating response with Perplexity: model={model}")
                for chunk in perplexity_client.stream_chat_response(prompt, model=model):
                    yield format_chunk(chunk)
            elif provider == "mistral":
                # For Mistral, we pass the image_data
                logger.info(f"Generating response with Mistral: model={model}, image_data={image_data is not None}")
                if image_data:
                    logger.info(f"Image data length: {len(image_data)}")
                for chunk in mistral_client.stream_chat_response(prompt, model=model, image_data=image_data):
                    yield format_chunk(chunk)
            elif provider == "cohere":
                logger.info(f"Generating response with Cohere: model={model}")
                for chunk in cohere_client.stream_chat_response(prompt, model=model):
                    yield format_chunk(chunk)
            elif provider == "xai":
                # For X.AI, we pass the image as image_data
                logger.info(f"Generating response with X.AI: model={model}, image={image_data is not None}")
                for chunk in xai_client.stream_chat_response(prompt, model=model, image=image_data):
                    yield format_chunk(chunk)
            elif provider == "coze":
                # Check if Coze client is available
                if not coze_client or not coze_raw_client:
                    yield format_chunk("Coze client not initialized properly", is_error=True)
                    return
                
                try:
                    # Store necessary request values to avoid accessing request object in the generator
                    user_id = current_user_id
                    
                    if not hasattr(coze_client, "conversation_store"):
                        yield format_chunk("Coze client doesn't have conversation store", is_error=True)
                        return
                        
                    # Ensure user exists in conversation store
                    if user_id not in coze_client.conversation_store:
                        coze_client.conversation_store[user_id] = {}
                        
                    # Get or create conversation for this model/bot
                    if model not in coze_client.conversation_store[user_id]:
                        # Initialize conversation outside of the generator
                        initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
                        conversation = coze_raw_client.conversations.create(messages=[initial_message])
                        coze_client.conversation_store[user_id][model] = conversation.id
                        
                    conversation_id = coze_client.conversation_store[user_id][model]
                    
                    # Prepare messages based on whether we have a file ID
                    messages = []
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
                    
                    for event in client.chat.stream(**stream_params):
                        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                            content = event.message.content
                            if content:  # Only send if there's actual content
                                total_tokens += len(content.split())
                                response = {
                                    'type': 'delta',
                                    'content': content,
                                    'tokens': total_tokens
                                }
                                yield format_chunk(response)
                        elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                            response = {
                                'type': 'complete',
                                'tokens': total_tokens
                            }
                            yield format_chunk(response)
                except Exception as e:
                    logger.error(f"Error with Coze streaming: {str(e)}")
                    yield format_chunk(f"Error with Coze: {str(e)}", is_error=True)
            else:  # ollama
                # For Ollama, we pass the image_data
                for chunk in ollama_client.stream_chat_response(prompt, model=model, image_data=image_data):
                    yield format_chunk(chunk)
        except Exception as e:
            yield format_chunk(str(e), is_error=True)
        finally:
            # Clean up Anthropic image file after response is generated
            if provider == "anthropic" and image_path:
                try:
                    os.remove(image_path)
                except Exception as cleanup_error:
                    print(f"Error cleaning up temporary file: {cleanup_error}", file=sys.stderr)

    return Response(generate_response(), mimetype="text/plain")

def format_chunk(chunk, is_error=False):
    """Format a response chunk for consistent streaming."""
    if is_error:
        return json.dumps({"error": chunk}) + "\n"
    
    if isinstance(chunk, dict):
        # Make sure each chunk ends with a newline to ensure proper separation
        return json.dumps(chunk) + "\n"
    
    if isinstance(chunk, str):
        # For string chunks, wrap them in a delta format for consistency
        return json.dumps({"type": "delta", "content": chunk}) + "\n"
    
    # Fallback for unknown types
    return json.dumps({"type": "delta", "content": str(chunk)}) + "\n"

@app.route("/clear", methods=["POST"])
def clear():
    """Clear the conversation history for the specified provider."""
    data = request.get_json()
    provider = data.get("provider", "anthropic")
    
    if provider == "anthropic":
        anthropic_client.clear_conversation()
    elif provider == "openai":
        openai_client.clear_conversation()
    elif provider == "perplexity":
        perplexity_client.clear_conversation()
    elif provider == "mistral":
        mistral_client.clear_conversation()
    elif provider == "cohere":
        cohere_client.clear_conversation()
    elif provider == "xai":
        xai_client.clear_conversation()
    elif provider == "coze":
        if coze_client:
            try:
                # Capture all necessary data from the request here
                user_id = data.get("user_id", "default_user")
                bot_id = data.get("bot_id", COZE_BOT_ID)
                
                # Clear from conversation store if present
                if hasattr(coze_client, "conversation_store"):
                    if user_id in coze_client.conversation_store and bot_id in coze_client.conversation_store[user_id]:
                        del coze_client.conversation_store[user_id][bot_id]
                        logger.info(f"Cleared conversation for user {user_id} and bot {bot_id}")
            except Exception as e:
                logger.error(f"Error clearing Coze conversation: {str(e)}")
    else:  # ollama
        ollama_client.clear_conversation()
    
    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5087) 