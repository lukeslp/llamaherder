#!/usr/bin/env python
import requests
import json
import sys

# LM Studio server URL
base_url = "http://192.168.0.32:8001"

def test_models():
    """Test the models endpoint"""
    print("Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/v1/models")
        if response.status_code == 200:
            print(f"Success! Status code: {response.status_code}")
            data = response.json()
            print(f"Found {len(data.get('data', []))} models")
        else:
            print(f"Error: Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error: {str(e)}")

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
        
        if response.status_code == 200:
            print(f"Success! Status code: {response.status_code}")
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                content = data['choices'][0]['message']['content']
                print(f"Response: {content}")
            else:
                print(f"Unexpected response format: {data}")
        else:
            print(f"Error: Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    print(f"Testing connection to LM Studio server at {base_url}")
    test_models()
    test_completion() 