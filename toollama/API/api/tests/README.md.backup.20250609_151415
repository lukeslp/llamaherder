# Camina Chat API Test Tools

This directory contains various tools for testing the Camina Chat API functionality.

## Available Test Tools

1. **API Test Server (`api_test_server.py`)**: 
   - Interactive web-based testing interface for the API
   - Provides UI to test various API endpoints, including image generation

2. **Image Generation Test (`test_image_generation.py`)**: 
   - Command-line tool to test image generation across different providers
   - Tests OpenAI, Gemini, and X.AI image generation capabilities

## Using the API Test Server

The API test server provides a web interface for interactively testing different API endpoints.

### Setup

```bash
# Navigate to the project root
cd /path/to/project

# Start the test server
python tests/api_test_server.py
```

### Command Line Options

```
usage: api_test_server.py [-h] [--port PORT] [--api-url API_URL] [--no-browser]

Run the API test server

options:
  -h, --help           show this help message and exit
  --port PORT          Port to run the server on (default: 8000)
  --api-url API_URL    Base URL for the API (default: https://api.assisted.space/v2)
  --no-browser         Do not open the browser automatically
```

### Using the Web Interface

1. The server will start and automatically open your browser to http://localhost:8000/
2. Select the tab for the API functionality you want to test (Image Generation, Chat, etc.)
3. Choose the provider (OpenAI, Gemini, X.AI)
4. Configure your request parameters
5. Click the appropriate button to submit the request
6. View results directly in the browser

## Using the Image Generation Test Script

The `test_image_generation.py` script allows you to test image generation from the command line.

### Running Image Generation Tests

```bash
# Navigate to the project root
cd /path/to/project

# Run tests for all providers
python tests/test_image_generation.py

# Run test with custom environment variables
API_BASE_URL="http://localhost:5000/v2" OPENAI_API_KEY="your-key" python tests/test_image_generation.py
```

### Environment Variables

- `API_BASE_URL`: Base URL for API requests (default: https://api.assisted.space/v2)
- `OPENAI_API_KEY`: API key for OpenAI
- `XAI_API_KEY`: API key for X.AI
- `GEMINI_API_KEY`: API key for Gemini

## Test Output

Test results are saved in the `test_results` directory, with JSON files containing the full API responses.

## Accessibility Considerations

- The web interface is designed with accessibility in mind, using semantic HTML and proper ARIA attributes
- Color contrasts follow WCAG 2.1 AA standards
- All interactive elements are keyboard navigable
- Response data is presented in a structured, readable format 