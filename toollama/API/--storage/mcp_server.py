import sys
import json
import requests
from uuid import uuid4
from typing import Generator, List, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# ------------------------------------------------------------------
# Perplexity API Chat Implementation (same core logic as before)
# ------------------------------------------------------------------

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

    def __init__(self, api_key: str):
        """Initialize the Perplexity client with the provided API key."""
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        # Initialize with a system message
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

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
            for model_id, info in self.MODELS.items()
        ]

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
            
            for line in response.iter_lines():
                if line:
                    try:
                        line_text = line.decode('utf-8')
                        if line_text.startswith("data: "):
                            line_text = line_text[6:]  # Remove "data: " prefix
                        if line_text == "[DONE]":
                            break
                        
                        data = json.loads(line_text)
                        if data.get("choices") and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                content = delta["content"]
                                full_response += content
                                yield content
                    except json.JSONDecodeError:
                        # Possibly a keep-alive or partial chunk; ignore and continue
                        continue
                    except Exception as e:
                        print(f"Error processing chunk: {e}", file=sys.stderr)
                        continue

            # Add assistant's response to history after complete stream
            self.chat_history.append({
                "role": "assistant",
                "content": full_response
            })

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            # Remove the user message if request failed
            if self.chat_history and self.chat_history[-1]["role"] == "user":
                self.chat_history.pop()
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if self.chat_history and self.chat_history[-1]["role"] == "user":
                self.chat_history.pop()

    def clear_conversation(self):
        """Clear the conversation history, keeping only the system message."""
        self.chat_history = [{
            "role": "system",
            "content": "You are a helpful AI assistant focused on accurate and insightful responses."
        }]

# ------------------------------------------------------------------
# FastAPI App (MCP Server)
# ------------------------------------------------------------------

API_KEY = "pplx-REPLACE_WITH_YOUR_PERPLEXITY_API_KEY"

app = FastAPI(title="MCP Server with Perplexity")

# Simple in-memory session store
sessions: Dict[str, PerplexityChat] = {}

# ---------------------
# MCP Data Models
# ---------------------

class SseRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    model: Optional[str] = "sonar"
    temperature: Optional[float] = 0.7

class ClearRequest(BaseModel):
    session_id: str

# ---------------------
# MCP Endpoints
# ---------------------

@app.get("/", response_class=JSONResponse)
def root():
    return {"status": "ok", "message": "MCP Perplexity server running."}

@app.get("/health", response_class=JSONResponse)
def health():
    return {"status": "ok"}

@app.get("/.well-known/mcp", response_class=JSONResponse)
def well_known_mcp():
    """
    Provide server metadata for MCP clients.
    """
    return {
        "name": "PerplexityMCP",
        "description": "A Python MCP server that streams from Perplexity API.",
        "version": "1.0.0",
    }

@app.get("/tools", response_class=JSONResponse)
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

@app.get("/models", response_class=JSONResponse)
def get_models():
    """
    Return a list of available models from PerplexityChat.
    """
    # For simplicity, use a temporary instance to list models.
    chat = PerplexityChat(API_KEY)
    return chat.list_models()

@app.get("/resources", response_class=JSONResponse)
def get_resources():
    """
    Return a list of 'resources' if your server also offers resource endpoints.
    """
    return []

@app.post("/sse")
def sse_endpoint(request_data: SseRequest):
    """
    An SSE endpoint that streams Perplexity’s response in the form:
        data: <text chunk>\n\n
    """
    if request_data.session_id and request_data.session_id in sessions:
        chat = sessions[request_data.session_id]
        session_id = request_data.session_id
    else:
        session_id = str(uuid4())
        chat = PerplexityChat(API_KEY)
        sessions[session_id] = chat

    def event_stream():
        try:
            for chunk in chat.stream_chat_response(
                request_data.message,
                request_data.model,
                request_data.temperature
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            print(f"Stream error: {e}", file=sys.stderr)
            yield f"data: [Error processing stream]\n\n"

    headers = {"X-Session-ID": session_id}
    return StreamingResponse(event_stream(), media_type="text/event-stream", headers=headers)

@app.post("/clear", response_class=JSONResponse)
def clear_session(request_data: ClearRequest):
    """
    Clears the conversation session so that future calls start fresh.
    """
    if request_data.session_id in sessions:
        sessions[request_data.session_id].clear_conversation()
        del sessions[request_data.session_id]
        return {"message": "Session cleared."}
    else:
        raise HTTPException(status_code=404, detail="Session not found.")

# ------------------------------------------------------------------
# Main Entry Point
# ------------------------------------------------------------------

if __name__ == "__main__":
    # Run the FastAPI app directly.
    uvicorn.run(app, host="0.0.0.0", port=8435)