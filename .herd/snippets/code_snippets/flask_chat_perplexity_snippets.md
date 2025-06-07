# Code Snippets from toollama/API/--storage/processed-flask-chat/flask_chat_perplexity.py

File: `toollama/API/--storage/processed-flask-chat/flask_chat_perplexity.py`  
Language: Python  
Extracted: 2025-06-07 05:17:55  

## Snippet 1
Lines 1-12

```Python
from flask import Flask, render_template_string, request, Response, stream_with_context
import requests
import json
import sys
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
import markdown
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"  # replace with a secure key in production
```

## Snippet 2
Lines 14-18

```Python
class PerplexityChat:
    MODELS = {
        "sonar-reasoning-pro": {
            "id": "sonar-reasoning-pro",
            "context_length": 127000,
```

## Snippet 3
Lines 20-35

```Python
},
        "sonar-reasoning": {
            "id": "sonar-reasoning",
            "context_length": 127000,
            "description": "Sonar model with reasoning capabilities"
        },
        "sonar-pro": {
            "id": "sonar-pro",
            "context_length": 200000,
            "description": "Sonar model with extended context"
        },
        "sonar": {
            "id": "sonar",
            "context_length": 127000,
            "description": "Base Sonar model"
        }
```

## Snippet 4
Lines 38-47

```Python
def __init__(self, api_key: str):
        """Initialize the Perplexity client with the provided API key."""
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        # Initialize with system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 5
Lines 48-56

```Python
def list_models(self):
        """Return a list of available models."""
        return [
            {
                "id": model_id,
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"]
            }
```

## Snippet 6
Lines 60-94

```Python
def stream_chat_response(self, message: str, model: str = "sonar", temperature: float = 0.7):
        """
        Stream a chat response from Perplexity.

        Yields chunks of response text as they arrive.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Append user message to history
        self.chat_history.append({
            "role": "user",
            "content": message
        })

        payload = {
            "model": model,
            "messages": self.chat_history,
            "temperature": temperature,
            "stream": True
        }

        full_response = ""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            response.raise_for_status()
```

## Snippet 7
Lines 96-98

```Python
if line:
                    try:
                        line_text = line.decode('utf-8')
```

## Snippet 8
Lines 106-109

```Python
if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                yield content
```

## Snippet 9
Lines 110-115

```Python
except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 10
Lines 116-121

```Python
# Append assistant's response to history
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })
```

## Snippet 11
Lines 122-131

```Python
except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            # On error, remove the user message
            self.chat_history.pop()
            yield "Error: Unable to get response from API."
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            self.chat_history.pop()
            yield "Error: An unexpected error occurred."
```

## Snippet 12
Lines 132-138

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 13
Lines 139-143

```Python
# --- Global PerplexityChat instance ---
# NOTE: In a production multi-user environment, you'd want to manage per-user conversation state.
API_KEY = "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"  # replace with your actual API key
chat_client = PerplexityChat(API_KEY)
```

## Snippet 14
Lines 146-153

```Python
# HTML template for the chat UX
INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Streaming Chat with Perplexity API</title>
  <style>
```

## Snippet 15
Lines 164-169

```Python
</head>
<body>
  <h2>Streaming Chat with Perplexity API</h2>
  <div>
    <label for="model">Choose a model:</label>
    <select id="model">
```

## Snippet 16
Lines 174-186

```Python
</div>
  <div id="chat-container"></div>
  <div id="controls">
    <form id="chatForm">
      <input type="text" id="message" placeholder="Enter your message" size="60" required>
      <button type="submit">Send</button>
      <button type="button" id="clearBtn">Clear Conversation</button>
    </form>
  </div>

  <script>
    const chatContainer = document.getElementById("chat-container");
```

## Snippet 17
Lines 187-200

```Python
function appendMessage(sender, text, newline = true) {
      const msgDiv = document.createElement("div");
      msgDiv.classList.add("message");
      msgDiv.classList.add(sender.toLowerCase());
      msgDiv.innerHTML = "<strong>" + sender + ":</strong> " + text + (newline ? "<br>" : "");
      chatContainer.appendChild(msgDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    document.getElementById("chatForm").addEventListener("submit", async function(e) {
      e.preventDefault();
      const messageInput = document.getElementById("message");
      const modelSelect = document.getElementById("model");
      const message = messageInput.value.trim();
```

## Snippet 18
Lines 201-216

```Python
if (!message) return;
      appendMessage("You", message);
      messageInput.value = "";

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: message,
            model: modelSelect.value
          })
        });
```

## Snippet 19
Lines 217-224

```Python
if (!response.ok) {
          appendMessage("Assistant", "Error: " + response.statusText);
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
```

## Snippet 20
Lines 226-228

```Python
const { value, done: doneReading } = await reader.read();
          done = doneReading;
          const chunk = decoder.decode(value);
```

## Snippet 21
Lines 229-231

```Python
if (chunk) {
            appendMessage("Assistant", chunk, false);
          }
```

## Snippet 22
Lines 233-235

```Python
} catch (err) {
        appendMessage("Assistant", "Error: " + err);
      }
```

## Snippet 23
Lines 236-239

```Python
});

    // Clear conversation button (reloads the page)
    document.getElementById("clearBtn").addEventListener("click", function() {
```

## Snippet 24
Lines 250-341

```Python
async def index():
    dark_mode_template = INDEX_HTML.replace(
        "<style>",
        """<style>
            :root {
                --bg-color: #1a1a1a;
                --text-color: #e0e0e0;
                --border-color: #333;
                --card-bg: #242424;
                --card-hover: #2a2a2a;
                --selected-bg: #1e3a5f;
                --button-bg: #2196f3;
                --button-hover: #1976d2;
                --tag-bg: #333;
                --error-color: #ff6b6b;
            }

            body {
                background-color: var(--bg-color);
                color: var(--text-color);
            }

            .model-card {
                background-color: var(--card-bg);
                border-color: var(--border-color);
            }

            .model-card:hover {
                background-color: var(--card-hover);
            }

            .model-card.selected {
                background-color: var(--selected-bg);
                border-color: var(--button-bg);
            }

            .capability-tag {
                background: var(--tag-bg);
                color: var(--text-color);
            }

            button {
                background: var(--button-bg);
            }

            button:hover {
                background: var(--button-hover);
            }

            select, input, textarea {
                background-color: var(--card-bg);
                color: var(--text-color);
                border: 1px solid var(--border-color);
                padding: 0.5rem;
                border-radius: 4px;
            }

            .chat-history {
                background-color: var(--card-bg);
                border-color: var(--border-color);
            }

            .chat-message.user {
                background-color: var(--selected-bg);
            }

            .chat-message.assistant {
                background-color: var(--card-hover);
            }

            #modelError {
                color: var(--error-color);
            }

            .provider-selector, .mode-selector {
                background-color: var(--card-bg);
            }

            .provider-btn, .mode-btn {
                background-color: var(--card-bg);
                color: var(--text-color);
            }

            .provider-btn.active, .mode-btn.active {
                background-color: var(--selected-bg);
                border-color: var(--button-bg);
            }
        """
    )
    models = chat_client.list_models()
    return await render_template_string(dark_mode_template, models=models)
```

## Snippet 25
Lines 345-349

```Python
if not data or "message" not in data:
        return "No message provided", 400
    message = data["message"]
    model = data.get("model", "sonar")
```

## Snippet 26
Lines 358-361

```Python
def clear():
    chat_client.clear_conversation()
    return "Conversation cleared", 200
```

## Snippet 27
Lines 362-365

```Python
async def stream_response(provider: str, prompt: str, model: str, image_path: Optional[str] = None, image_data: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Stream response from any provider with consistent handling."""
    try:
        response_text = ""
```

## Snippet 28
Lines 368-374

```Python
if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                response_text += content
                yield content
```

## Snippet 29
Lines 377-384

```Python
if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                response_text += content
                yield content
                await asyncio.sleep(0)
```

## Snippet 30
Lines 387-390

```Python
if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
```

## Snippet 31
Lines 391-396

```Python
# Convert markdown to HTML for display
                content = markdown.markdown(content)
                response_text += content
                yield content
                await asyncio.sleep(0)
```

## Snippet 32
Lines 399-406

```Python
if isinstance(chunk, dict):
                    content = chunk.get('content', '')
                else:
                    content = str(chunk)
                response_text += content
                yield content
                await asyncio.sleep(0)
```

## Snippet 33
Lines 409-416

```Python
if isinstance(chunk, dict):
                    content = chunk.get('response', chunk.get('content', ''))
                else:
                    content = str(chunk)
                response_text += content
                yield content
                await asyncio.sleep(0)
```

