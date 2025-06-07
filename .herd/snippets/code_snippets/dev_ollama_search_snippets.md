# Code Snippets from toollama/soon/tools_pending/dev_ollama_search.py

File: `toollama/soon/tools_pending/dev_ollama_search.py`  
Language: Python  
Extracted: 2025-06-07 05:14:30  

## Snippet 1
Lines 2-11

```Python
Tool-using setup for Ollama with Web Search integration
"""

import json
import requests
from typing import Dict, Any, List
from rejects.dev_llm_tool_websearch import Tools
import re
import asyncio
```

## Snippet 2
Lines 13-20

```Python
def __init__(self, model: str = "drummer-search:3b"):
        self.model = model
        self.search_tool = Tools()
        # Configure search engine URL - replace with your SearXNG instance
        self.search_tool.valves.SEARXNG_ENGINE_API_BASE_URL = "https://searx.be/search"
        self.search_tool.valves.RETURNED_SCRAPPED_PAGES_NO = 5
        self.base_url = "http://localhost:11434/api/chat"
```

## Snippet 3
Lines 21-35

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
Lines 38-44

```Python
if not content.endswith("}"):
                content += "}"

            # Validate JSON structure
            json.loads(content)
            return content
```

## Snippet 5
Lines 45-51

```Python
except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {content}")
            raise
```

## Snippet 6
Lines 54-57

```Python
if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
```

## Snippet 7
Lines 58-62

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
```

## Snippet 8
Lines 63-65

```Python
if tool_name == "search_web":
            result = await self.search_tool.search_web(**params)
            return json.loads(result)
```

## Snippet 9
Lines 67-70

```Python
if "url" in params:
                params["url"] = self.normalize_url(params["url"])
            result = await self.search_tool.get_website(**params)
            return json.loads(result)
```

## Snippet 10
Lines 76-79

```Python
if not results:
            return "No results found."

        output = []
```

## Snippet 11
Lines 81-87

```Python
if isinstance(result, dict):
                title = result.get("title", "Untitled")
                url = result.get("url", "No URL")
                excerpt = result.get("excerpt", result.get("snippet", ""))[:200] + "..."

                output.append(f"\n{idx}. {title}")
                output.append(f"   URL: {url}")
```

## Snippet 12
Lines 88-91

```Python
if excerpt:
                    output.append(f"   Summary: {excerpt}")
                output.append("")
```

## Snippet 13
Lines 94-103

```Python
async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)

            # Parse and execute the tool call
            tool_call = json.loads(response)
            tool_result = await self.execute_tool(tool_call)
```

## Snippet 14
Lines 108-110

```Python
if "error" in tool_result:
                    return f"Error: {tool_result['error']}"
                return self.format_search_result([tool_result])
```

## Snippet 15
Lines 114-117

```Python
except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
```

## Snippet 16
Lines 120-128

```Python
async def main():
    print("\nWeb Search Tool")
    print("Commands:")
    print("- Search query: what's new with AI?")
    print("- Check website: check example.com")
    print("- Research topic: tell me about quantum computing")
    print("Type 'quit' to exit\n")

    agent = OllamaSearchUser()
```

## Snippet 17
Lines 129-131

```Python
while True:
        try:
            user_input = input("\nEnter request: ").strip()
```

## Snippet 18
Lines 140-145

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
```

