# Code Snippets from toollama/finished/ollama_arxiv.py

File: `toollama/finished/ollama_arxiv.py`  
Language: Python  
Extracted: 2025-06-07 05:10:57  

## Snippet 1
Lines 2-11

```Python
Tool-using setup for Ollama with arXiv integration
"""

import json
import requests
from typing import Dict, Any, List
from tools.llm_tool_arxiv import Tools
import re
import asyncio
```

## Snippet 2
Lines 13-18

```Python
def __init__(self, model: str = "drummer-arxiv"):
        self.model = model
        self.arxiv_tool = Tools()
        self.base_url = "http://localhost:11434/api/chat"
        print("\nInitialized arXiv search tool")
```

## Snippet 3
Lines 19-33

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
            print("\nRaw LLM Response:", repr(content))
```

## Snippet 4
Lines 37-40

```Python
if json_start >= 0 and json_end >= 0:
                content = content[json_start:json_end + 1]

            # Clean up any potential JSON formatting issues
```

## Snippet 5
Lines 45-52

```Python
if not content.endswith('}}'):
                content = content + '}'

            print("Cleaned Response:", repr(content))

            # Validate JSON structure
            try:
                parsed = json.loads(content)
```

## Snippet 6
Lines 57-65

```Python
if "topic" not in parsed["parameters"]:
                    raise ValueError("Missing topic parameter")

                # Clean up the topic - remove extra spaces and normalize case
                parsed["parameters"]["topic"] = parsed["parameters"]["topic"].strip()
                content = json.dumps(parsed)

                print("Parsed JSON:", json.dumps(parsed, indent=2))
                return content
```

## Snippet 7
Lines 66-69

```Python
except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON Error: {str(e)}")
                raise
```

## Snippet 8
Lines 70-76

```Python
except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except Exception as e:
            print(f"Error parsing response: {e}")
            raise
```

## Snippet 9
Lines 77-85

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
            search_topic = params.get('topic', 'unknown topic')
            print(f"\nSearching arXiv for: {search_topic}")
```

## Snippet 10
Lines 101-104

```Python
except Exception as e:
            print(f"\nSearch error: {str(e)}")
            return f"Error searching arXiv: {str(e)}"
```

## Snippet 11
Lines 105-121

```Python
async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)

            # Parse and execute the tool call
            tool_call = json.loads(response)
            result = await self.execute_tool(tool_call)

            # Result is already formatted by the arXiv tool
            return result

        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
```

## Snippet 12
Lines 124-132

```Python
async def main():
    print("\narXiv Paper Search Tool")
    print("Commands:")
    print("- Search papers: find papers about quantum computing")
    print("- Latest research: latest papers on transformers")
    print("- Specific topic: search papers on speech recognition")
    print("Type 'quit' to exit\n")

    agent = OllamaArxivUser()
```

## Snippet 13
Lines 133-135

```Python
while True:
        try:
            user_input = input("\nEnter request: ").strip()
```

## Snippet 14
Lines 144-149

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
```

