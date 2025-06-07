# Code Snippets from toollama/storage/test_api.py

File: `toollama/storage/test_api.py`  
Language: Python  
Extracted: 2025-06-07 05:11:21  

## Snippet 1
Lines 4-36

```Python
def test_api():
    url = "https://actuallyusefulai.com/api/v1/prod/chat/drummer"

    # Test message
    data = {
        "model": "llama3.2:3b",
        "messages": [
            {
                "role": "user",
                "content": "why is the sky blue?"
            }
        ],
        # "stream": False
    }

    print("\n🚀 Sending request...")
    print(f"Request data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(
            url,
            json=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )

        print(f"\n📡 Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"\nRaw response text:\n{response.text[:1000]}")
```

## Snippet 2
Lines 41-43

```Python
if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
```

## Snippet 3
Lines 44-46

```Python
if 'content' in data:
                            content.append(data['content'])
                        print(f"Parsed chunk: {data}")
```

## Snippet 4
Lines 51-57

```Python
else:
            try:
                response_data = response.json()
                print(f"\nParsed JSON response: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"\nFailed to parse JSON: {e}")
```

