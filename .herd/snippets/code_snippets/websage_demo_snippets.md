# Code Snippets from toollama/API/--storage/websage_demo.py

File: `toollama/API/--storage/websage_demo.py`  
Language: Python  
Extracted: 2025-06-07 05:16:59  

## Snippet 1
Lines 1-19

```Python
#!/usr/bin/env python3
"""
WebSage Demo - Demonstrating the WebSage Ollama model with web search capabilities

This script shows how to use the WebSage model (based on mistral-small) with
the infinite_search.py tool to perform web searches and summarize content.

Requirements:
- Ollama installed with the WebSage model created
- requests library
- The infinite_search.py tool (adapted from the original)
"""

import json
import requests
import asyncio
import sys
from typing import List, Dict, Any, Optional
```

## Snippet 2
Lines 21-34

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
Lines 36-39

```Python
def __init__(self):
        self.tools = Tools()
        self.conversation_history = []
```

## Snippet 4
Lines 40-51

```Python
async def search_and_read(self, query: str, search_engine: str = "google") -> str:
        """
        Perform a web search and read content from the top results.

        Args:
            query: The search query
            search_engine: The search engine to use (google, bing, or baidu)

        Returns:
            A string containing the search results and content
        """
        # Select the appropriate search method based on the engine
```

## Snippet 5
Lines 56-60

```Python
elif search_engine == "baidu":
            search_results = await self.tools.baidu_search(query)
        else:
            return f"Error: Unsupported search engine '{search_engine}'"
```

## Snippet 6
Lines 61-64

```Python
# Extract URLs from search results (simplified for demo)
        # In a real implementation, you would parse the search results properly
        urls = self._extract_urls_from_search_results(search_results)
```

## Snippet 7
Lines 67-69

```Python
for url in urls[:2]:
            try:
                url_content = await self.tools.read_url(url)
```

## Snippet 8
Lines 76-89

```Python
def _extract_urls_from_search_results(self, search_results: str) -> List[str]:
        """
        Extract URLs from search results (simplified implementation).
        In a real application, you would parse the HTML properly.

        Args:
            search_results: The search results HTML

        Returns:
            A list of URLs extracted from the search results
        """
        # This is a very simplified extraction - would need proper HTML parsing in production
        urls = []
        lines = search_results.split('\n')
```

## Snippet 9
Lines 102-137

```Python
async def chat_with_websage(self, user_message: str) -> str:
        """
        Send a message to the WebSage model and get a response.

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
            "stream": False
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            # Extract the assistant's message
            assistant_message = result.get("message", {}).get("content", "No response")

            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama API: {str(e)}"
```

## Snippet 10
Lines 138-145

```Python
async def run_demo(self):
        """Run an interactive demo of the WebSage model with web search capabilities."""
        print("\n" + "="*80)
        print("WebSage Demo - Web Search & Summary Expert".center(80))
        print("="*80)
        print("\nThis demo shows how to use the WebSage model with web search capabilities.")
        print("Type 'exit' or 'quit' to end the demo.\n")
```

## Snippet 11
Lines 156-164

```Python
if user_input.lower().startswith(('search ', 'find ', 'look up ')):
                print("\nPerforming web search...")

                # Extract the search query
                query = user_input.split(' ', 1)[1]

                # Perform the search (default to Google)
                search_results = await self.search_and_read(query)
```

## Snippet 12
Lines 167-173

```Python
websage_prompt = f"I performed a web search for '{query}' and got these results. Please analyze and summarize the key information:\n\n{search_results}"

                # Get WebSage's response
                websage_response = await self.chat_with_websage(websage_prompt)

                # Display the response
                print(f"\nWebSage: {websage_response}")
```

## Snippet 13
Lines 174-179

```Python
else:
                # Regular chat with WebSage
                print("\nSending to WebSage...")
                response = await self.chat_with_websage(user_input)
                print(f"\nWebSage: {response}")
```

## Snippet 14
Lines 181-183

```Python
# Check if Ollama is running
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
```

## Snippet 15
Lines 184-188

```Python
if response.status_code != 200:
            print("Error: Could not connect to Ollama API.")
            print("Please ensure Ollama is running on http://localhost:11434")
            sys.exit(1)
```

## Snippet 16
Lines 193-195

```Python
if not model_exists:
            print(f"Error: The '{MODEL_NAME}' model does not exist in Ollama.")
            print("Please create it first using:")
```

## Snippet 17
Lines 198-205

```Python
except requests.exceptions.RequestException:
        print("Error: Could not connect to Ollama API.")
        print("Please ensure Ollama is running on http://localhost:11434")
        sys.exit(1)

    # Run the demo
    demo = WebSageDemo()
    asyncio.run(demo.run_demo())
```

