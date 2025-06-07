# Getting Started with OpenAI Responses API

The OpenAI Responses API offers powerful document processing capabilities with advanced features like web search, file search, function calling, and computer use (code interpreter). This guide will help you get started with using these capabilities.

## Prerequisites

- An API key for the Assisted.Space API
- Documents to process (PDF, text files, etc.)
- Python 3.x (for the examples)

## Basic Usage

### Processing a Simple Document

```python
import requests

with open("document.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Summarize the key points in this document",
            "max_tokens": 4096
        }
    )

result = response.json()
print(result)
```

## Advanced Capabilities

The OpenAI Responses API supports several advanced capabilities:

### 1. Web Search

Enable the model to perform real-time web searches to enhance responses with current information.

```python
import requests

with open("research_paper.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Update this research paper with recent findings and developments",
            "web_search": "true"
        }
    )

result = response.json()
print(result)
```

### 2. File Search

Allow the model to search within the uploaded documents for relevant information.

```python
import requests

with open("large_manual.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Find all sections related to safety precautions and summarize them",
            "file_search": "true"
        }
    )

result = response.json()
print(result)
```

### 3. Function Calling

Define custom tools or functions that the model can invoke based on the user's prompt.

```python
import requests
import json

# Define a weather tool
weather_tool = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }
}]

with open("travel_itinerary.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Check the weather for all destinations in this travel itinerary",
            "tools": json.dumps(weather_tool)
        }
    )

result = response.json()
print(result)

# Check for tool calls in the response
if "tool_calls" in result:
    for tool_call in result["tool_calls"]:
        print(f"Tool called: {tool_call['function']['name']}")
        print(f"Arguments: {tool_call['function']['arguments']}")
```

### 4. Computer Use (Code Interpreter)

Enable the model to perform calculations, execute code, and interact with files programmatically.

```python
import requests

with open("financial_data.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Extract the financial data, calculate growth rates, and create a summary analysis",
            "computer_use": "true"
        }
    )

result = response.json()
print(result)
```

### 5. Combining Multiple Capabilities

You can combine multiple capabilities for more powerful document processing:

```python
import requests
import json

# Define a tool for currency conversion
currency_tool = [{
    "type": "function",
    "function": {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The amount to convert"
                },
                "from_currency": {
                    "type": "string",
                    "description": "The currency code to convert from (e.g., USD)"
                },
                "to_currency": {
                    "type": "string",
                    "description": "The currency code to convert to (e.g., EUR)"
                }
            },
            "required": ["amount", "from_currency", "to_currency"]
        }
    }
}]

with open("international_business_plan.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Analyze this business plan, update market data with current information, convert all financial figures to EUR, and calculate projected ROI",
            "web_search": "true",
            "file_search": "true",
            "computer_use": "true",
            "tools": json.dumps(currency_tool)
        }
    )

result = response.json()
print(result)
```

## Streaming Responses

For long-running processes, you can enable streaming mode:

```python
import requests
import json

with open("document.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Provide a detailed analysis of this document",
            "stream": "true"
        },
        stream=True
    )

for chunk in response.iter_content(chunk_size=1024):
    if chunk:
        try:
            # Parse the chunk as SSE data
            chunk_text = chunk.decode('utf-8')
            for line in chunk_text.strip().split('\n'):
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    if "content" in data:
                        print(data["content"], end='', flush=True)
                    elif "status" in data:
                        print(f"\nStatus update: {data['status']}")
                    elif "tool_calls" in data:
                        print(f"\nTool call: {data['tool_calls']}")
        except Exception as e:
            print(f"Error parsing chunk: {e}")
```

## Retrieving Asynchronous Results

If a response is too large or processing takes time, you may need to retrieve results later:

```python
import requests
import time

# First submit the document
with open("large_document.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Provide a comprehensive analysis of this document"
        }
    )

result = response.json()
response_id = result.get("response_id")
status = result.get("status")

print(f"Response ID: {response_id}")
print(f"Initial status: {status}")

# If not completed, poll for results
if status != "completed" and response_id:
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        print(f"Waiting for processing to complete (attempt {retry_count + 1})...")
        time.sleep(5)  # Wait 5 seconds between checks
        
        # Check status
        response = requests.get(
            f"https://api.assisted.space/v2/responses/{response_id}",
            headers={"X-API-Key": "your_api_key"}
        )
        
        status_result = response.json()
        current_status = status_result.get("status")
        
        print(f"Current status: {current_status}")
        
        if current_status == "completed":
            print(f"Content: {status_result.get('content')}")
            break
        
        retry_count += 1
```

## Best Practices

1. **Choose the right capabilities** - Only enable the capabilities you need to optimize performance.
2. **Be specific in prompts** - Clear instructions yield better results.
3. **Use appropriate models** - More complex tasks typically require more advanced models.
4. **Handle large documents appropriately** - Consider splitting very large documents or using file_search for targeted analysis.
5. **Cache results** - Use the response_id to retrieve previously generated content instead of reprocessing.

## Error Handling

Always include proper error handling in your code:

```python
import requests

try:
    with open("document.pdf", "rb") as f:
        response = requests.post(
            "https://api.assisted.space/v2/responses",
            headers={"X-API-Key": "your_api_key"},
            files={"file": f},
            data={
                "model": "gpt-4o-2024-11-20",
                "prompt": "Summarize this document"
            },
            timeout=60  # Set a reasonable timeout
        )
    
    # Check response status code
    if response.status_code == 200:
        result = response.json()
        print(result)
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        
except FileNotFoundError:
    print("Error: Document file not found")
except requests.exceptions.Timeout:
    print("Error: Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Error: Request failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

For more information, refer to the [full OpenAI Responses API documentation](/docs/openai_responses.md). 