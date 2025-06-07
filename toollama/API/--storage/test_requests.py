#!/usr/bin/env python
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import requests
    print(f"Requests module path: {requests.__file__}")
    print(f"Requests module dir: {dir(requests)}")
    
    # Check if there's a local module named requests
    if 'requests' in sys.modules:
        print(f"Requests module is loaded from: {sys.modules['requests']}")
    
    # Try to import requests in a different way
    import importlib
    requests_spec = importlib.util.find_spec("requests")
    print(f"Requests spec: {requests_spec}")
    
    # Try to use requests directly
    try:
        print("Testing requests.get...")
        response = requests.get("https://httpbin.org/get")
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"Error with requests.get: {e}")
    
    try:
        print("Testing requests.post...")
        response = requests.post("https://httpbin.org/post", json={"test": "data"})
        print(f"Response status code: {response.status_code}")
    except Exception as e:
        print(f"Error with requests.post: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 