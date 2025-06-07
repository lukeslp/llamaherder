# Code Snippets from toollama/finished/ollama_finance.py

File: `toollama/finished/ollama_finance.py`  
Language: Python  
Extracted: 2025-06-07 05:10:48  

## Snippet 1
Lines 2-11

```Python
Tool-using setup for Ollama with Finance integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
import asyncio
from typing import Dict, Any
from tools.llm_tool_finance import Tools
```

## Snippet 2
Lines 15-20

```Python
def __init__(self, model: str = "drummer-finance"):
        """Initialize the finance router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.finance_tool = Tools()
```

## Snippet 3
Lines 21-36

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
Lines 39-53

```Python
if not content.endswith("}"):
                content += "}"

            # Validate JSON structure
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError:
                print("\nWarning: Invalid JSON response from model. Attempting to fix...")
                # Attempt to fix common JSON issues
                content = content.replace("'", '"')
                content = content.replace("None", "null")
                json.loads(content)  # Validate again
                return content
```

## Snippet 5
Lines 54-63

```Python
except requests.exceptions.RequestException as e:
            print(f"\nNetwork error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"\nInvalid JSON: {content}")
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            raise
```

## Snippet 6
Lines 64-67

```Python
def format_output(self, result: str) -> str:
        """Format finance results with enhanced accessibility"""
        return result
```

## Snippet 7
Lines 68-73

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified finance tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
```

## Snippet 8
Lines 74-80

```Python
if tool_name == "analyze_asset":
                result = await self.finance_tool.analyze_asset(**params)
            else:
                return f"Error: Unknown tool {tool_name}"

            return self.format_output(result)
```

## Snippet 9
Lines 81-84

```Python
except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"
```

## Snippet 10
Lines 85-99

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
                print(f"\nInvalid JSON response: {response}")
                return "Invalid response format. Please try a more specific request."
            except Exception as e:
                print(f"\nError executing tool: {str(e)}")
```

## Snippet 11
Lines 107-122

```Python
"""Main function to run the finance tool with enhanced help"""
    processor = OllamaFinanceUser()

    print("\nFinance Analysis Tool")
    print("\nAvailable Commands:")
    print("Stock Analysis:")
    print("- 'analyze TICKER'")
    print("- 'analyze stock TICKER'")
    print("- Example: analyze AAPL")

    print("\nCrypto Analysis:")
    print("- 'analyze crypto SYMBOL'")
    print("- Example: analyze BTC-USD")

    print("\nType 'quit' to exit\n")
```

## Snippet 12
Lines 123-125

```Python
while True:
        try:
            request = input("\nEnter request: ").strip()
```

## Snippet 13
Lines 126-132

```Python
if request.lower() == 'quit':
                print("Exiting...")
                break

            result = await processor.run_interaction(request)
            print("\n" + result)
```

## Snippet 14
Lines 133-136

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
```

