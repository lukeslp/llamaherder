# Code Snippets from toollama/finished/ollama_coderunner.py

File: `toollama/finished/ollama_coderunner.py`  
Language: Python  
Extracted: 2025-06-07 05:10:47  

## Snippet 1
Lines 1-10

```Python
import json
import requests
from typing import Dict, Any
import asyncio
import platform
import subprocess
import tempfile
import os
import re
```

## Snippet 2
Lines 14-43

```Python
def __init__(self, model: str = "drummer-code"):
        """Initialize the code router"""
        self.model = model
        self.base_url = "http://localhost:11434/api"

        # Import available tools
        try:
            from llm_tool_infinite_search import Tools as InfiniteSearch
            self.infinite_tool = InfiniteSearch()
        except ImportError:
            self.infinite_tool = None

        try:
            from llm_tool_wayback import Tools as WaybackMachine
            self.wayback_tool = WaybackMachine()
        except ImportError:
            self.wayback_tool = None

        try:
            from llm_tool_arxiv import Tools as ArxivSearch
            self.arxiv_tool = ArxivSearch()
        except ImportError:
            self.arxiv_tool = None

        try:
            from llm_tool_coderunner import Tools as CodeRunner
            self.code_tool = CodeRunner()
        except ImportError:
            self.code_tool = None
```

## Snippet 3
Lines 44-86

```Python
def generate(self, prompt: str) -> str:
        """Generate a response from Ollama using structured outputs"""
        data = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string",
                        "enum": ["run_python_code", "run_bash_command", "google_search", "bing_search", "baidu_search", "read_url", "get_archived_snapshot", "get_capture_history", "search_papers"]
                    },
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "command": {"type": "string"},
                            "query": {"type": "string"},
                            "url": {"type": "string"},
                            "topic": {"type": "string"},
                            "timestamp": {"type": "string"}
                        }
                    }
                },
                "required": ["tool", "parameters"]
            }
        }

        try:
            response = requests.post(f"{self.base_url}/chat", json=data)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            print("\nRaw LLM Response:", repr(content))

            try:
                # Parse the JSON response
                parsed = json.loads(content)

                # Validate required fields
```

## Snippet 4
Lines 91-96

```Python
if not isinstance(parsed["parameters"], dict):
                    raise ValueError("'parameters' must be an object")

                # Clean and return the response
                return json.dumps(parsed)
```

## Snippet 5
Lines 97-103

```Python
except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {str(e)}")
                raise
            except ValueError as e:
                print(f"Validation Error: {str(e)}")
                raise
```

## Snippet 6
Lines 104-110

```Python
except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except Exception as e:
            print(f"Error parsing response: {e}")
            raise
```

## Snippet 7
Lines 111-117

```Python
async def execute_tool(self, tool_response: str) -> None:
        """Execute the appropriate tool based on the response"""
        try:
            parsed = json.loads(tool_response)
            tool_name = parsed["tool"]
            params = parsed["parameters"]
```

## Snippet 8
Lines 119-125

```Python
if self.code_tool:
                    result = await self.code_tool.run_python_code(params["code"])
                    print("\nPython Output:")
                    print(result)
                else:
                    print("Python code runner not available")
```

## Snippet 9
Lines 127-133

```Python
if self.code_tool:
                    result = await self.code_tool.run_bash_command(params["command"])
                    print("\nBash Output:")
                    print(result)
                else:
                    print("Bash command runner not available")
```

## Snippet 10
Lines 135-141

```Python
if self.infinite_tool:
                    result = await self.infinite_tool.google_search(params["query"])
                    print("\nSearch Results:")
                    print(json.dumps(result, indent=2))
                else:
                    print("Google search tool not available")
```

## Snippet 11
Lines 143-149

```Python
if self.infinite_tool:
                    result = await self.infinite_tool.bing_search(params["query"])
                    print("\nSearch Results:")
                    print(json.dumps(result, indent=2))
                else:
                    print("Bing search tool not available")
```

## Snippet 12
Lines 151-157

```Python
if self.infinite_tool:
                    result = await self.infinite_tool.baidu_search(params["query"])
                    print("\nSearch Results:")
                    print(json.dumps(result, indent=2))
                else:
                    print("Baidu search tool not available")
```

## Snippet 13
Lines 159-165

```Python
if self.infinite_tool:
                    result = await self.infinite_tool.read_url(params["url"])
                    print("\nURL Content:")
                    print(result)
                else:
                    print("URL reader tool not available")
```

## Snippet 14
Lines 167-173

```Python
if self.wayback_tool:
                    result = await self.wayback_tool.get_archived_snapshot(params["url"], params.get("timestamp"))
                    print("\nWayback Machine Snapshot:")
                    print(json.dumps(result, indent=2))
                else:
                    print("Wayback Machine tool not available")
```

## Snippet 15
Lines 175-181

```Python
if self.wayback_tool:
                    result = await self.wayback_tool.get_capture_history(params["url"])
                    print("\nWayback Machine History:")
                    print(json.dumps(result, indent=2))
                else:
                    print("Wayback Machine tool not available")
```

## Snippet 16
Lines 183-189

```Python
if self.arxiv_tool:
                    result = await self.arxiv_tool.search_papers(params["topic"])
                    print("\nPaper Search Results:")
                    print(json.dumps(result, indent=2))
                else:
                    print("arXiv search tool not available")
```

## Snippet 17
Lines 197-201

```Python
"""Main function to run the code router"""
    router = OllamaCodeRouter()

    print("\nCode Router Tool")
    print("\nAvailable Tools:")
```

## Snippet 18
Lines 202-208

```Python
if router.code_tool:
        print("✓ Code Runner:")
        print("  - Run Python scripts")
        print("  - Run Bash commands")
    else:
        print("✗ Code Runner not available")
```

## Snippet 19
Lines 209-217

```Python
if router.infinite_tool:
        print("\n✓ Search & Web:")
        print("  - Google Search")
        print("  - Bing Search")
        print("  - Baidu Search")
        print("  - Read URL content")
    else:
        print("\n✗ Search tools not available")
```

## Snippet 20
Lines 218-224

```Python
if router.wayback_tool:
        print("\n✓ Internet Archive:")
        print("  - Get archived snapshots")
        print("  - View capture history")
    else:
        print("\n✗ Internet Archive tools not available")
```

## Snippet 21
Lines 225-239

```Python
if router.arxiv_tool:
        print("\n✓ Academic Search:")
        print("  - Search arXiv papers")
    else:
        print("\n✗ Academic search not available")

    print("\nCommands:")
    print("- 'write a python script that...' or 'run python code...'")
    print("- 'run command...' or 'execute...'")
    print("- 'search google/bing/baidu for...'")
    print("- 'read content from URL...'")
    print("- 'check wayback machine for...'")
    print("- 'find papers about...'")
    print("Type 'quit' to exit\n")
```

## Snippet 22
Lines 240-242

```Python
while True:
        try:
            request = input("\nEnter request: ").strip()
```

## Snippet 23
Lines 243-249

```Python
if request.lower() == 'quit':
                print("Exiting...")
                break

            response = router.generate(request)
            await router.execute_tool(response)
```

## Snippet 24
Lines 250-253

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
```

