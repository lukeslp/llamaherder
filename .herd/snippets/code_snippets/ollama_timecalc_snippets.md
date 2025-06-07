# Code Snippets from toollama/finished/ollama_timecalc.py

File: `toollama/finished/ollama_timecalc.py`  
Language: Python  
Extracted: 2025-06-07 05:10:42  

## Snippet 1
Lines 2-11

```Python
Tool-using setup for Ollama with Time & Calculation integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
import asyncio
from typing import Dict, Any
from tools.llm_tool_timecalc import Tools
```

## Snippet 2
Lines 15-20

```Python
def __init__(self, model: str = "drummer-timecalc"):
        """Initialize the time and calculation router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.timecalc_tool = Tools()
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
Lines 77-81

```Python
elif "difference" in data:  # Time difference
                output = [
                    "Time Difference Results:",
                    f"Time 1: {data.get('time1')}",
                    f"Time 2: {data.get('time2')}",
```

## Snippet 7
Lines 86-90

```Python
elif "expression" in data:  # Math evaluation
                output = [
                    "Math Evaluation Results:",
                    f"Expression: {data.get('expression')}"
                ]
```

## Snippet 8
Lines 103-107

```Python
if len(zones) > 20:
                    zones = zones[:20]
                    return f"Available Timezones (showing first 20 of {len(data.get('timezones', []))}):\n" + "\n".join(zones)
                return "Available Timezones:\n" + "\n".join(zones)
```

## Snippet 9
Lines 112-117

```Python
async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified time or calculation tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})

        try:
```

## Snippet 10
Lines 126-132

```Python
elif tool_name == "list_timezones":
                result = self.timecalc_tool.list_timezones(**params)
            else:
                return f"Error: Unknown tool {tool_name}"

            return self.format_output(result)
```

## Snippet 11
Lines 133-136

```Python
except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"
```

## Snippet 12
Lines 137-151

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

## Snippet 13
Lines 159-176

```Python
"""Main function to run the time and calculation tool with enhanced help"""
    processor = OllamaTimeCalcUser()

    print("\nTime & Calculation Tool")
    print("\nAvailable Commands:")
    print("Time Operations:")
    print("- 'convert TIME to TIMEZONE'")
    print("- 'time difference between TIME1 and TIME2'")
    print("- 'current time in TIMEZONE'")
    print("- 'list timezones [FILTER]'")

    print("\nMath Operations:")
    print("- 'calculate EXPRESSION'")
    print("- 'evaluate EXPRESSION with VAR1=VALUE1, VAR2=VALUE2'")
    print("- Supports: +, -, *, /, ^, sin, cos, tan, log, sqrt, pi, e")

    print("\nType 'quit' to exit\n")
```

## Snippet 14
Lines 177-179

```Python
while True:
        try:
            request = input("\nEnter request: ").strip()
```

## Snippet 15
Lines 180-186

```Python
if request.lower() == 'quit':
                print("Exiting...")
                break

            result = await processor.run_interaction(request)
            print("\n" + result)
```

## Snippet 16
Lines 187-190

```Python
except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
```

