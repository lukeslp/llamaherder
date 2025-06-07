import requests
import json

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
        
        if 'text/event-stream' in response.headers.get('Content-Type', ''):
            print("\nParsing streaming response...")
            content = []
            for line in response.text.split('\n'):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if 'content' in data:
                            content.append(data['content'])
                        print(f"Parsed chunk: {data}")
                    except json.JSONDecodeError:
                        continue
            if content:
                print(f"\nFinal content: {''.join(content)}")
        else:
            try:
                response_data = response.json()
                print(f"\nParsed JSON response: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"\nFailed to parse JSON: {e}")
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    test_api() 