# Code Snippets from toollama/finished/ollama_knowledge.py

File: `toollama/finished/ollama_knowledge.py`  
Language: Python  
Extracted: 2025-06-07 05:10:37  

## Snippet 1
Lines 2-15

```Python
Tool-using setup for Ollama with Knowledge Base integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
from typing import Dict, Any, Optional
from tools.llm_tool_knowledge import Tools
import asyncio
import sys
from pathlib import Path
import os
import re
```

## Snippet 2
Lines 19-24

```Python
def __init__(self, model: str = "drummer-knowledge"):
        """Initialize the knowledge base router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.knowledge_tool = Tools()
```

## Snippet 3
Lines 25-40

```Python
def generate(self, prompt: str) -> str:
        """Generate a response from Ollama with enhanced error handling"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        try:
            response = requests.post(self.base_url, json=data, timeout=30)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()

            # Ensure we have a complete JSON object
```

## Snippet 4
Lines 43-57

```Python
if not content.endswith("}"):
                content += "}"

            # Validate JSON structure
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError:
                print("\nWarning: Invalid JSON response from model. Attempting to fix...", file=sys.stderr)
                # Attempt to fix common JSON issues
                content = content.replace("'", '"')
                content = re.sub(r'(\w+):', r'"\1":', content)
                json.loads(content)  # Validate again
                return content
```

## Snippet 5
Lines 58-67

```Python
except requests.exceptions.RequestException as e:
            print(f"\nNetwork error: {e}", file=sys.stderr)
            raise
        except json.JSONDecodeError as e:
            print(f"\nInvalid JSON: {content}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            raise
```

## Snippet 6
Lines 73-79

```Python
if "results" in data and "format" in data:  # Wikidata results
                output = [
                    "Wikidata Query Results:",
                    f"Format: {data.get('format')}",
                    f"Results Found: {data.get('count', 0)}"
                ]
```

## Snippet 7
Lines 80-88

```Python
if data.get('format') == "raw":
                    output.extend([
                        "\nRaw Results:",
                        "```json",
                        json.dumps(data.get('results'), indent=2),
                        "```"
                    ])
                else:
                    output.append("\nResults:")
```

## Snippet 8
Lines 97-104

```Python
elif "result" in data and "format" in data:  # Wolfram Alpha results
                output = [
                    "Wolfram Alpha Results:",
                    f"Format: {data.get('format')}",
                    f"Query: {data.get('query')}"
                ]

                result = data.get('result', {})
```

## Snippet 9
Lines 126-132

```Python
elif "results" in data and "mode" in data:  # Perplexity results
                output = [
                    "Perplexity Search Results:",
                    f"Mode: {data.get('mode')}",
                    f"Results Found: {data.get('count', 0)}"
                ]
```

## Snippet 10
Lines 137-142

```Python
for i, res in enumerate(data.get('results', []), 1):
                    output.extend([
                        f"\n{i}. {res.get('title')}",
                        f"   URL: {res.get('url')}",
                        f"   {res.get('snippet')}"
                    ])
```

## Snippet 11
Lines 150-155

```Python
elif "transcript" in data:  # YouTube transcript
                output = [
                    "YouTube Transcript Results:",
                    f"URL: {data.get('url')}"
                ]
```

## Snippet 12
Lines 156-163

```Python
if "metadata" in data:
                    meta = data["metadata"]
                    output.extend([
                        f"Title: {meta.get('title')}",
                        f"Author: {meta.get('author')}",
                        f"Views: {meta.get('view_count')}",
                        f"Published: {meta.get('publish_date')}"
                    ])
```

## Snippet 13
Lines 164-169

```Python
if meta.get('description'):
                        output.extend([
                            "\nDescription:",
                            meta['description']
                        ])
```

## Snippet 14
Lines 170-178

```Python
output.extend([
                    "\nTranscript:",
                    "```",
                    data.get('transcript'),
                    "```"
                ])

                return "\n".join(output)
```

## Snippet 15
Lines 183-188

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified knowledge base tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
```

## Snippet 16
Lines 195-201

```Python
elif tool_name == "get_youtube_transcript":
                result = await self.knowledge_tool.get_youtube_transcript(**params)
            else:
                return f"Error: Unknown tool {tool_name}"

            return self.format_output(result)
```

## Snippet 17
Lines 202-205

```Python
except Exception as e:
            print(f"\nTool execution error: {str(e)}", file=sys.stderr)
            return f"Error executing {tool_name}: {str(e)}"
```

## Snippet 18
Lines 206-220

```Python
async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with enhanced error handling"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)

            # Parse and execute the tool call
            try:
                tool_call = json.loads(response)
                return await self.execute_tool(tool_call)
            except json.JSONDecodeError:
                print(f"\nInvalid JSON response: {response}", file=sys.stderr)
                return "Invalid response format. Please try a more specific request."
            except Exception as e:
                print(f"\nError executing tool: {str(e)}", file=sys.stderr)
```

## Snippet 19
Lines 228-234

```Python
"""Main function to run the knowledge base tool with enhanced help"""
    processor = OllamaKnowledgeUser()

    print("\nKnowledge Base Tool")
    print("\nAvailable Commands:")
    print("Wikidata Queries:")
    print("- 'find ENTITY'")
```

## Snippet 20
Lines 235-244

```Python
print("- 'search for TOPIC'")
    print("- Formats: simple, detailed, raw")

    print("\nWolfram Alpha:")
    print("- 'calculate EXPRESSION'")
    print("- 'solve PROBLEM'")
    print("- Formats: plain, math, image")
    print("- Options: steps, units")

    print("\nPerplexity Search:")
```

## Snippet 21
Lines 245-256

```Python
print("- 'search for TOPIC'")
    print("- 'research TOPIC'")
    print("- Modes: search, academic, writing, analysis")
    print("- Options: citations, recent only")

    print("\nYouTube Transcripts:")
    print("- 'get transcript from URL'")
    print("- 'transcribe video URL'")
    print("- Options: language, metadata")

    print("\nType 'quit' to exit\n")
```

## Snippet 22
Lines 257-259

```Python
while True:
        try:
            request = input("\nEnter request: ").strip()
```

## Snippet 23
Lines 260-266

```Python
if request.lower() == 'quit':
                print("Exiting...")
                break

            result = await processor.run_interaction(request)
            print("\n" + result)
```

## Snippet 24
Lines 267-270

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
```

