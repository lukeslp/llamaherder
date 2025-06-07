# Code Snippets from toollama/finished/ollama_infinite.py

File: `toollama/finished/ollama_infinite.py`  
Language: Python  
Extracted: 2025-06-07 05:10:55  

## Snippet 1
Lines 2-12

```Python
Tool-using setup for Ollama with Infinite Search integration
"""

import json
import requests
from typing import Dict, Any, List
from tools.llm_tool_infinite_search import Tools
import re
import asyncio
from bs4 import BeautifulSoup
```

## Snippet 2
Lines 14-22

```Python
def __init__(self, model: str = "belter-infinite"):
        self.model = model
        self.search_tool = Tools()
        # Configure search engine URL and settings
        self.search_tool.valves.SEARXNG_URL = "https://searx.be/search"
        self.search_tool.valves.TIMEOUT = 60
        print(f"\nInitialized with search URL: {self.search_tool.valves.SEARXNG_URL}")
        self.base_url = "http://localhost:11434/api/chat"
```

## Snippet 3
Lines 23-38

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
            print("\nLLM Response:", content)  # Debug print

            # Ensure we have a complete JSON object
```

## Snippet 4
Lines 41-47

```Python
if not content.endswith("}"):
                content += "}"

            # Validate JSON structure
            json.loads(content)
            return content
```

## Snippet 5
Lines 48-54

```Python
except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {content}")
            raise
```

## Snippet 6
Lines 57-60

```Python
if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url
```

## Snippet 7
Lines 61-66

```Python
def extract_urls_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract URLs and titles from the search result text"""
        results = []
        lines = text.split('\n')
        current_title = ""
```

## Snippet 8
Lines 69-74

```Python
if current_title:
                    results.append({
                        "title": current_title,
                        "url": line.strip()
                    })
                    current_title = ""
```

## Snippet 9
Lines 80-88

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
            print(f"\nExecuting tool: {tool_name}")
            print(f"Parameters: {params}")
```

## Snippet 10
Lines 89-93

```Python
if tool_name == "google_search":
                result = await self.search_tool.google_search(**params)
                print("\nRaw search result:")
                print(result)
                return {"content": result, "type": "search"}
```

## Snippet 11
Lines 94-98

```Python
elif tool_name == "bing_search":
                result = await self.search_tool.bing_search(**params)
                print("\nRaw search result:")
                print(result)
                return {"content": result, "type": "search"}
```

## Snippet 12
Lines 99-103

```Python
elif tool_name == "baidu_search":
                result = await self.search_tool.baidu_search(**params)
                print("\nRaw search result:")
                print(result)
                return {"content": result, "type": "search"}
```

## Snippet 13
Lines 105-108

```Python
if "url" in params:
                    params["url"] = self.normalize_url(params["url"])
                result = await self.search_tool.read_url(**params)
                return {"content": result, "type": "article"}
```

## Snippet 14
Lines 111-115

```Python
except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            print(f"Error type: {type(e)}")
            return {"error": f"Error executing {tool_name}: {str(e)}"}
```

## Snippet 15
Lines 118-125

```Python
if "error" in result:
            return f"Error: {result['error']}"

        content = result.get("content", "")
        result_type = result.get("type", "unknown")

        print("\nFormatting result type:", result_type)
```

## Snippet 16
Lines 126-130

```Python
if result_type == "search":
            # First, try to find the search results section
            search_section = None
            content_parts = content.split("<system>")
```

## Snippet 17
Lines 132-136

```Python
if content_parts:
                search_section = content_parts[0].strip()

            print("\nSearch section:", search_section)
```

## Snippet 18
Lines 137-144

```Python
if not search_section:
                return "No search results found."

            # Extract URLs and titles
            lines = search_section.split('\n')
            results = []
            current_item = {}
```

## Snippet 19
Lines 164-168

```Python
if not results:
                return "No relevant results could be extracted."

            # Format output
            output = ["Search Results:"]
```

## Snippet 20
Lines 169-174

```Python
for idx, item in enumerate(results[:5], 1):
                output.append(f"\n{idx}. {item['title']}")
                output.append(f"   URL: {item['url']}")

            return "\n".join(output)
```

## Snippet 21
Lines 176-182

```Python
if not content:
                return "No content could be extracted from the article."

            # Remove system instructions
            content = re.sub(r"<system>.*?</system>", "", content, flags=re.DOTALL)

            # Split into paragraphs and limit length
```

## Snippet 22
Lines 184-189

```Python
if not paragraphs:
                return "No readable content found in the article."

            summary = "\n\n".join(paragraphs[:3]) + "\n\n[Content truncated...]"
            return f"Article Content:\n\n{summary}"
```

## Snippet 23
Lines 192-201

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

## Snippet 24
Lines 205-208

```Python
except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
```

## Snippet 25
Lines 211-220

```Python
async def main():
    print("\nInfinite Search Tool")
    print("Commands:")
    print("- Google search: find latest AI news")
    print("- Bing search: search WCAG documentation")
    print("- Baidu search: search Chinese tech news")
    print("- Read URL: read https://example.com/article")
    print("Type 'quit' to exit\n")

    agent = OllamaInfiniteUser()
```

## Snippet 26
Lines 221-223

```Python
while True:
        try:
            user_input = input("\nEnter request: ").strip()
```

## Snippet 27
Lines 232-237

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
```

