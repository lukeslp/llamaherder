# Code Snippets from toollama/finished/ollama_web.py

File: `toollama/finished/ollama_web.py`  
Language: Python  
Extracted: 2025-06-07 05:10:45  

## Snippet 1
Lines 1-13

```Python
#!/usr/bin/env python3
"""Web search and scraping tool using Ollama with multiple backends."""

import json
import asyncio
import requests
from typing import Dict, Any, Optional, List
from tools.llm_tool_webscrape import Tools as ScrapeTools
from tools.llm_tool_infinite_search import Tools as SearchTools
from tools.llm_tool_knowledge import Tools as KnowledgeTools
import re
import os
```

## Snippet 2
Lines 15-23

```Python
def __init__(self, model="belter-web", base_url="http://localhost:11434/api/chat"):
        """Initialize the web tools with model and various backends."""
        self.model = model
        self.base_url = base_url
        self.scrape_tool = ScrapeTools()
        self.search_tool = SearchTools()
        self.knowledge_tool = KnowledgeTools()
        print("\nInitialized web tools")
```

## Snippet 3
Lines 26-29

```Python
if not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url
```

## Snippet 4
Lines 30-75

```Python
def generate(self, prompt: str) -> str:
        """Generate a response from Ollama"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": """You are a web search and scraping assistant.
                Available tools:
                1. web_scrape: Scrape content from a URL
                   Parameters: {"url": "example.com"}
                2. google_search: Search using Google
                   Parameters: {"query": "search terms"}
                3. bing_search: Search using Bing
                   Parameters: {"query": "search terms"}
                4. perplexity_search: Search using Perplexity AI
                   Parameters: {"query": "search terms", "mode": "search|academic|writing|analysis"}

                Respond with a JSON object containing:
                {
                    "tool": "tool_name",
                    "parameters": {
                        // tool specific parameters
                    }
                }"""},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        try:
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            print("\nRaw LLM Response:", repr(content))

            # Clean and parse JSON response
            content = self._clean_json_response(content)

            try:
                parsed = json.loads(content)

                # Normalize the response based on tool type
                clean_response = {
                    "tool": parsed.get("tool", ""),
                    "parameters": {}
                }
```

## Snippet 5
Lines 88-90

```Python
except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {str(e)}")
                # Handle direct URL inputs
```

## Snippet 6
Lines 91-99

```Python
if isinstance(prompt, str) and (prompt.startswith("http") or "." in prompt):
                    return json.dumps({
                        "tool": "web_scrape",
                        "parameters": {
                            "url": self.normalize_url(prompt)
                        }
                    })
                raise
```

## Snippet 7
Lines 100-106

```Python
except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except Exception as e:
            print(f"Error parsing response: {e}")
            raise
```

## Snippet 8
Lines 107-113

```Python
def _clean_json_response(self, content: str) -> str:
        """Clean and format JSON response from LLM"""
        content = content.encode().decode('unicode_escape')

        # Extract JSON part
        json_start = content.find("{")
        json_end = content.rfind("}")
```

## Snippet 9
Lines 114-135

```Python
if json_start >= 0 and json_end >= 0:
            content = content[json_start:json_end + 1]

        # Basic cleaning
        content = (content.replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("'", '"'))

        # Fix JSON formatting issues
        content = (content.replace('\\"', '"')
                        .replace('""', '"')
                        .strip())

        # Remove spaces between JSON elements
        content = re.sub(r'\s*:\s*', ':', content)
        content = re.sub(r'\s*,\s*', ',', content)
        content = re.sub(r'\s*{\s*', '{', content)
        content = re.sub(r'\s*}\s*', '}', content)

        return content
```

## Snippet 10
Lines 136-141

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
```

## Snippet 11
Lines 144-148

```Python
if not url:
                    return "Error: No URL provided"
                print(f"\nScraping URL: {url}")
                return await self.scrape_tool.web_scrape(url)
```

## Snippet 12
Lines 151-155

```Python
if not query:
                    return "Error: No search query provided"
                print(f"\nPerforming Google search: {query}")
                return await self.search_tool.google_search(query)
```

## Snippet 13
Lines 158-162

```Python
if not query:
                    return "Error: No search query provided"
                print(f"\nPerforming Bing search: {query}")
                return await self.search_tool.bing_search(query)
```

## Snippet 14
Lines 174-177

```Python
except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"
```

## Snippet 15
Lines 178-193

```Python
async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)

            # Parse and execute the tool call
            tool_call = json.loads(response)
            result = await self.execute_tool(tool_call)

            return result

        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
```

## Snippet 16
Lines 197-208

```Python
"""Main function to run the web tools."""
    web_tools = OllamaWebUser()

    print("\nWeb Search and Scraping Tool")
    print("Commands:")
    print("- Direct URL: example.com")
    print("- Scrape: scrape example.com")
    print("- Google Search: search python programming")
    print("- Bing Search: bing machine learning")
    print("- Perplexity: perplexity quantum computing")
    print("Type 'quit' to exit\n")
```

## Snippet 17
Lines 209-211

```Python
while True:
        try:
            user_input = input("\nEnter request: ").strip()
```

## Snippet 18
Lines 218-222

```Python
except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
```

