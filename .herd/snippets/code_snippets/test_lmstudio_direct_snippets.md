# Code Snippets from toollama/API/--storage/test_lmstudio_direct.py

File: `toollama/API/--storage/test_lmstudio_direct.py`  
Language: Python  
Extracted: 2025-06-07 05:16:49  

## Snippet 1
Lines 1-8

```Python
#!/usr/bin/env python
import requests
import json
import sys

# LM Studio server URL
base_url = "http://192.168.0.32:8001"
```

## Snippet 2
Lines 9-13

```Python
def test_models():
    """Test the models endpoint"""
    print("Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/v1/models")
```

## Snippet 3
Lines 14-16

```Python
if response.status_code == 200:
            print(f"Success! Status code: {response.status_code}")
            data = response.json()
```

## Snippet 4
Lines 18-20

```Python
else:
            print(f"Error: Status code: {response.status_code}")
            print(response.text)
```

## Snippet 5
Lines 24-39

```Python
def test_completion():
    """Test the chat completion endpoint"""
    print("\nTesting chat completion endpoint...")
    try:
        payload = {
            "model": "mistral-7b-instruct",
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "max_tokens": 100,
            "stream": False
        }

        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload
        )
```

## Snippet 6
Lines 40-42

```Python
if response.status_code == 200:
            print(f"Success! Status code: {response.status_code}")
            data = response.json()
```

## Snippet 7
Lines 43-47

```Python
if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"Response: {content}")
            else:
                print(f"Unexpected response format: {data}")
```

## Snippet 8
Lines 48-50

```Python
else:
            print(f"Error: Status code: {response.status_code}")
            print(response.text)
```

