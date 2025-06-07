# Assisted.Space API (v2)

A unified API for accessing various AI providers, including Anthropic Claude, OpenAI GPT, Ollama, Perplexity, Mistral, Cohere, X.AI, and Coze.

## API Base URL

All API endpoints are accessible at:
```
https://api.assisted.space/v2
```

For example, to access the chat endpoint:
```
https://api.assisted.space/v2/chat/{provider}
```

## Features

- **Multi-provider Support**: Seamlessly work with multiple AI providers through a single, consistent API.
- **Streaming Support**: Stream responses from AI models in real-time.
- **Chat & Alt Text Generation**: Generate both conversational responses and alt text for images.
- **Function/Tool Calling**: Invoke tools and functions through models that support them.
- **File Management**: Upload, download, and manage files for use with AI models.
- **Document Processing**: Process PDFs and other documents using OpenAI's Responses API.
- **Image Generation**: Create, edit, and generate variations of images using OpenAI's DALL-E models.
- **Dreamwalker Workflows**: Execute complex, multi-step AI workflows (coming soon).

## Current and Planned Providers

### Currently Supported
- **Anthropic Claude**: Claude 3 models (Opus, Sonnet, Haiku)
- **OpenAI**: GPT-4, GPT-4o, and GPT-3.5 models
- **Ollama**: Local open-source models (Llama, Mistral, etc.)
- **Mistral AI**: Mistral Small, Medium, Large, and Pixtral models
- **Cohere**: Command-R+, Command, and Command Light models
- **X.AI**: Grok models including Grok-2 and Grok Vision
- **Coze**: Specialized bots for alt text generation and TTS

### Coming Soon
- **Perplexity**: Sonar models for advanced search and analysis
- **MLX**: Local inference on Apple Silicon devices
- **LM Studio**: API for hosted and local models

## API Endpoints

The API is organized around the following main endpoints:

### Chat Endpoints

- `POST /api.assisted.space/v2/chat/stream`: Stream a chat response from an AI provider
- `POST /api.assisted.space/v2/chat/completions`: Get a non-streaming chat response
- `POST /api.assisted.space/v2/chat/clear`: Clear conversation history

### Alt Text Endpoints

- `POST /api.assisted.space/v2/alt/generate`: Generate alt text for an image

### Document Processing Endpoints

- `POST /api.assisted.space/v2/responses`: Process documents (PDF, text, etc.) using OpenAI's Responses API with advanced capabilities:
  - **Web Search**: Enhance responses with real-time web data
  - **File Search**: Search within documents for specific information
  - **Function Calling**: Invoke custom tools based on document content
  - **Computer Use**: Execute code and perform calculations
- `GET /api.assisted.space/v2/responses/<response_id>`: Retrieve the status or content of a document processing request

### Image Generation Endpoints

- `POST /api.assisted.space/v2/images/generate`: Generate images using OpenAI's DALL-E models
- `POST /api.assisted.space/v2/images/edit`: Edit existing images using OpenAI's DALL-E models
- `POST /api.assisted.space/v2/images/variations`: Create variations of existing images using OpenAI's DALL-E models

### Tools Endpoints

- `POST /api.assisted.space/v2/tools/call`: Call a tool/function with an AI provider
- `GET/POST /api.assisted.space/v2/tools/schemas`: Get available tool schemas
- `GET /api.assisted.space/v2/tools/capabilities`: Get tool capabilities for all providers

### Files Endpoints

- `POST /api.assisted.space/v2/files/upload`: Upload a file to the server
- `GET /api.assisted.space/v2/files/download/<file_id>`: Download a file
- `DELETE /api.assisted.space/v2/files/delete/<file_id>`: Delete a file
- `GET /api.assisted.space/v2/files/list`: List uploaded files

### Web Search Endpoints

- `GET/POST /api.assisted.space/v2/web/duckduckgo`: Search the web using DuckDuckGo
- `GET/POST /api.assisted.space/v2/web/searxng`: Search using SearXNG with content scraping
- `GET/POST /api.assisted.space/v2/web/website`: Extract content from a specified website URL
- `GET/POST /api.assisted.space/v2/web/reader`: Extract clean, readable content via Reader API
- `GET/POST /api.assisted.space/v2/web/search/<engine>`: Search using various engines (google, bing, baidu)

### Academic Research Endpoints

- `GET/POST /api.assisted.space/v2/research/semantic-scholar`: Search academic papers using Semantic Scholar
- `GET/POST /api.assisted.space/v2/research/arxiv`: Search preprints on arXiv
- `GET/POST /api.assisted.space/v2/research/pubmed`: Search medical literature on PubMed
- `GET/POST /api.assisted.space/v2/research/google-scholar`: Search academic papers via Google Scholar

### Dreamwalker Endpoints (Coming Soon)

- `POST /api.assisted.space/v2/dreamwalker/swarm`: Execute query expansion and parallel search
- `POST /api.assisted.space/v2/dreamwalker/research`: Analyze academic literature with citation tracing
- `POST /api.assisted.space/v2/dreamwalker/compare`: Compare responses across multiple providers
- `POST /api.assisted.space/v2/dreamwalker/factcheck`: Verify claims across multiple sources

## Authentication

All API requests require authentication with an API key. You can pass the API key in one of the following ways:

1. Using the `X-API-Key` header (recommended): 
   ```
   X-API-Key: your_api_key
   ```

2. As a query parameter:
   ```
   ?api_key=your_api_key
   ```

3. In the request body (JSON or form data):
   ```json
   {
     "api_key": "your_api_key",
     "provider": "anthropic",
     ...
   }
   ```

## Getting Started

### Prerequisites

- Python 3.8+
- Flask
- Provider-specific Python clients (anthropic, openai, etc.)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables for API keys:
   ```
   export ANTHROPIC_API_KEY=your_anthropic_key
   export OPENAI_API_KEY=your_openai_key
   export MISTRAL_API_KEY=your_mistral_key
   export COHERE_API_KEY=your_cohere_key
   export XAI_API_KEY=your_xai_key
   export COZE_API_KEY=your_coze_key
   ```
4. Run the API server:
   ```
   python -m api.app
   ```

## Examples

### Streaming Chat Completion

```python
import requests
import json

response = requests.post(
    "https://api.assisted.space/v2/chat/stream",
    headers={"X-API-Key": "your_api_key"},
    json={
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "prompt": "Tell me a short story about a robot learning to paint."
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if "content" in data:
            print(data["content"], end="", flush=True)
```

### Streaming with X.AI (Grok)

```python
import requests
import json

response = requests.post(
    "https://api.assisted.space/v2/chat/xai",
    headers={"X-API-Key": "your_api_key"},
    json={
        "model": "grok-2-1212",
        "prompt": "Explain how quantum computing works",
        "stream": True
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if "content" in data:
            print(data["content"], end="", flush=True)
```

### Alt Text Generation

```python
import requests

with open("image.jpg", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/alt/generate",
        headers={"X-API-Key": "your_api_key"},
        files={"image": f},
        data={
            "provider": "openai",
            "model": "gpt-4o",
            "prompt": "Generate descriptive alt text for the visually impaired for social media",
            "stream": "false"
        }
    )

result = response.json()
print(f"Alt Text: {result['alt_text']}")
```

### Alt Text Generation with Coze

```python
import requests

with open("image.jpg", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/alt/coze",
        headers={"X-API-Key": "your_api_key"},
        files={"image": f},
        data={
            "model": "7462296933429346310",  # Alt Text Generator Bot ID
            "prompt": "Generate detailed alt text for accessibility purposes",
            "stream": "false"
        }
    )

result = response.json()
print(f"Alt Text: {result['alt_text']}")
```

### Tool Calling Example

```python
import requests
import json

response = requests.post(
    "https://api.assisted.space/v2/tools/call",
    headers={"X-API-Key": "your_api_key"},
    json={
        "provider": "mistral",
        "model": "mistral-small",
        "prompt": "What's the weather in San Francisco today?",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"]
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    }
)

result = response.json()
print(json.dumps(result, indent=2))
```

### Website Scraping Example

```python
import requests

# Extract content from a website
response = requests.get(
    "https://api.assisted.space/v2/web/website",
    headers={"X-API-Key": "your_api_key"},
    params={
        "url": "https://example.com",
        "max_words": 2000
    }
)

result = response.json()
print(f"Title: {result['result']['title']}")
print(f"Excerpt: {result['result']['excerpt']}")
print(f"Content length: {len(result['result']['content'])} characters")
```

### SearXNG Search with Content Scraping

```python
import requests
import json

response = requests.post(
    "https://api.assisted.space/v2/web/searxng",
    headers={"X-API-Key": "your_api_key"},
    json={
        "query": "climate change solutions",
        "max_results": 3,
        "ignored_websites": "wikipedia.org,youtube.com"
    }
)

results = response.json()
print(f"Found {results['count']} results for query: {results['query']}")

for i, result in enumerate(results['results'], 1):
    print(f"\n{i}. {result['title']}")
    print(f"   URL: {result['url']}")
    print(f"   Snippet: {result['snippet']}")
    print(f"   Content length: {len(result['content'])} characters")
```

### Document Processing with Advanced Capabilities

```python
import requests
import json

# Weather tool definition for function calling
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

with open("financial_report.pdf", "rb") as f:
    response = requests.post(
        "https://api.assisted.space/v2/responses",
        headers={"X-API-Key": "your_api_key"},
        files={"file": f},
        data={
            "model": "gpt-4o-2024-11-20",
            "prompt": "Analyze this financial report, compare with current market data, and calculate key metrics.",
            "web_search": "true",    # Enable real-time web search
            "file_search": "true",   # Enable document search
            "computer_use": "true",  # Enable code execution
            "tools": json.dumps(weather_tool)  # Add custom tool definition
        }
    )

result = response.json()

# Check if we have an immediate response or need to retrieve it later
if result.get("status") == "completed":
    print(f"Analysis: {result['content']}")
else:
    # For long-running processes, we may need to retrieve the result later
    response_id = result.get("response_id")
    print(f"Processing started. Response ID: {response_id}")
    print(f"Check status later with: GET /responses/{response_id}")
```

### Image Generation

```python
import requests
import json

# Generate an image
response = requests.post(
    "https://api.assisted.space/v2/images/generate",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key"
    },
    json={
        "prompt": "A surreal painting of a floating island with waterfalls",
        "model": "dall-e-3",
        "size": "1024x1024",
        "n": 1,
        "quality": "standard",
        "style": "vivid"
    }
)

result = response.json()
image_url = result["data"][0]["url"]
print(f"Generated image URL: {image_url}")

# Edit an image
with open("image.png", "rb") as img_file, open("mask.png", "rb") as mask_file:
    files = {
        "image": img_file,
        "mask": mask_file
    }
    data = {
        "prompt": "Add a cute cat sitting in the foreground",
        "model": "dall-e-2",
        "size": "1024x1024",
        "n": 1
    }
    response = requests.post(
        "https://api.assisted.space/v2/images/edit",
        headers={"X-API-Key": "your_api_key"},
        files=files,
        data=data
    )
    
    result = response.json()
    edited_image_url = result["data"][0]["url"]
    print(f"Edited image URL: {edited_image_url}")
```

## Accessibility Considerations

This API was built with accessibility in mind:

- Alt text generation endpoint specifically designed for creating descriptive image captions
- Consistent error responses that are easy to parse
- Detailed documentation for all endpoints
- Streaming capabilities to provide real-time feedback
- Appropriate content types and headers for response handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or inquiries, please contact [api@assisted.space](mailto:api@assisted.space). 