# Code Snippets from toollama/API/examples/use_extension_tools.py

File: `toollama/API/examples/use_extension_tools.py`  
Language: Python  
Extracted: 2025-06-07 05:17:26  

## Snippet 1
Lines 1-16

```Python
#!/usr/bin/env python
"""
Example script demonstrating how to use the Camina API extension tools.

This script shows how to use the code execution, text analysis, and data
formatting tools through the API, both directly and via AI tool calling.
"""

import requests
import json
import os
import sys

# API base URL - change this to match your deployment
API_URL = "http://localhost:8435/v2"
```

## Snippet 2
Lines 20-24

```Python
if isinstance(result, dict):
        print(json.dumps(result, indent=2))
    else:
        print(result)
    print("=" * (len(label) + 8))
```

## Snippet 3
Lines 27-33

```Python
def execute_python_code(code):
    """Execute Python code using the code execution tool."""
    response = requests.post(
        f"{API_URL}/tools/execute/code",
        json={"code": code}
    )
    return response.json()
```

## Snippet 4
Lines 37-42

```Python
"""Analyze text for sentiment, entities, and offensive content."""
    response = requests.post(
        f"{API_URL}/tools/analyze/text",
        json={"text": text, "language": language}
    )
    return response.json()
```

## Snippet 5
Lines 45-51

```Python
def format_data(data, target_format="yaml", style="pretty"):
    """Convert data between different formats."""
    response = requests.post(
        f"{API_URL}/tools/process/format",
        json={"data": data, "target_format": target_format, "style": style}
    )
    return response.json()
```

## Snippet 6
Lines 54-65

```Python
def use_tool_via_ai(prompt, tool_schema, provider="anthropic", model="claude-3-opus-20240229"):
    """Use a tool through an AI provider's tool calling interface."""
    response = requests.post(
        f"{API_URL}/tools/call",
        json={
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "tools": [tool_schema]
        }
    )
    return response.json()
```

## Snippet 7
Lines 68-71

```Python
def get_tool_schemas():
    """Get all available extension tool schemas."""
    response = requests.get(f"{API_URL}/tools/schemas/extensions")
    return response.json()
```

## Snippet 8
Lines 74-83

```Python
if __name__ == "__main__":
    # Example 1: Direct code execution
    code_result = execute_python_code("""
import math
import random

# Calculate the square root of a random number
number = random.randint(1, 100)
result = math.sqrt(number)
```

## Snippet 9
Lines 87-123

```Python
data = [random.randint(1, 100) for _ in range(10)]
print(f"Random data: {data}")
print(f"Average: {sum(data)/len(data):.2f}")
""")
    print_result("1. Code Execution Result", code_result)

    # Example 2: Text analysis
    text_result = analyze_text(
        "I absolutely love this product! It's the best purchase I've made this year. "
        "The customer service from Apple was excellent too."
    )
    print_result("2. Text Analysis Result", text_result)

    # Example 3: Data formatting
    data = {
        "users": [
            {"name": "John Doe", "age": 32, "occupation": "Developer"},
            {"name": "Jane Smith", "age": 28, "occupation": "Designer"},
            {"name": "Bob Johnson", "age": 45, "occupation": "Manager"}
        ],
        "company": "Acme Inc.",
        "location": "New York",
        "founded": 2005
    }

    # Convert to YAML
    yaml_result = format_data(data, "yaml", "pretty")
    print_result("3a. Data Formatting (YAML)", yaml_result)

    # Convert to XML
    xml_result = format_data(data, "xml", "pretty")
    print_result("3b. Data Formatting (XML)", xml_result)

    # Convert to CSV (works best with list data)
    csv_result = format_data(data["users"], "csv", "pretty")
    print_result("3c. Data Formatting (CSV from list)", csv_result)
```

## Snippet 10
Lines 124-129

```Python
# Example 4: Using tools via AI (if you have API access to providers)
    try:
        # Get the tool schemas
        schemas = get_tool_schemas()

        # Find the code execution schema
```

## Snippet 11
Lines 132-139

```Python
if code_schema:
            ai_result = use_tool_via_ai(
                "Calculate the first 10 Fibonacci numbers using Python code.",
                code_schema
            )
            print_result("4. AI Tool Calling Result", ai_result)
        else:
            print("Code execution schema not found")
```

## Snippet 12
Lines 140-142

```Python
except Exception as e:
        print(f"Error using AI tool calling: {str(e)}")
        print("This part requires API access to a provider like Anthropic or OpenAI")
```

