# Code Snippets from toollama/API/--storage/mcp_server.py

File: `toollama/API/--storage/mcp_server.py`  
Language: Python  
Extracted: 2025-06-07 05:16:55  

## Snippet 1
Lines 1-11

```Python
import sys
import json
import requests
from uuid import uuid4
from typing import Generator, List, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
```

## Snippet 2
Lines 16-39

```Python
class PerplexityChat:
    MODELS = {
        "sonar-reasoning-pro": {
            "id": "sonar-reasoning-pro",
            "context_length": 127000,
            "description": "Advanced reasoning and analysis"
        },
        "sonar-reasoning": {
            "id": "sonar-reasoning",
            "context_length": 127000,
            "description": "Enhanced reasoning capabilities"
        },
        "sonar-pro": {
            "id": "sonar-pro",
            "context_length": 200000,
            "description": "Professional grade completion"
        },
        "sonar": {
            "id": "sonar",
            "context_length": 127000,
            "description": "Standard chat completion"
        }
    }
```

## Snippet 3
Lines 40-49

```Python
def __init__(self, api_key: str):
        """Initialize the Perplexity client with the provided API key."""
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        # Initialize with a system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 4
Lines 50-63

```Python
def list_models(self) -> List[Dict]:
        """
        Get available Perplexity models.

        Returns:
            List[Dict]: List of available models with their details.
        """
        return [
            {
                "id": model_id,
                "name": model_id,
                "context_length": info["context_length"],
                "description": info["description"]
            }
```

## Snippet 5
Lines 67-113

```Python
def stream_chat_response(
        self,
        message: str,
        model: str = "sonar",
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """
        Stream a chat response from Perplexity.

        Args:
            message (str): The user's input message.
            model (str): The Perplexity model to use.
            temperature (float): Response temperature (0.0 to 1.0).

        Yields:
            str: Chunks of the response text as they arrive.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Add user message to history
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
                stream=True,
                timeout=60  # adjust timeout as needed
            )
            response.raise_for_status()
```

## Snippet 6
Lines 115-117

```Python
if line:
                    try:
                        line_text = line.decode('utf-8')
```

## Snippet 7
Lines 126-129

```Python
if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                yield content
```

## Snippet 8
Lines 130-136

```Python
except json.JSONDecodeError:
                        # Possibly a keep-alive or partial chunk; ignore and continue
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue
```

## Snippet 9
Lines 137-142

```Python
# Add assistant's response to history after complete stream
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })
```

## Snippet 10
Lines 153-159

```Python
def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]
```

## Snippet 11
Lines 162-170

```Python
# ------------------------------------------------------------------

API_KEY = "pplx-REPLACE_WITH_YOUR_PERPLEXITY_API_KEY"

app = FastAPI(title="MCP Server with Perplexity")

# Simple in-memory session store
sessions: Dict[str, PerplexityChat] = {}
```

## Snippet 12
Lines 175-180

```Python
class SseRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    model: Optional[str] = "sonar"
    temperature: Optional[float] = 0.7
```

## Snippet 13
Lines 199-206

```Python
Provide server metadata for MCP clients.
    """
    return {
        "name": "PerplexityMCP",
        "description": "A Python MCP server that streams from Perplexity API.",
        "version": "1.0.0",
    }
```

## Snippet 14
Lines 208-228

```Python
def get_tools():
    """
    Return a list of available 'tools' in the MCP format.
    """
    return [
        {
            "slug": "perplexityChat",
            "displayName": "Perplexity Chat",
            "description": "Use Perplexity API to chat with advanced language models.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "User query or message"},
                    "model": {"type": "string", "description": "Which Perplexity model to use"},
                    "temperature": {"type": "number", "description": "Sampling temperature"}
                },
                "required": ["message"]
            }
        }
    ]
```

## Snippet 15
Lines 230-237

```Python
def get_models():
    """
    Return a list of available models from PerplexityChat.
    """
    # For simplicity, use a temporary instance to list models.
    chat = PerplexityChat(API_KEY)
    return chat.list_models()
```

## Snippet 16
Lines 241-244

```Python
Return a list of 'resources' if your server also offers resource endpoints.
    """
    return []
```

## Snippet 17
Lines 246-250

```Python
def sse_endpoint(request_data: SseRequest):
    """
    An SSE endpoint that streams Perplexity’s response in the form:
        data: <text chunk>\n\n
    """
```

## Snippet 18
Lines 251-258

```Python
if request_data.session_id and request_data.session_id in sessions:
        chat = sessions[request_data.session_id]
        session_id = request_data.session_id
    else:
        session_id = str(uuid4())
        chat = PerplexityChat(API_KEY)
        sessions[session_id] = chat
```

## Snippet 19
Lines 261-266

```Python
for chunk in chat.stream_chat_response(
                request_data.message,
                request_data.model,
                request_data.temperature
            ):
                yield f"data: {chunk}\n\n"
```

## Snippet 20
Lines 267-270

```Python
except Exception as e:
            print(f"Stream error: {e}", file=sys.stderr)
            yield f"data: [Error processing stream]\n\n"
```

## Snippet 21
Lines 275-278

```Python
def clear_session(request_data: ClearRequest):
    """
    Clears the conversation session so that future calls start fresh.
    """
```

## Snippet 22
Lines 279-285

```Python
if request_data.session_id in sessions:
        sessions[request_data.session_id].clear_conversation()
        del sessions[request_data.session_id]
        return {"message": "Session cleared."}
    else:
        raise HTTPException(status_code=404, detail="Session not found.")
```

