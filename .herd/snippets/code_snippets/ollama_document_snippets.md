# Code Snippets from toollama/finished/ollama_document.py

File: `toollama/finished/ollama_document.py`  
Language: Python  
Extracted: 2025-06-07 05:10:43  

## Snippet 1
Lines 2-16

```Python
Tool-using setup for Ollama with Document Management integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
from typing import Dict, Any, Optional
from tools.llm_tool_document import Tools
import asyncio
import sys
from pathlib import Path
import os
import re
from collections import defaultdict
```

## Snippet 2
Lines 20-25

```Python
def __init__(self, model: str = "drummer-document"):
        """Initialize the document management router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.document_tool = Tools()
```

## Snippet 3
Lines 26-41

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
Lines 44-58

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
Lines 59-68

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
Lines 74-81

```Python
if "result" in data and "format" in data:  # OCR results
                output = [
                    "OCR Processing Results:",
                    f"Language: {data.get('language', 'Unknown')}",
                    f"Format: {data.get('format')}",
                    f"Pages Processed: {data.get('pages', 1)}"
                ]
```

## Snippet 7
Lines 82-86

```Python
if data.get('format') == "markdown":
                    output.extend([
                        "\nExtracted Text:",
                        data.get('result')
                    ])
```

## Snippet 8
Lines 87-101

```Python
elif data.get('format') == "json":
                    output.extend([
                        "\nExtracted Text (JSON):",
                        f"```json\n{json.dumps(data.get('result'), indent=2)}\n```"
                    ])
                else:  # text
                    output.extend([
                        "\nExtracted Text:",
                        "```",
                        data.get('result'),
                        "```"
                    ])

                return "\n".join(output)
```

## Snippet 9
Lines 126-138

```Python
for doc in data.get('documents', []):
                    output.extend([
                        f"\n{doc.get('title')}",
                        f"ID: {doc.get('id')}",
                        f"Type: {doc.get('document_type')}",
                        f"Created: {doc.get('created_date')}",
                        f"Correspondent: {doc.get('correspondent')}",
                        "Tags: " + ", ".join(doc.get('tags', [])),
                        "---"
                    ])

                return "\n".join(output)
```

## Snippet 10
Lines 139-145

```Python
elif "organized" in data:  # File organization results
                output = [
                    "File Organization Results:",
                    f"Total Organized: {data.get('total_organized', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
```

## Snippet 11
Lines 179-186

```Python
elif "archived" in data:  # Archive results
                output = [
                    "Archive Creation Results:",
                    f"Archive: {data.get('archive')}",
                    f"Total Archived: {data.get('total_archived', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
```

## Snippet 12
Lines 199-205

```Python
elif "deleted" in data:  # Deletion results
                output = [
                    "File Deletion Results:",
                    f"Total Deleted: {data.get('total_deleted', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
```

## Snippet 13
Lines 222-227

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified document management tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
```

## Snippet 14
Lines 232-238

```Python
elif tool_name == "manage_files":
                result = await self.document_tool.manage_files(**params)
            else:
                return f"Error: Unknown tool {tool_name}"

            return self.format_output(result)
```

## Snippet 15
Lines 239-242

```Python
except Exception as e:
            print(f"\nTool execution error: {str(e)}", file=sys.stderr)
            return f"Error executing {tool_name}: {str(e)}"
```

## Snippet 16
Lines 243-257

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

## Snippet 17
Lines 265-290

```Python
"""Main function to run the document management tool with enhanced help"""
    processor = OllamaDocumentUser()

    print("\nDocument Management Tool")
    print("\nAvailable Commands:")
    print("OCR Processing:")
    print("- 'extract text from FILE'")
    print("- 'process FILE in LANGUAGE'")
    print("- Formats: text, json, markdown")
    print("- Options: language, metadata")

    print("\nPaperless Integration:")
    print("- 'find documents TYPE'")
    print("- 'search TAG in YEAR'")
    print("- 'get documents from CORRESPONDENT'")
    print("- Filters: type, tag, correspondent, year, month")

    print("\nFile Management:")
    print("- 'organize DIRECTORY'")
    print("- 'move/copy FILES to DESTINATION'")
    print("- 'archive FILES as ARCHIVE'")
    print("- 'delete FILES'")
    print("- Options: recursive, pattern, create_dirs")

    print("\nType 'quit' to exit\n")
```

## Snippet 18
Lines 291-293

```Python
while True:
        try:
            request = input("\nEnter request: ").strip()
```

## Snippet 19
Lines 294-300

```Python
if request.lower() == 'quit':
                print("Exiting...")
                break

            result = await processor.run_interaction(request)
            print("\n" + result)
```

## Snippet 20
Lines 301-304

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
```

