#!/usr/bin/env python3

import os
import sys
import json
import requests
import time
import logging
from pathlib import Path
from io import BytesIO
import mimetypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set API base URL
API_BASE_URL = "https://api.assisted.space/v2"

# Output directory for test results
OUTPUT_DIR = "test_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Test document paths
TEST_PDF = "test_document.pdf"  # This should be a path to a valid PDF file in your environment

def get_mime_type(file_path):
    """Get the MIME type of a file."""
    # Initialize mimetypes if needed
    if not mimetypes.inited:
        mimetypes.init()
        
    # Get mime type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Default to application/octet-stream if type couldn't be determined
    if mime_type is None:
        mime_type = "application/octet-stream"
        
    return mime_type

def create_test_file():
    """Create a test text file if it doesn't exist."""
    if os.path.exists(TEST_PDF):
        return
        
    print(f"Creating test text file with .pdf extension...")
    try:
        # Create a simple text file with .pdf extension
        with open(TEST_PDF, 'w') as f:
            f.write("This is a test document.\n\n")
            f.write("It contains text that can be processed by AI models.\n")
        print("Created simple text file with .pdf extension")
    except Exception as e:
        print(f"Error creating test file: {e}")

def test_responses_endpoint(model="gpt-4o-mini", prompt="Tell me what major news happened today"):
    """
    Test the responses API endpoint for document processing.
    
    Args:
        model (str): The model to use for processing.
        prompt (str): The prompt to use for processing.
        
    Returns:
        dict: The response from the API.
    """
    print(f"Testing POST {API_BASE_URL}/responses")
    print(f"Using model: {model}")
    print(f"Using prompt: {prompt}")
    
    try:
        # Add your API key
        api_key = "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"
        
        # Add headers with API key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Prepare the request data
        data = {
            'model': model,
            'prompt': prompt,
            'tools': [{'type': 'web_search_preview'}]
        }
        
        # Make the request
        print(f"Sending request to {API_BASE_URL}/responses...")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(
            f"{API_BASE_URL}/responses",
            json=data,
            headers=headers,
            timeout=30
        )
        
        # Print the response status and content
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        
        # Save the response to a file
        output_file = os.path.join(OUTPUT_DIR, "responses_test.json")
        with open(output_file, 'w') as f:
            f.write(response.text)
            
        print(f"Response saved to {output_file}")
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print("POST to /responses endpoint succeeded")
            
            # If we got a response_id, try to retrieve the response
            if 'response_id' in data:
                response_id = data['response_id']
                status = data.get('status', '')
                
                print(f"\nGot response_id: {response_id}, status: {status}")
                
                if status != "completed":
                    print("Response is still processing. Waiting a moment and then retrieving...")
                    time.sleep(5)  # Wait a moment before trying to retrieve
                    
                    # Retrieve the response
                    retrieve_url = f"{API_BASE_URL}/responses/{response_id}"
                    print(f"Retrieving response from: {retrieve_url}")
                    
                    # Use API key in the header for retrieving too
                    retrieve_response = requests.get(
                        retrieve_url, 
                        headers=headers,
                        timeout=30
                    )
                    print(f"Retrieve response status: {retrieve_response.status_code}")
                    print(f"Retrieve response content: {retrieve_response.text}")
                    
                    # Save the retrieve response to a file
                    retrieve_output_file = os.path.join(OUTPUT_DIR, f"responses_{response_id}_retrieve.json")
                    with open(retrieve_output_file, 'w') as f:
                        f.write(retrieve_response.text)
                        
                    print(f"Retrieve response saved to {retrieve_output_file}")
                    
                    if retrieve_response.status_code == 200:
                        print(f"GET from /responses/{response_id} succeeded")
                        retrieve_data = retrieve_response.json()
                        
                        if 'content' in retrieve_data:
                            print("\nContent retrieved successfully!")
                            return retrieve_data
                        else:
                            print(f"\nNo content available yet. Status: {retrieve_data.get('status', 'unknown')}")
                            return retrieve_data
                    else:
                        print(f"GET from /responses/{response_id} failed")
                        return {"error": f"Failed to retrieve response: {retrieve_response.text}"}
                else:
                    # If the response was completed immediately
                    print("\nResponse was completed immediately!")
                    return data
            else:
                # If no response_id was returned but the request was successful
                return data
        else:
            print("POST to /responses endpoint failed")
            return {"error": f"Request failed with status code {response.status_code}: {response.text}"}
    
    except Exception as e:
        print(f"Error in test_responses_endpoint: {str(e)}")
        return {"error": str(e)}

def test_responses_endpoint_stream(model="gpt-4o-mini", prompt="What was a positive news story from today?"):
    """
    Test the responses API endpoint for document processing with streaming.
    
    Args:
        model (str): The model to use for processing.
        prompt (str): The prompt to use for processing.
        
    Returns:
        dict: A summary of the streaming test results.
    """
    # Use the consolidated /responses endpoint for streaming
    responses_url = f"{API_BASE_URL}/responses"
    print(f"\n--- Testing Streaming POST {responses_url} ---")
    print(f"Using model: {model}")
    print(f"Using prompt: {prompt}")
    
    try:
        # Add your API key
        api_key = "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"
        
        # Add headers with API key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Prepare the request data
        data = {
            'model': model,
            'prompt': prompt,
            'tools': [{'type': 'web_search_preview'}],
            'stream': True
        }
        
        # Make the request
        print(f"Sending streaming request to {responses_url}...")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        with requests.post(
            responses_url,
            json=data,
            headers=headers,
            stream=True, 
            timeout=30
        ) as response:
            # Print the response status and content
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            # Save the response to a file
            output_file = os.path.join(OUTPUT_DIR, "responses_stream_test.json")
            with open(output_file, 'w') as f:
                # Process the stream and collect the response
                full_response = ""
                for chunk in response.iter_content(decode_unicode=True):
                    if chunk:
                        # Write chunk to file
                        f.write(chunk)
                        # Print chunk to console
                        print(chunk, end='')
                        # Add to full response
                        full_response += chunk
                                   
            print(f"\nStreaming complete. Full response saved to {output_file}")
            print(f"Full Response:\n{full_response}")

            if full_response and not full_response.startswith("Error:"):
                print("\nStreaming POST to stream_test endpoint appears successful.")
                return {
                    "status": "success", 
                    "response": full_response,
                    "output_file": output_file
                }
            else:
                error_msg = "No response received or error in response"
                print(f"\nStreaming POST to stream_test endpoint failed: {error_msg}")
                return {
                    "status": "failure", 
                    "error": error_msg,
                    "response": full_response,
                    "output_file": output_file
                }
    
    except Exception as e:
        print(f"Error in test_responses_endpoint_stream: {str(e)}")
        return {"error": str(e)}

def test_function_calling_endpoint(model="gpt-4o-mini", prompt="What's the weather like in Boston?"):
    """
    Test the responses API endpoint with function calling.
    
    Args:
        model (str): The model to use for processing.
        prompt (str): The prompt to use for processing.
        
    Returns:
        dict: The response from the API.
    """
    print(f"Testing POST {API_BASE_URL}/responses with function calling")
    print(f"Using model: {model}")
    print(f"Using prompt: {prompt}")
    
    try:
        # Add your API key
        api_key = "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"
        
        # Add headers with API key
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Define the weather tool
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                            },
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                        },
                        "required": ["location", "unit"],
                    }
                }
            }
        ]
        
        # Prepare the request data
        data = {
            'model': model,
            'messages': [{"role": "user", "content": prompt}],  # Format as messages array
            'tools': tools,
            'tool_choice': 'auto'
        }
        
        # Make the request
        print(f"Sending request to {API_BASE_URL}/responses...")
        print(f"Headers: {headers}")
        print(f"Data: {data}")
        
        response = requests.post(
            f"{API_BASE_URL}/responses",
            json=data,
            headers=headers,
            timeout=30
        )
        
        # Print the response status and content
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        
        # Save the response to a file
        output_file = os.path.join(OUTPUT_DIR, "responses_function_test.json")
        with open(output_file, 'w') as f:
            f.write(response.text)
            
        print(f"Response saved to {output_file}")
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            print("POST to /responses endpoint succeeded")
            return data
        else:
            print("POST to /responses endpoint failed")
            return {"error": f"Request failed with status code {response.status_code}: {response.text}"}
    
    except Exception as e:
        print(f"Error in test_function_calling_endpoint: {str(e)}")
        return {"error": str(e)}

if __name__ == '__main__':
    print("=== Testing OpenAI Responses API ===")
    # Test both streaming and non-streaming endpoints
    print("\nTesting streaming endpoint...")
    stream_result = test_responses_endpoint_stream()
    print("\nTesting non-streaming endpoint...")
    result = test_responses_endpoint()
    print("\nTesting function calling endpoint...")
    function_result = test_function_calling_endpoint()
    
    print("\n=== Test Complete ===")
    if "error" in stream_result or "error" in result or "error" in function_result:
        print("Tests failed!")
        if "error" in stream_result:
            print(f"Streaming test error: {stream_result['error']}")
        if "error" in result:
            print(f"Non-streaming test error: {result['error']}")
        if "error" in function_result:
            print(f"Function calling test error: {function_result['error']}")
        sys.exit(1)
    else:
        print("All tests succeeded!")
        sys.exit(0) 