# Code Snippets from toollama/finished/ollama_wayback.py

File: `toollama/finished/ollama_wayback.py`  
Language: Python  
Extracted: 2025-06-07 05:10:40  

## Snippet 1
Lines 2-10

```Python
Tool-using setup for Ollama with Wayback Machine integration
"""

import json
import requests
from typing import Dict, Any, List
from tools.llm_tool_wayback import Tools
import re
```

## Snippet 2
Lines 12-16

```Python
def __init__(self, model: str = "drummer-wayback"):
        self.model = model
        self.wayback_tool = Tools()
        self.base_url = "http://localhost:11434/api/chat"
```

## Snippet 3
Lines 17-31

```Python
def generate(self, prompt: str) -> str:
        """Generate a response from Ollama"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()

            # Ensure we have a complete JSON object
```

## Snippet 4
Lines 34-40

```Python
if not content.endswith("}"):
                content += "}"

            # Validate JSON structure
            json.loads(content)
            return content
```

## Snippet 5
Lines 41-47

```Python
except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {content}")
            raise
```

## Snippet 6
Lines 50-53

```Python
if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
```

## Snippet 7
Lines 54-58

```Python
def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
```

## Snippet 8
Lines 65-69

```Python
elif tool_name == "get_capture_history":
            return self.wayback_tool.get_capture_history(**params)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
```

## Snippet 9
Lines 79-83

```Python
else:
                    data = result["data"]
                    return (f"Found snapshot of {result['original_url']}\n"
                           f"Date: {data.get('timestamp', 'unknown')}\n"
                           f"URL: {data.get('url', 'not available')}")
```

## Snippet 10
Lines 88-97

```Python
def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)

            # Parse and execute the tool call
            tool_call = json.loads(response)
            tool_result = self.execute_tool(tool_call)
```

## Snippet 11
Lines 101-104

```Python
except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
```

## Snippet 12
Lines 107-115

```Python
def main():
    print("\nWayback Machine Archive Tool")
    print("Commands:")
    print("- Enter a URL directly: example.com")
    print("- Search with date: show me example.com from 2020")
    print("- Get history: history of example.com")
    print("Type 'quit' to exit\n")

    agent = OllamaToolUser()
```

## Snippet 13
Lines 116-118

```Python
while True:
        try:
            user_input = input("\nEnter request: ").strip()
```

## Snippet 14
Lines 127-132

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
```

