# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_chat_coze.py

File: `toollama/API/--storage/processed-flask-chat/flask_chat_coze.py`  
Language: Python  
Extracted: 2025-06-07 05:17:46  

## Snippet 1
Lines 4-33

```Python
This module provides a Flask interface to the Coze API for streaming chat responses.
Supports model selection, conversation history, and image handling.
"""

import os
import sys
import tempfile
import io
import json
import requests
from flask import Flask, request, render_template_string, Response, jsonify, stream_with_context
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image
import logging
import traceback
from huggingface_hub import InferenceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
COZE_AUTH_TOKEN = 'pat_x43jhhVkypZ7CrKwnFwLGLdHOAegoEQqnhFO4kIqomnw6a3Zp4EaorAYfn6EMLz4'
COZE_BOT_ID = "7462296933429346310"  # Alt Text Generator bot ID
COZE_TTS_BOT_ID = "7463319430379470854"  # TTS Generator bot ID
COZE_SPACE_ID = "7345427862138912773"
HF_API_KEY = "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"
```

## Snippet 2
Lines 34-39

```Python
# Store for conversations
conversation_store = {}

# Import Coze SDK
try:
    from cozepy import Coze, TokenAuth, Message, ChatEventType, MessageObjectString
```

## Snippet 3
Lines 40-45

```Python
if not COZE_AUTH_TOKEN:
        logger.warning("COZE_AUTH_TOKEN not found in environment variables")
        coze = None
    else:
        logger.info("Initializing Coze client")
        coze = Coze(auth=TokenAuth(token=COZE_AUTH_TOKEN))
```

## Snippet 4
Lines 46-49

```Python
except Exception as e:
    logger.error(f"Failed to initialize Coze client: {str(e)}")
    coze = None
```

## Snippet 5
Lines 51-53

```Python
def stream_chat_with_file(message, bot_id, user_id, file_id=None):
    """Stream a chat response from Coze with proper file handling."""
    try:
```

## Snippet 6
Lines 58-66

```Python
if bot_id not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = coze.conversations.create(messages=[initial_message])
            conversation_store[user_id][bot_id] = conversation.id

        conversation_id = conversation_store[user_id][bot_id]

        # Build message with optional file attachment
        messages = []
```

## Snippet 7
Lines 67-78

```Python
if file_id:
            messages.append(
                Message.build_user_question_objects([
                    MessageObjectString.build_text(message or "Please describe this image"),
                    MessageObjectString.build_image(file_id=file_id)
                ])
            )
        else:
            messages.append(Message.build_user_question_text(message))

        # Stream response
        total_tokens = 0
```

## Snippet 8
Lines 79-84

```Python
for event in coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            conversation_id=conversation_id,
            additional_messages=messages
        ):
```

## Snippet 9
Lines 85-91

```Python
if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                total_tokens += len(event.message.content.split())
                yield {
                    'type': 'delta',
                    'content': event.message.content,
                    'tokens': total_tokens
                }
```

## Snippet 10
Lines 92-97

```Python
elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                yield {
                    'type': 'complete',
                    'tokens': total_tokens
                }
```

## Snippet 11
Lines 98-101

```Python
except Exception as e:
        logger.error(f"Error in stream_chat_response: {str(e)}")
        yield {'type': 'error', 'message': str(e)}
```

## Snippet 12
Lines 105-110

```Python
def __init__(self, coze_client=None, auth_token=None):
        """Initialize with Coze client and API key."""
        self.coze = coze_client
        self.auth_token = auth_token
        self.conversation_store = {}
```

## Snippet 13
Lines 111-113

```Python
def fetch_coze_bots(self):
        """Fetch bots from Coze API using direct HTTP request."""
        try:
```

## Snippet 14
Lines 118-130

```Python
headers = {"Authorization": f"Bearer {self.auth_token}"}

            # Try various possible endpoint patterns
            endpoints = [
                "https://api.coze.com/v1/published_bots",
                "https://api.coze.com/v1/bots",
                "https://api.coze.com/v1/bots/list",
                "https://api.coze.com/v1/bots/published",
                "https://api.coze.com/v1/agents",
                "https://www.coze.com/api/v1/bots",
                "https://www.coze.com/api/v1/published_bots"
            ]
```

## Snippet 15
Lines 131-135

```Python
for endpoint in endpoints:
                try:
                    logger.info(f"Attempting to fetch bots from: {endpoint}")
                    response = requests.get(endpoint, headers=headers, timeout=10)
```

## Snippet 16
Lines 136-142

```Python
# Only raise for 4xx/5xx status codes, not for other types of errors
                    response.raise_for_status()

                    # Try to parse the response as JSON
                    data = response.json()

                    # Check common response patterns
```

## Snippet 17
Lines 159-163

```Python
except ValueError as e:
                    logger.warning(f"Failed to parse JSON from {endpoint}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Unexpected error accessing {endpoint}: {str(e)}")
```

## Snippet 18
Lines 165-171

```Python
if COZE_SPACE_ID:
                space_endpoints = [
                    f"https://api.coze.com/v1/spaces/{COZE_SPACE_ID}/bots",
                    f"https://api.coze.com/v1/spaces/{COZE_SPACE_ID}/agents",
                    f"https://www.coze.com/api/v1/spaces/{COZE_SPACE_ID}/bots"
                ]
```

## Snippet 19
Lines 172-180

```Python
for endpoint in space_endpoints:
                    try:
                        logger.info(f"Attempting to fetch bots from space endpoint: {endpoint}")
                        response = requests.get(endpoint, headers=headers, timeout=10)
                        response.raise_for_status()

                        data = response.json()

                        # Check common response patterns
```

## Snippet 20
Lines 196-200

```Python
# If all attempts failed, log and return empty list
            logger.warning("Could not fetch bots from any endpoint. The API endpoints may have changed or access might be restricted.")
            logger.info("Falling back to hardcoded models only")
            return []
```

## Snippet 21
Lines 201-205

```Python
except Exception as e:
            logger.error(f"Error in fetch_coze_bots: {str(e)}")
            logger.error(traceback.format_exc())
            return []
```

## Snippet 22
Lines 206-218

```Python
def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """Return a list of available Coze bots."""
        try:
            # Always include the hardcoded Alt Text Generator bot
            models = [{
                "id": COZE_BOT_ID,
                "name": "Alt Text Generator",
```

## Snippet 23
Lines 226-229

```Python
if self.auth_token:
                try:
                    # Fetch bots from the API
                    bots = self.fetch_coze_bots()
```

## Snippet 24
Lines 230-232

```Python
logger.info(f"Fetched {len(bots)} bots from Coze API")

                    # Process each bot and add to the models list
```

## Snippet 25
Lines 235-240

```Python
if not isinstance(bot, dict):
                            logger.warning(f"Skipping bot with non-dict data: {bot}")
                            continue

                        # Extract bot ID using various potential field names
                        bot_id = None
```

## Snippet 26
Lines 242-245

```Python
if id_field in bot:
                                bot_id = bot.get(id_field)
                                break
```

## Snippet 27
Lines 246-250

```Python
if not bot_id:
                            logger.warning(f"Skipping bot with no identifiable ID: {bot}")
                            continue

                        # Skip the alt text bot since we already have it hardcoded
```

## Snippet 28
Lines 251-255

```Python
if bot_id == COZE_BOT_ID:
                            continue

                        # Extract bot details using various potential field names
                        bot_name = None
```

## Snippet 29
Lines 276-289

```Python
# Check for vision capabilities with various field patterns
                        vision_indicators = [
                            bot.get('has_vision', False),
                            bot.get('hasVision', False),
                            bot.get('vision_enabled', False),
                            bot.get('visionEnabled', False),
                            bot.get('supportsVision', False),
                            bot.get('supports_vision', False),
                            bot.get('supports_images', False),
                            bot.get('supportsImages', False),
                            'vision' in bot.get('capabilities', []),
                            'image' in bot.get('capabilities', [])
                        ]
```

## Snippet 30
Lines 293-304

```Python
# Check for audio capabilities with various field patterns
                        audio_indicators = [
                            bot.get('has_audio', False),
                            bot.get('hasAudio', False),
                            bot.get('audio_enabled', False),
                            bot.get('audioEnabled', False),
                            bot.get('supportsAudio', False),
                            bot.get('supports_audio', False),
                            'audio' in bot.get('capabilities', []),
                            'voice' in bot.get('capabilities', [])
                        ]
```

## Snippet 31
Lines 313-315

```Python
if date_value:
                                    try:
                                        # Handle different date formats - string or timestamp
```

## Snippet 32
Lines 321-324

```Python
except Exception as e:
                                        logger.warning(f"Failed to parse creation date: {e}")
                                    break
```

## Snippet 33
Lines 330-333

```Python
if owner_value:
                                    owner = owner_value
                                    break
```

## Snippet 34
Lines 334-343

```Python
# Add bot to models list
                        models.append({
                            "id": bot_id,
                            "name": bot_name,
                            "description": bot_desc,
                            "capabilities": bot_capabilities,
                            "created_at": creation_date,
                            "owned_by": owner
                        })
```

## Snippet 35
Lines 345-347

```Python
except Exception as e:
                    logger.error(f"Error processing Coze bots: {str(e)}")
                    logger.error(traceback.format_exc())
```

## Snippet 36
Lines 358-362

```Python
else:
                # If auth token is not available, add the hardcoded TTS bot
                models.append({
                    "id": COZE_TTS_BOT_ID,
                    "name": "TTS Generator",
```

## Snippet 37
Lines 373-376

```Python
# Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
```

## Snippet 38
Lines 377-383

```Python
except Exception as e:
            logger.error(f"Error in list_models: {str(e)}")
            logger.error(traceback.format_exc())
            # Return default models in case of error
            return [{
                "id": COZE_BOT_ID,
                "name": "Alt Text Generator",
```

## Snippet 39
Lines 390-397

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = COZE_BOT_ID,
        user_id: str = "default_user",
        file_id: Optional[str] = None
    ) -> Generator[Dict, None, None]:
        """Stream a chat response from Coze using the shared implementation."""
```

## Snippet 40
Lines 406-409

```Python
if user_id not in self.conversation_store:
            self.conversation_store[user_id] = {}

        # Make sure conversation is initialized in both stores
```

## Snippet 41
Lines 410-419

```Python
if model not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = self.coze.conversations.create(messages=[initial_message])
            conversation_store[user_id][model] = conversation.id
            # Also update local store
            self.conversation_store[user_id][model] = conversation_store[user_id][model]

        # Use the shared implementation
        yield from stream_chat_with_file(message, model, user_id, file_id)
```

## Snippet 42
Lines 420-423

```Python
def clear_conversation(self, user_id: str, model: str):
        """Clear conversation history."""
        # Clear from global conversation store
        global conversation_store
```

## Snippet 43
Lines 424-427

```Python
if user_id in conversation_store and model in conversation_store[user_id]:
            del conversation_store[user_id][model]

        # Also clear from local store
```

## Snippet 44
Lines 432-585

```Python
chat_client = CozeChat(coze_client=coze, auth_token=COZE_AUTH_TOKEN) if coze else None

# Flask routes
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coze Chat</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: #f5f5f7;
        }
        header {
            background-color: #333;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        main {
            display: flex;
            flex-direction: column;
            flex: 1;
            padding: 1rem;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 1rem;
        }
        button {
            padding: 8px 16px;
            background-color: #0071e3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #0062c3;
        }
        #clearBtn {
            background-color: #ff3b30;
        }
        #clearBtn:hover {
            background-color: #d33227;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            flex: 1;
            gap: 10px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem;
            overflow-y: auto;
            max-height: 60vh;
        }
        .message {
            padding: 12px;
            border-radius: 8px;
            max-width: 80%;
            word-break: break-word;
        }
        .user-message {
            background-color: #e1f5fe;
            align-self: flex-end;
        }
        .assistant-message {
            background-color: #f1f1f1;
            align-self: flex-start;
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin-top: 1rem;
        }
        #userInput {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .bot-selector {
            margin-bottom: 1rem;
        }
        select, .file-input-label {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            font-size: 14px;
        }
        .file-input-container {
            position: relative;
            overflow: hidden;
            display: inline-block;
        }
        .file-input-label {
            cursor: pointer;
            display: inline-block;
            padding: 8px 16px;
            background-color: #34c759;
            color: white;
            border-radius: 4px;
        }
        .file-input-label:hover {
            background-color: #2aa84a;
        }
        #fileInput {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            width: 0.1px;
            height: 0.1px;
        }
        #uploadPreview {
            max-width: 200px;
            max-height: 200px;
            margin-top: 10px;
            display: none;
            border-radius: 4px;
        }
        .loading {
            display: none;
            align-items: center;
            justify-content: center;
            margin-top: 10px;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #0071e3;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
```

## Snippet 45
Lines 589-597

```Python
}
        .error {
            color: #ff3b30;
            padding: 10px;
            background-color: #ffeeee;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }
```

## Snippet 46
Lines 599-607

```Python
</head>
<body>
    <header>
        <h1>Coze Chat</h1>
    </header>
    <main>
        <div class="bot-selector">
            <label for="botSelect">Select Bot:</label>
            <select id="botSelect">
```

## Snippet 47
Lines 611-625

```Python
</div>

        <div class="chat-container" id="chatContainer"></div>

        <div class="loading" id="loadingIndicator">
            <div class="loading-spinner"></div>
            <span>Processing...</span>
        </div>

        <div class="error" id="errorContainer"></div>

        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message...">
            <div class="file-input-container">
                <label for="fileInput" class="file-input-label">Upload</label>
```

## Snippet 48
Lines 627-629

```Python
</div>
            <button id="sendBtn">Send</button>
            <button id="clearBtn">Clear</button>
```

## Snippet 49
Lines 630-632

```Python
</div>

        <img id="uploadPreview" src="" alt="Preview">
```

## Snippet 50
Lines 633-650

```Python
</main>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const fileInput = document.getElementById('fileInput');
        const sendBtn = document.getElementById('sendBtn');
        const clearBtn = document.getElementById('clearBtn');
        const botSelect = document.getElementById('botSelect');
        const uploadPreview = document.getElementById('uploadPreview');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const errorContainer = document.getElementById('errorContainer');

        let uploadedFileId = null;
        let currentUserId = 'user_' + Date.now();

        // Handle file selection
        fileInput.addEventListener('change', async function(e) {
```

## Snippet 51
Lines 651-664

```Python
if (fileInput.files.length > 0) {
                const file = fileInput.files[0];

                // Preview image
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadPreview.src = e.target.result;
                    uploadPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);

                // Upload file
                await uploadFile(file);
            }
```

## Snippet 52
Lines 668-682

```Python
async function uploadFile(file) {
            try {
                loadingIndicator.style.display = 'flex';
                errorContainer.style.display = 'none';

                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
```

## Snippet 53
Lines 683-685

```Python
if (data.success && data.file_id) {
                    uploadedFileId = data.file_id;
                    console.log('File uploaded successfully, ID:', uploadedFileId);
```

## Snippet 54
Lines 689-693

```Python
} catch (error) {
                console.error('Error uploading file:', error);
                showError('Error uploading file: ' + error.message);
                uploadedFileId = null;
                uploadPreview.style.display = 'none';
```

## Snippet 55
Lines 705-708

```Python
async function sendMessage() {
            const message = userInput.value.trim();
            const botId = botSelect.value;
```

## Snippet 56
Lines 709-727

```Python
if (!message && !uploadedFileId) return;

            // Add user message to chat
            addMessage(message, 'user');

            // Clear input
            userInput.value = '';

            try {
                loadingIndicator.style.display = 'flex';
                errorContainer.style.display = 'none';

                // Prepare request data
                const requestData = {
                    message: message,
                    bot_id: botId,
                    user_id: currentUserId
                };
```

## Snippet 57
Lines 728-731

```Python
if (uploadedFileId) {
                    requestData.file_id = uploadedFileId;
                }
```

## Snippet 58
Lines 732-738

```Python
// Use EventSource for streaming response
                const source = new EventSource(
                    '/chat_unified?' +
                    new URLSearchParams({
                        message: message,
                        bot_id: botId,
                        user_id: currentUserId,
```

## Snippet 59
Lines 741-748

```Python
);

                let assistantMessage = '';
                let assistantDiv = null;

                source.onmessage = function(event) {
                    const data = JSON.parse(event.data);
```

## Snippet 60
Lines 749-753

```Python
if (data.type === 'start') {
                        // Create assistant message div
                        assistantDiv = document.createElement('div');
                        assistantDiv.className = 'message assistant-message';
                        chatContainer.appendChild(assistantDiv);
```

## Snippet 61
Lines 754-756

```Python
} else if (data.type === 'delta') {
                        // Update assistant message with new content
                        assistantMessage += data.content;
```

## Snippet 62
Lines 757-760

```Python
if (assistantDiv) {
                            assistantDiv.textContent = assistantMessage;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
```

## Snippet 63
Lines 761-764

```Python
} else if (data.type === 'complete') {
                        // Message complete
                        source.close();
                        loadingIndicator.style.display = 'none';
```

## Snippet 64
Lines 765-769

```Python
} else if (data.type === 'error') {
                        // Handle error
                        source.close();
                        showError('Error: ' + data.message);
                    }
```

## Snippet 65
Lines 770-783

```Python
};

                source.onerror = function(error) {
                    source.close();
                    console.error('EventSource error:', error);
                    showError('Connection error occurred');
                    loadingIndicator.style.display = 'none';
                };

                // Reset file upload
                uploadedFileId = null;
                uploadPreview.style.display = 'none';
                fileInput.value = '';
```

## Snippet 66
Lines 784-788

```Python
} catch (error) {
                console.error('Error sending message:', error);
                showError('Error: ' + error.message);
                loadingIndicator.style.display = 'none';
            }
```

## Snippet 67
Lines 792-800

```Python
function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text || (sender === 'user' ? 'Please analyze this image' : '');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        // Show error message
```

## Snippet 68
Lines 801-822

```Python
function showError(message) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
        }

        // Clear chat
        clearBtn.addEventListener('click', async function() {
            try {
                loadingIndicator.style.display = 'flex';
                errorContainer.style.display = 'none';

                const response = await fetch('/clear', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: currentUserId,
                        bot_id: botSelect.value
                    })
                });
```

## Snippet 69
Lines 823-827

```Python
if (response.ok) {
                    chatContainer.innerHTML = '';
                    uploadedFileId = null;
                    uploadPreview.style.display = 'none';
                    fileInput.value = '';
```

## Snippet 70
Lines 828-831

```Python
} else {
                    const data = await response.json();
                    throw new Error(data.error || 'Failed to clear chat');
                }
```

## Snippet 71
Lines 832-834

```Python
} catch (error) {
                console.error('Error clearing chat:', error);
                showError('Error clearing chat: ' + error.message);
```

## Snippet 72
Lines 847-855

```Python
if request.method == "GET":
        return render_template_string(
            HTML_TEMPLATE,
            alt_text_bot=COZE_BOT_ID,
            tts_bot=COZE_TTS_BOT_ID
        )

    try:
        data = request.json
```

## Snippet 73
Lines 856-863

```Python
if not data:
            return jsonify({"error": "No data received"}), 400

        message = data.get('message', '')
        file_id = data.get('file_id')
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)
```

## Snippet 74
Lines 864-867

```Python
def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
```

## Snippet 75
Lines 868-875

```Python
for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id,
                    file_id=file_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"
```

## Snippet 76
Lines 876-879

```Python
except Exception as e:
                logger.error(f"Error in default chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## Snippet 77
Lines 880-888

```Python
return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
```

## Snippet 78
Lines 889-892

```Python
except Exception as e:
        logger.error(f"Error in default chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
```

## Snippet 79
Lines 895-897

```Python
"""Endpoint for Coze chat completions."""
    try:
        data = request.json
```

## Snippet 80
Lines 898-905

```Python
if not data:
            return jsonify({"error": "No data received"}), 400

        message = data.get('message', '')
        file_id = data.get('file_id')
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)
```

## Snippet 81
Lines 906-909

```Python
def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
```

## Snippet 82
Lines 910-917

```Python
for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id,
                    file_id=file_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"
```

## Snippet 83
Lines 918-921

```Python
except Exception as e:
                logger.error(f"Error in completions chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## Snippet 84
Lines 922-930

```Python
return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
```

## Snippet 85
Lines 931-934

```Python
except Exception as e:
        logger.error(f"Error in completions chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
```

## Snippet 86
Lines 937-939

```Python
"""Endpoint for Coze drummer chat completions."""
    try:
        data = request.json
```

## Snippet 87
Lines 940-947

```Python
if not data:
            return jsonify({"error": "No data received"}), 400

        message = data.get('message', '')
        file_id = data.get('file_id')
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)
```

## Snippet 88
Lines 948-951

```Python
def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
```

## Snippet 89
Lines 952-959

```Python
for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id,
                    file_id=file_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"
```

## Snippet 90
Lines 960-963

```Python
except Exception as e:
                logger.error(f"Error in drummer chat stream: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## Snippet 91
Lines 964-967

```Python
return Response(
            stream_with_context(generate()),
            content_type='text/event-stream'
        )
```

## Snippet 92
Lines 968-971

```Python
except Exception as e:
        logger.error(f"Error in drummer chat: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

## Snippet 93
Lines 976-979

```Python
if not HF_API_KEY:
            return jsonify({"error": "Hugging Face API key not configured"}), 500

        data = request.json
```

## Snippet 94
Lines 980-992

```Python
if not data:
            return jsonify({"error": "No data received"}), 400

        client = InferenceClient(api_key=HF_API_KEY)

        # Extract parameters
        message = data.get('message', '')
        image_data = data.get('image')  # Expecting base64 encoded image
        model = data.get('model', 'meta-llama/Llama-3.2-11B-Vision-Instruct')
        max_tokens = data.get('max_tokens', 500)

        # Prepare messages
        messages = []
```

## Snippet 95
Lines 993-1014

```Python
if image_data:
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message or "Describe this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }]
        else:
            messages = [{
                "role": "user",
                "content": message
            }]
```

## Snippet 96
Lines 1015-1052

```Python
def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"

                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens
                )

                response_content = completion.choices[0].message.content
                total_tokens = len(response_content.split())

                yield f"data: {json.dumps({
                    'type': 'delta',
                    'content': response_content,
                    'tokens': total_tokens
                })}\n\n"

                yield f"data: {json.dumps({
                    'type': 'complete',
                    'tokens': total_tokens
                })}\n\n"

            except Exception as e:
                logger.error(f"Error in HF chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
```

## Snippet 97
Lines 1053-1056

```Python
except Exception as e:
        logger.error(f"Error in HF chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
```

## Snippet 98
Lines 1058-1069

```Python
def clear_conversation():
    """Clear a chat conversation."""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)

        chat_client.clear_conversation(user_id, bot_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Snippet 99
Lines 1075-1078

```Python
if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
```

## Snippet 100
Lines 1079-1085

```Python
if not file:
            return jsonify({"error": "Empty file"}), 400

        # Upload file using direct API call
        files = {'file': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': f'Bearer {COZE_AUTH_TOKEN}'}
```

## Snippet 101
Lines 1086-1094

```Python
logger.info(f"Uploading file {file.filename} to Coze")
        upload_response = requests.post(
            'https://api.coze.com/v1/files/upload',
            files=files,
            headers=headers
        )

        logger.info(f"Upload response: {upload_response.text}")
```

## Snippet 102
Lines 1095-1103

```Python
if not upload_response.ok:
            raise Exception(f"Upload failed: {upload_response.text}")

        upload_data = upload_response.json()
        logger.info(f"Upload data: {upload_data}")

        # Extract file ID according to documented response format
        # Response format: {"code": 0, "data": {"id": "xxx", ...}, "msg": ""}
        file_id = None
```

## Snippet 103
Lines 1107-1115

```Python
if not file_id:
            raise Exception("No file_id in response")

        logger.info(f"File uploaded successfully, ID: {file_id}")
        return jsonify({
            "success": True,
            "file_id": file_id
        })
```

## Snippet 104
Lines 1116-1120

```Python
except Exception as e:
        error_msg = str(e)
        logger.error(f"File upload error: {error_msg}")
        return jsonify({"error": error_msg}), 500
```

## Snippet 105
Lines 1124-1129

```Python
if request.method == "GET":
        # Handle SSE request
        message = request.args.get('message', '')
        bot_id = request.args.get('bot_id', COZE_BOT_ID)
        user_id = request.args.get('user_id', 'default_user')
```

## Snippet 106
Lines 1130-1133

```Python
def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
```

## Snippet 107
Lines 1134-1140

```Python
for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"
```

## Snippet 108
Lines 1141-1144

```Python
except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## Snippet 109
Lines 1145-1153

```Python
return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
```

## Snippet 110
Lines 1154-1161

```Python
else:
        # Handle POST request with file upload
        try:
            message = request.form.get('message', '')
            bot_id = request.form.get('bot_id', COZE_BOT_ID)
            user_id = request.form.get('user_id', 'default_user')
            file_id = None
```

## Snippet 111
Lines 1164-1179

```Python
if file:
                    # Save file temporarily
                    temp_dir = tempfile.gettempdir()
                    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
                    try:
                        file.save(temp_file.name)
                        temp_file.close()

                        # Upload file to Coze
                        file_id = chat_client.coze.files.upload(temp_file.name)
                    finally:
                        try:
                            os.remove(temp_file.name)
                        except Exception as cleanup_error:
                            logger.error(f"Error cleaning up temporary file: {cleanup_error}")
```

## Snippet 112
Lines 1180-1183

```Python
def generate():
                try:
                    yield f"data: {json.dumps({'type': 'start'})}\n\n"
```

## Snippet 113
Lines 1184-1191

```Python
for response in chat_client.stream_chat_response(
                        message=message,
                        model=bot_id,
                        user_id=user_id,
                        file_id=file_id
                    ):
                        yield f"data: {json.dumps(response)}\n\n"
```

## Snippet 114
Lines 1192-1195

```Python
except Exception as e:
                    logger.error(f"Error in chat stream: {str(e)}\n{traceback.format_exc()}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## Snippet 115
Lines 1196-1204

```Python
return Response(
                stream_with_context(generate()),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
```

## Snippet 116
Lines 1205-1208

```Python
except Exception as e:
            logger.error(f"Error in chat: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500
```

## Snippet 117
Lines 1213-1226

```Python
if request.method == "GET":
            # Handle SSE requests with query parameters
            message = request.args.get('message', '')
            file_id = request.args.get('file_id')
            user_id = request.args.get('user_id', 'default_user')
            bot_id = request.args.get('bot_id', COZE_BOT_ID)
        else:
            # Handle JSON POST request
            data = request.json or {}
            message = data.get('message', '')
            file_id = data.get('file_id')
            user_id = data.get('user_id', 'default_user')
            bot_id = data.get('bot_id', COZE_BOT_ID)
```

## Snippet 118
Lines 1231-1237

```Python
if bot_id not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = coze.conversations.create(messages=[initial_message])
            conversation_store[user_id][bot_id] = conversation.id

        conversation_id = conversation_store[user_id][bot_id]
```

## Snippet 119
Lines 1238-1242

```Python
def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"

                messages = []
```

## Snippet 120
Lines 1243-1253

```Python
if file_id:
                    messages.append(
                        Message.build_user_question_objects([
                            MessageObjectString.build_text(message or "Please describe this image"),
                            MessageObjectString.build_image(file_id=file_id)
                        ])
                    )
                else:
                    messages.append(Message.build_user_question_text(message))

                total_tokens = 0
```

## Snippet 121
Lines 1254-1259

```Python
for event in coze.chat.stream(
                    bot_id=bot_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    additional_messages=messages
                ):
```

## Snippet 122
Lines 1260-1266

```Python
if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                        total_tokens += len(event.message.content.split())
                        yield f"data: {json.dumps({
                            'type': 'delta',
                            'content': event.message.content,
                            'tokens': total_tokens
                        })}\n\n"
```

## Snippet 123
Lines 1267-1272

```Python
elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                        yield f"data: {json.dumps({
                            'type': 'complete',
                            'tokens': total_tokens
                        })}\n\n"
```

## Snippet 124
Lines 1273-1276

```Python
except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
```

## Snippet 125
Lines 1277-1285

```Python
return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
```

## Snippet 126
Lines 1286-1289

```Python
except Exception as e:
        logger.error(f"Error in chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500
```

