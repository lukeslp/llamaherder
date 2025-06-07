# Code Snippets from toollama/API/api-tools/tools/Untitled/geospy.py

File: `toollama/API/api-tools/tools/Untitled/geospy.py`  
Language: Python  
Extracted: 2025-06-07 05:20:03  

## Snippet 1
Lines 1-5

```Python
from runtime import Args
from typings.geoPredict.geoPredict import Input, Output
import base64
import requests
```

## Snippet 2
Lines 6-13

```Python
def encode_image_to_base64(image_url: str) -> str:
    """
    Encodes an image from a URL to a base64 string.
    """
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode("utf-8")
```

## Snippet 3
Lines 14-29

```Python
def send_request(image_base64: str, api_key: str, endpoint_url: str):
    """
    Sends an HTTP POST request to the GeoSpy AI API with the encoded image.
    """
    payload = {
        "image": image_base64,
        "top_k": 5  # Optional, adjust as needed
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint_url, json=payload, headers=headers)
    return response.json()
```

## Snippet 4
Lines 32-45

```Python
Handler function that integrates with GeoSpy API.
    """
    # Extract input parameters
    image_url = args.input.image
    api_key = args.input.api_key
    endpoint_url = "https://dev.geospy.ai/predict"

    # Encode image and send request
    image_base64 = encode_image_to_base64(image_url)
    result = send_request(image_base64, api_key, endpoint_url)

    # Log and return the result
    args.logger.info(f"API Response: {result}")
    return {"message": result}
```

