# Code Snippets from toollama/API/--storage/simple_requests.py

File: `toollama/API/--storage/simple_requests.py`  
Language: Python  
Extracted: 2025-06-07 05:16:52  

## Snippet 1
Lines 1-12

```Python
#!/usr/bin/env python
import requests

print("Testing requests.get...")
response = requests.get("https://httpbin.org/get")
print(f"Response status code: {response.status_code}")

print("Testing requests.post...")
response = requests.post("https://httpbin.org/post", json={"test": "data"})
print(f"Response status code: {response.status_code}")

print("Requests module is working correctly!")
```

