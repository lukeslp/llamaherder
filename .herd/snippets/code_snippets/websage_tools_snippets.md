# Code Snippets from toollama/API/--storage/websage_tools.py

File: `toollama/API/--storage/websage_tools.py`  
Language: Python  
Extracted: 2025-06-07 05:16:45  

## Snippet 1
Lines 6-21

```Python
for web searching and content extraction, following Ollama's tool calling format.

Requirements:
- Ollama installed with the WebSage model created
- requests library
- The infinite_search.py tool (adapted from the original)
"""

import json
import requests
import asyncio
import sys
from typing import List, Dict, Any, Optional, Callable
import uuid
import time
```

## Snippet 2
Lines 23-36

```Python
# Adjust the import path as needed for your setup
sys.path.append('./api-tools/tools/tools/tools2')
try:
    from infinite_search import Tools
except ImportError:
    print("Error: Could not import Tools from infinite_search.")
    print("Please ensure the infinite_search.py file is in the correct location.")
    print("Expected path: ./api-tools/tools/tools/tools2/infinite_search.py")
    sys.exit(1)

# Ollama API settings
OLLAMA_API_URL = "http://localhost:11434/api"
MODEL_NAME = "websage"  # The name you used when creating the model
```

## Snippet 3
Lines 38-121

```Python
def __init__(self):
        self.tools = Tools()
        self.conversation_history = []

        # Define the tools that will be available to the model
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "google_search",
                    "description": "Search the web using Google search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on Google"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "bing_search",
                    "description": "Search the web using Bing search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on Bing"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "baidu_search",
                    "description": "Search the web using Baidu search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on Baidu"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_url",
                    "description": "Extract and read content from a specified URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to extract content from"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]

        # Map tool names to their implementation functions
        self.tool_implementations = {
            "google_search": self._google_search,
            "bing_search": self._bing_search,
            "baidu_search": self._baidu_search,
            "read_url": self._read_url
        }
```

## Snippet 4
Lines 122-129

```Python
async def _google_search(self, query: str) -> str:
        """Implementation of the google_search tool"""
        try:
            result = await self.tools.google_search(query)
            return result
        except Exception as e:
            return f"Error performing Google search: {str(e)}"
```

## Snippet 5
Lines 130-137

```Python
async def _bing_search(self, query: str) -> str:
        """Implementation of the bing_search tool"""
        try:
            result = await self.tools.bing_search(query)
            return result
        except Exception as e:
            return f"Error performing Bing search: {str(e)}"
```

## Snippet 6
Lines 138-145

```Python
async def _baidu_search(self, query: str) -> str:
        """Implementation of the baidu_search tool"""
        try:
            result = await self.tools.baidu_search(query)
            return result
        except Exception as e:
            return f"Error performing Baidu search: {str(e)}"
```

## Snippet 7
Lines 146-153

```Python
async def _read_url(self, url: str) -> str:
        """Implementation of the read_url tool"""
        try:
            result = await self.tools.read_url(url)
            return result
        except Exception as e:
            return f"Error reading URL {url}: {str(e)}"
```

## Snippet 8
Lines 154-159

```Python
async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        try:
            function_name = tool_call.get("function", {}).get("name")
            function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
```

## Snippet 9
Lines 160-167

```Python
if function_name not in self.tool_implementations:
                return {
                    "tool_call_id": tool_call.get("id"),
                    "role": "tool",
                    "content": f"Error: Tool '{function_name}' not found"
                }

            # Execute the appropriate tool function
```

## Snippet 10
Lines 174-183

```Python
elif function_name == "read_url":
                result = await self._read_url(function_args.get("url", ""))
            else:
                result = "Error: Unknown tool"

            return {
                "tool_call_id": tool_call.get("id"),
                "role": "tool",
                "content": result
            }
```

## Snippet 11
Lines 184-190

```Python
except Exception as e:
            return {
                "tool_call_id": tool_call.get("id", "unknown"),
                "role": "tool",
                "content": f"Error executing tool: {str(e)}"
            }
```

## Snippet 12
Lines 191-193

```Python
async def chat_with_websage(self, user_message: str) -> str:
        """
        Send a message to the WebSage model and get a response.
```

## Snippet 13
Lines 194-221

```Python
Handles tool calls if the model requests them.

        Args:
            user_message: The user's message

        Returns:
            The model's response
        """
        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Prepare the request to the Ollama API
        url = f"{OLLAMA_API_URL}/chat"
        payload = {
            "model": MODEL_NAME,
            "messages": self.conversation_history,
            "stream": False,
            "tools": self.available_tools
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            # Extract the assistant's message
            assistant_message = result.get("message", {})
```

## Snippet 14
Lines 223-228

```Python
if "tool_calls" in assistant_message:
                # Add the assistant's response with tool calls to the conversation history
                self.conversation_history.append(assistant_message)

                # Process each tool call
                tool_results = []
```

## Snippet 15
Lines 229-249

```Python
for tool_call in assistant_message.get("tool_calls", []):
                    tool_result = await self._execute_tool_call(tool_call)
                    tool_results.append(tool_result)
                    self.conversation_history.append(tool_result)

                # Get the final response after tool execution
                final_payload = {
                    "model": MODEL_NAME,
                    "messages": self.conversation_history,
                    "stream": False,
                    "tools": self.available_tools
                }

                final_response = requests.post(url, json=final_payload)
                final_response.raise_for_status()
                final_result = final_response.json()

                final_message = final_result.get("message", {})
                self.conversation_history.append(final_message)

                return final_message.get("content", "No response after tool execution")
```

## Snippet 16
Lines 250-254

```Python
else:
                # No tool calls, just return the content
                self.conversation_history.append(assistant_message)
                return assistant_message.get("content", "No response")
```

## Snippet 17
Lines 255-259

```Python
except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Ollama API: {str(e)}"
            print(error_message)
            return error_message
```

## Snippet 18
Lines 260-267

```Python
async def run_demo(self):
        """Run an interactive demo of the WebSage model with web search capabilities."""
        print("\n" + "="*80)
        print("WebSage Tools Demo - Web Search & Summary Expert".center(80))
        print("="*80)
        print("\nThis demo shows how to use the WebSage model with proper tool definitions.")
        print("Type 'exit' or 'quit' to end the demo.\n")
```

## Snippet 19
Lines 277-287

```Python
# Process the user input with WebSage
            print("\nWebSage is processing your request...")
            start_time = time.time()

            response = await self.chat_with_websage(user_input)

            end_time = time.time()
            processing_time = end_time - start_time

            # Display the response
            print(f"\nWebSage: {response}")
```

## Snippet 20
Lines 291-293

```Python
"""Check if Ollama is running and the WebSage model exists"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
```

## Snippet 21
Lines 294-298

```Python
if response.status_code != 200:
            print("Error: Could not connect to Ollama API.")
            print("Please ensure Ollama is running on http://localhost:11434")
            return False
```

## Snippet 22
Lines 303-305

```Python
if not model_exists:
            print(f"Error: The '{MODEL_NAME}' model does not exist in Ollama.")
            print("Please create it first using:")
```

## Snippet 23
Lines 310-314

```Python
except requests.exceptions.RequestException:
        print("Error: Could not connect to Ollama API.")
        print("Please ensure Ollama is running on http://localhost:11434")
        return False
```

## Snippet 24
Lines 317-322

```Python
if not check_ollama_status():
        sys.exit(1)

    # Run the demo
    websage = WebSageTools()
    asyncio.run(websage.run_demo())
```

