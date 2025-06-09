# Camina Chat API Documentation

## Overview

Camina Chat API provides a unified interface to interact with multiple AI providers, including Anthropic Claude, Mistral AI, Ollama, OpenAI, Cohere, X.AI (Grok), and Coze. The API supports text chat, multimodal interactions (vision), alt text generation, and tool calling capabilities, and advanced multi-step AI workflows through the Dreamwalker framework.

## Base URL

```
http://localhost:8435/v2
```

## Authentication

API keys for each provider are configured in the server's environment variables or in the `config.py` file. No client-side authentication is required for local development.

## Available Providers

- **anthropic**: Anthropic Claude models (Claude 3 Opus, Sonnet, Haiku)
- **mistral**: Mistral AI models (Mistral Tiny, Small, Medium, Large, and Pixtral)
- **ollama**: Local models running through Ollama (Llama, Mistral, custom models)
- **openai**: OpenAI hosted models (GPT-4, GPT-3.5, GPT-4 Vision)
- **cohere**: Cohere Command models (Command, Command Light, Command R+)
- **xai**: X.AI (Grok) models (Grok 2, Grok Vision)
- **coze**: Coze platform bots (Alt Text Generator, TTS Generator)
- **perplexity**: Perplexity API models (Sonar, Sonar Pro, Sonar Reasoning)
- **mlx**: Local models for Apple Silicon (Mistral, Qwen, Nemo, DeepSeek)

### Coming Soon

- **lmstudio**: LM Studio-hosted models (Vision models, embeddings)

### Provider-Specific Information

#### Ollama Provider

The Ollama provider enables access to locally-run, open-source models through the [Ollama](https://ollama.ai/) project. This allows for:

- **Local Inference**: Models run on your local hardware, with no data leaving your system
- **Custom Models**: Support for custom models you've imported into Ollama
- **Vision Capabilities**: Vision analysis through LLaVA and other multimodal models
- **No API Key Required**: Uses your local Ollama installation

Ollama must be installed and running locally for this provider to work. The API connects to Ollama through its HTTP API at `http://localhost:11434` by default.

#### OpenAI Provider

The OpenAI provider enables access to OpenAI's state-of-the-art hosted GPT models. This allows for:

- **Hosted Inference**: Models run on OpenAI's infrastructure, with requests processed through their API
- **Vision Capabilities**: Image analysis through GPT-4o and GPT-4 Vision models (note: all modern OpenAI models like GPT-4o have vision capabilities built-in)
- **Tool Calling**: Native function calling capabilities (previously known as "plugins")
- **Long Context**: Support for long contexts up to 128k tokens with some models

An OpenAI API key is required to use this provider. The API key should be set in the `OPENAI_API_KEY` environment variable.

#### Cohere Provider

The Cohere provider enables access to Cohere's Command models through their API. This allows for:

- **Hosted Inference**: Models run on Cohere's infrastructure, with requests processed through their API
- **Chat Capabilities**: Support for conversational chat functionality
- **Tool Calling**: Support for function calling via tool definition
- **No Vision Support**: Cohere models currently do not support image analysis or vision features

A Cohere API key is required to use this provider. The API key should be set in the `COHERE_API_KEY` environment variable or configured in the application.

#### X.AI Provider

The X.AI provider enables access to X.AI's Grok models through their API. This allows for:

- **Hosted Inference**: Models run on X.AI's infrastructure, with requests processed through their API
- **Vision Capabilities**: Image analysis through Grok Vision models (grok-2-vision-1212, grok-2-vision-1212)
- **Tool Calling**: Support for function calling through the OpenAI-compatible interface
- **Conversational History**: Maintained context across multiple exchanges

An X.AI API key is required to use this provider, which can be set in the `XAI_API_KEY` environment variable. The API uses the OpenAI SDK with a custom base URL to communicate with X.AI's API.

#### Coze Provider

The Coze provider enables access to specialized bots created on the Coze platform. This allows for:

- **Hosted Inference**: Bots run on Coze's infrastructure, with requests processed through their API
- **Specialized Bots**: Access to purpose-built bots like the Alt Text Generator and TTS Generator
- **Vision Capabilities**: Image analysis through the Alt Text Generator bot (ID: 7462296933429346310)
- **Tool Calling**: Support for function calling through specialized bots
- **File Handling**: Support for file uploads and processing

A Coze API key is required to use this provider, which can be set in the `COZE_API_KEY` environment variable. The API uses a custom implementation to communicate with Coze's API, including handling file uploads for image processing.

#### Perplexity Provider

The Perplexity provider enables access to Perplexity's advanced search-augmented models. This allows for:

- **Web Search Integration**: Models can search the web in real-time to provide up-to-date information
- **Research Capabilities**: Specialized models for in-depth research with large context windows
- **Reasoning**: Advanced reasoning capabilities with Chain-of-Thought processing
- **API Key Required**: Requires a valid Perplexity API key

#### MLX Provider

The MLX provider enables access to locally-run models optimized for Apple Silicon devices through the [MLX framework](https://github.com/ml-explore/mlx). This allows for:

- **Local Inference**: Models run directly on your Apple Silicon hardware, with no data leaving your system
- **Apple Silicon Optimization**: Models are optimized for Apple's Neural Engine and GPU, providing efficient inference
- **No API Key Required**: Uses the MLX command-line tools installed on your system
- **Offline Operation**: All processing happens locally without internet connectivity requirements

The MLX provider requires:
1. An Apple Silicon Mac (M1, M2, or M3 series)
2. MLX framework and MLX LM command-line tools installed
3. Sufficient storage space for model weights

Available models include:
- Qwen2 7B (optimized for Apple Silicon)
- Mistral 7B (optimized for instruction following)
- Mistral Nemo 7B (optimized for instruction following)
- DeepSeek R1 7B (optimized for reasoning)
- Mistral Small 24B (optimized for instruction following)
- DeepSeek R1 32B (optimized for reasoning)

**Note**: MLX models currently do not support vision capabilities. The provider will be updated as new capabilities become available in the MLX framework.

## Endpoints

### API Information

Get information about the API, including available providers and endpoints.

**Endpoint:** `GET /`

**Response:**
```json
{
  "status": "ok",
  "version": "v2",
  "providers": {
    "anthropic": true,
    "openai": true,
    "ollama": true,
    "perplexity": true,
    "mistral": true,
    "cohere": true,
    "xai": true,
    "coze": true,
    "mlx": true,
    "lmstudio": false
  },
  "endpoints": [
    "https://api.assisted.space/v2/chat/{provider}",
    "https://api.assisted.space/v2/alt/{provider}",
    "https://api.assisted.space/v2/tools/{provider}",
    "https://api.assisted.space/v2/models/{provider}",
    "https://api.assisted.space/v2/dreamwalker/{workflow}"
  ]
}
```

### Health Check

Check the health status of the API.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "timestamp": 1708838400,
  "providers": {
    "anthropic": true,
    "openai": true,
    "ollama": true,
    "perplexity": true,
    "mistral": true,
    "cohere": true,
    "xai": true,
    "coze": true,
    "mlx": true,
    "lmstudio": false
  }
}
```

### List Models

Get a list of available models from a specific provider.

**Endpoint:** `GET /models/{provider}`

**Query Parameters:**
- `sort_by` (optional): Field to sort by (`created`, `id`, `capabilities`). Default: `created`
- `capability` (optional): Filter models by capability (`vision`, `text`, `function`, etc.)
- `generation` (optional): Filter OpenAI models by generation
- `category` (optional): Filter Mistral models by category (`mistral`, `mixtral`, `pixtral`)
- `tags` (optional): Filter Ollama models by tags (`llama`, `mistral`, `vision`, etc.)

**Provider-Specific Behavior:**
- **Mistral**: Automatically filters out duplicate model IDs to ensure each model is only returned once
- **Ollama**: Returns all locally available models from your Ollama installation
- **Cohere**: Returns available Command models (command-r-plus, command-light, etc.)
- **X.AI**: Returns available Grok models with their capabilities (text, function, vision)
- **Coze**: Returns available specialized bots with their IDs and capabilities

**Example:** `GET /models/anthropic`

**Response:**
```json
[
  {
    "id": "claude-3-opus-20240229",
    "name": "Claude 3 Opus",
    "description": "Claude 3 Opus",
    "capabilities": ["text", "vision", "code", "analysis"],
    "capability_count": 4,
    "created": "2024-02-29",
    "created_at": "February 29, 2024",
    "owned_by": "anthropic",
    "provider": "anthropic"
  },
  {
    "id": "claude-3-sonnet-20240229",
    "name": "Claude 3 Sonnet",
    "description": "Claude 3 Sonnet",
    "capabilities": ["text", "vision", "code"],
    "capability_count": 3,
    "created": "2024-02-29",
    "created_at": "February 29, 2024",
    "owned_by": "anthropic",
    "provider": "anthropic"
  }
]
```

**Example:** `GET /models/cohere`

**Response:**
```json
[
  {
    "id": "command-r-plus-08-2024",
    "name": "Command R+ (August 2024)",
    "description": "Cohere's most capable model for complex tasks",
    "capabilities": ["text", "function"],
    "capability_count": 2,
    "created": "2024-08-01",
    "created_at": "August 1, 2024",
    "owned_by": "cohere",
    "provider": "cohere"
  },
  {
    "id": "command-light",
    "name": "Command Light",
    "description": "Lightweight model for faster processing",
    "capabilities": ["text"],
    "capability_count": 1,
    "created": "2023-11-01",
    "created_at": "November 1, 2023",
    "owned_by": "cohere",
    "provider": "cohere"
  }
]
```

**Example:** `GET /models/coze`

**Response:**
```json
[
  {
    "id": "7462296933429346310",
    "name": "Alt Text Generator Bot",
    "description": "Specialized bot for generating descriptive alt text from images",
    "capabilities": ["text", "vision"],
    "capability_count": 2,
    "created": "2024-08-01",
    "created_at": "August 1, 2024",
    "owned_by": "coze",
    "provider": "coze"
  },
  {
    "id": "7463319430379470854",
    "name": "TTS Generator Bot",
    "description": "Specialized bot for text-to-speech generation",
    "capabilities": ["text", "audio"],
    "capability_count": 2,
    "created": "2024-08-01",
    "created_at": "August 1, 2024",
    "owned_by": "coze",
    "provider": "coze"
  }
]
```

### Chat

Send a message to a model and get a response.

**Endpoint:** `POST /chat/{provider}`

**Request Body:**
```json
{
  "model": "claude-3-haiku-20240307",
  "prompt": "Hello, how are you today?",
  "max_tokens": 16192,
  "stream": true,
  "image_path": null,
  "image_data": null,
  "use_test_image": false
}
```

**Parameters:**
- `model` (required): The model ID to use
- `prompt` (required): The user's message
- `max_tokens` (optional): Maximum number of tokens to generate. Default: 16192
- `stream` (optional): Whether to stream the response. Default: true
- `image_path` (optional): Path to an image file (server-side)
- `image_data` (optional): Base64-encoded image data
- `use_test_image` (optional): Whether to use a test image. Default: false

**Ollama-Specific Parameters:**
- `temperature` (optional): Controls randomness (0.0-1.0). Default: 0.7
- `top_p` (optional): Nucleus sampling parameter (0.0-1.0). Default: 0.9
- `top_k` (optional): Number of tokens to sample from. Default: 40
- `repeat_penalty` (optional): Penalty for repeating tokens (1.0-2.0). Default: 1.1
- `seed` (optional): Random seed for deterministic output (integer)

**OpenAI-Specific Parameters:**
- `temperature` (optional): Controls randomness (0.0-1.0). Default: 0.7
- `top_p` (optional): Nucleus sampling parameter (0.0-1.0). Default: 1.0
- `presence_penalty` (optional): Penalty for repetition (0.0-2.0). Default: 0.0
- `frequency_penalty` (optional): Penalty for token frequency (0.0-2.0). Default: 0.0

**Cohere-Specific Parameters:**
- `temperature` (optional): Controls randomness (0.0-1.0). Default: 0.7
- `p` (optional): Nucleus sampling parameter (0.0-1.0). Default: 0.7
- `k` (optional): Number of tokens to sample from. Default: 0 (disabled)
- `frequency_penalty` (optional): Penalty for token frequency (0.0-1.0). Default: 0.0

**X.AI-Specific Parameters:**
- `temperature` (optional): Controls randomness (0.0-1.0). Default: 0.7
- `image_data` (optional): When set to null, explicitly prevents image data from being included in the request

**Coze-Specific Parameters:**
- `file_id` (optional): ID of a previously uploaded file for image analysis
- `temperature` (optional): Controls randomness (0.0-1.0). Default: 0.7

**Response (non-streaming):**
```json
{
  "content": "I'm doing well, thank you for asking! I'm Claude, an AI assistant created by Anthropic. I'm here to help with a wide range of tasks through conversation. How can I assist you today?",
  "model": "claude-3-haiku-20240307",
  "provider": "anthropic"
}
```

**Response (streaming):**
The response is streamed as a series of text chunks or JSON objects, depending on the provider.

### Alt Text Generation

Generate descriptive alt text for an image.

**Endpoint:** `POST /alt/{provider}`

**Form Data:**
- `image` (required): The image file to generate alt text for
- `prompt` (optional): Custom prompt for alt text generation. Default: "Generate descriptive alt text for this image"
- `model` (required): The model ID to use
- `stream` (optional): Whether to stream the response. Default: false

**Response:**
```json
{
  "alt_text": "A simple test image with a red square on the left side and a blue circle on the right side. Below these shapes is the text 'Test Image' in black.",
  "model": "claude-3-haiku-20240307",
  "provider": "anthropic"
}
```

**Provider Compatibility:**
- **Anthropic**: All Claude 3 models support vision
- **OpenAI**: GPT-4o and GPT-4 Vision models support vision
- **Mistral**: Pixtral models support vision
- **Ollama**: Vision-capable models like LLaVA support vision
- **X.AI**: Vision-capable models like grok-2-vision-1212 support vision
- **Cohere**: Currently does not support vision or alt text generation
- **Coze**: The Alt Text Generator bot (ID: 7462296933429346310) supports vision

**Ollama Vision Support:**

For the Ollama provider, any model can be used with image data. Vision-capable models like LLaVA will properly analyze the image content, while text-only models may ignore the image but will still generate a response. The API will respect the model choice made by the user and will not automatically switch to a vision-capable model.

**X.AI Vision Support:**

For the X.AI provider, vision-capable models like `grok-2-vision-1212` should be used for image analysis. When using the X.AI provider for alt text generation, the image data should be sent as a base64-encoded string in the JSON payload instead of using form data:

```json
{
  "model": "grok-2-vision-1212",
  "prompt": "Describe what's in this image in detail",
  "image_data": "BASE64_ENCODED_IMAGE_DATA"
}
```

**Coze Vision Support:**

For the Coze provider, the Alt Text Generator bot (ID: 7462296933429346310) should be used for image analysis. When using the Coze provider for alt text generation, the image is first uploaded to Coze's servers to obtain a file ID, which is then used in the request:

```json
{
  "model": "7462296933429346310",
  "prompt": "Describe what's in this image in detail",
  "file_id": "FILE_ID_FROM_UPLOAD"
}
```

The API handles this two-step process automatically when using the `/alt/coze` endpoint with form data.

### Tool Calling

Use AI models to call tools based on a prompt.

**Endpoint:** `POST /tools/{provider}`

**Request Body:**
```json
{
  "model": "claude-3-opus-20240229",
  "prompt": "What is the weather in Seattle?",
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
              "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "The unit of temperature to use"
            }
          },
          "required": ["location"]
        }
      }
    }
  ],
  "max_tokens": 200
}
```

**Parameters:**
- `model` (required): The model ID to use
- `prompt` (required): The user's message
- `tools` (required): List of tool definitions
- `max_tokens` (optional): Maximum number of tokens to generate. Default: 16192

**Provider-Specific Behavior:**
- **Anthropic, Mistral**: Native tool calling support
- **Ollama**: Tool calling is implemented by formatting tool definitions in the prompt
- **OpenAI**: Native tool calling support via the function calling API
- **Cohere**: Limited tool calling support via prompt formatting
- **X.AI**: Function calling support compatible with the OpenAI interface
- **Coze**: Tool calling support through specialized bots

**Response:**
```json
{
  "content": "I need to check the weather in Seattle for you.",
  "tool_calls": [
    {
      "id": "call_123456789",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\":\"Seattle, WA\",\"unit\":\"fahrenheit\"}"
      }
    }
  ],
  "model": "claude-3-opus-20240229",
  "provider": "anthropic"
}
```

### Archive Retrieval

Retrieve archived versions of web pages from various archive services.

**Endpoint:** `GET /tools/archive` or `POST /tools/archive`

**Query Parameters (GET) or JSON Body (POST):**
- `url` (required): The URL to find an archived version for
- `provider` (optional): The archive provider to use (`wayback`, `archiveis`, `memento`). Default: `wayback`
- `capture` (optional): Whether to capture a new snapshot (for `archiveis` only). Default: `false`

**Example (GET):** `GET /tools/archive?url=https://example.com&provider=wayback`

**Example (POST):**
```json
{
  "url": "https://example.com",
  "provider": "archiveis",
  "capture": true
}
```

**Response:**
```json
{
  "original_url": "https://example.com",
  "provider": "wayback",
  "timestamp": "2023-08-15T12:34:56.789Z",
  "success": true,
  "archived_url": "https://web.archive.org/web/20230815123456/https://example.com",
  "message": "Successfully retrieved the most recent snapshot from the Wayback Machine"
}
```

**Direct Tool Execution Endpoint:** `POST /tools/execute/get_archived_webpage`

This endpoint allows direct execution of the archive tool without going through a provider's tool calling mechanism.

**Request Body:**
```json
{
  "url": "https://example.com",
  "provider": "memento"
}
```

**Tool Schema Endpoint:** `GET /tools/archive/schema`

Returns the JSON schema for the archive tool, which can be used with the tool calling API.

**Supported Archive Providers:**
- **wayback**: Internet Archive's Wayback Machine
- **archiveis**: Archive.is service (supports capturing new snapshots)
- **memento**: Memento Aggregator (searches across multiple archive services)

### Clear Conversation

Clear the conversation history for a provider.

**Endpoint:** `POST /chat/{provider}/clear`

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation cleared"
}
```

### Dreamwalker Framework

Execute complex, multi-step AI workflows with the Dreamwalker framework.

#### Start a Search Workflow

Start a new search workflow that expands a query into multiple related searches and generates a comprehensive summary.

**Endpoint:** `POST /dreamwalker/search`

**Request Body:**
```json
{
  "query": "Impact of climate change on agriculture",
  "workflow_type": "swarm",
  "model": "coolhand/camina-search:24b"
}
```

**Parameters:**
- `query` (required): The query to process
- `workflow_type` (optional): Type of workflow to execute. Default: "swarm"
- `model` (optional): Model to use for the workflow. Default: "coolhand/camina-search:24b"

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "initialized",
  "progress": 0,
  "step_description": null
}
```

#### Get Workflow Status

Check the status of a running workflow.

**Endpoint:** `GET /dreamwalker/status/{workflow_id}`

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_type": "SwarmDreamwalker",
  "status": "running",
  "progress": 45,
  "start_time": 1708838400.123,
  "end_time": null,
  "duration": 120.5,
  "steps_completed": [
    {
      "description": "Generating variant search queries",
      "timestamp": 1708838410.123
    },
    {
      "description": "Executing searches for variant queries",
      "timestamp": 1708838430.123
    }
  ],
  "steps_remaining": [],
  "error": null,
  "results": {},
  "metadata": {
    "model": "coolhand/camina-search:24b",
    "api_base_url": "https://api.assisted.space/v2",
    "tools_available": true
  }
}
```

#### Get Workflow Result

Get the result of a completed workflow.

**Endpoint:** `GET /dreamwalker/result/{workflow_id}`

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "Impact of climate change on agriculture",
  "variant_queries": [
    "Impact of rising temperatures on crop yields",
    "Climate change effects on global food security",
    "Adaptation strategies for agriculture under climate change",
    "Regional differences in agricultural climate change impacts",
    "Future projections of climate change on farming practices"
  ],
  "search_results_count": 5,
  "urls_extracted": 23,
  "summary": "# Impact of Climate Change on Agriculture\n\n## Introduction\n\nClimate change poses significant challenges to agriculture worldwide...",
  "conversation_history": [
    {
      "role": "user",
      "content": "Impact of climate change on agriculture"
    },
    {
      "role": "assistant",
      "content": "# Impact of Climate Change on Agriculture\n\n## Introduction\n\nClimate change poses significant challenges to agriculture worldwide..."
    }
  ]
}
```

#### Cancel a Workflow

Cancel a running workflow.

**Endpoint:** `DELETE /dreamwalker/cancel/{workflow_id}`

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow_type": "SwarmDreamwalker",
  "status": "cancelled",
  "progress": 45,
  "start_time": 1708838400.123,
  "end_time": 1708838520.123,
  "duration": 120.0,
  "steps_completed": [
    {
      "description": "Generating variant search queries",
      "timestamp": 1708838410.123
    },
    {
      "description": "Executing searches for variant queries",
      "timestamp": 1708838430.123
    }
  ],
  "steps_remaining": [],
  "error": null,
  "results": {},
  "metadata": {
    "model": "coolhand/camina-search:24b",
    "api_base_url": "https://api.assisted.space/v2",
    "tools_available": true
  }
}
```

#### List Workflows

List active workflows.

**Endpoint:** `GET /dreamwalker/list`

**Query Parameters:**
- `status` (optional): Filter workflows by status (`initialized`, `running`, `completed`, `failed`, `cancelled`)
- `limit` (optional): Maximum number of workflows to return. Default: 10

**Response:**
```json
[
  {
    "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
    "workflow_type": "SwarmDreamwalker",
    "status": "completed",
    "progress": 100,
    "start_time": 1708838400.123,
    "end_time": 1708838520.123,
    "duration": 120.0,
    "steps_completed": [
      {
        "description": "Generating variant search queries",
        "timestamp": 1708838410.123
      },
      {
        "description": "Executing searches for variant queries",
        "timestamp": 1708838430.123
      },
      {
        "description": "Generating comprehensive summary",
        "timestamp": 1708838500.123
      }
    ],
    "steps_remaining": [],
    "error": null,
    "results": {
      "query": "Impact of climate change on agriculture",
      "variant_queries": ["..."],
      "search_results_count": 5,
      "urls_extracted": 23,
      "summary": "..."
    },
    "metadata": {
      "model": "coolhand/camina-search:24b",
      "api_base_url": "https://api.assisted.space/v2",
      "tools_available": true
    }
  },
  {
    "workflow_id": "550e8400-e29b-41d4-a716-446655440001",
    "workflow_type": "SwarmDreamwalker",
    "status": "running",
    "progress": 45,
    "start_time": 1708838600.123,
    "end_time": null,
    "duration": 60.0,
    "steps_completed": [
      {
        "description": "Generating variant search queries",
        "timestamp": 1708838610.123
      }
    ],
    "steps_remaining": [],
    "error": null,
    "results": {},
    "metadata": {
      "model": "coolhand/camina-search:24b",
      "api_base_url": "https://api.assisted.space/v2",
      "tools_available": true
    }
  }
]
```

#### Clean Up Workflows

Clean up old workflows.

**Endpoint:** `DELETE /dreamwalker/cleanup`

**Query Parameters:**
- `status` (optional): Status of workflows to clean up. Default: "completed"
- `age_hours` (optional): Age in hours of workflows to clean up. Default: 24

**Response:**
```json
{
  "status": "success",
  "removed_count": 5,
  "remaining_count": 3
}
```

### Dreamwalker Workflows

The Dreamwalker framework provides advanced multi-step AI workflows for complex tasks. These workflows combine multiple steps, tools, and providers to deliver comprehensive results for complex tasks.

**Base Endpoint:** `/dreamwalker`

#### Start a Swarm Search Workflow

Start a new Swarm search workflow, which expands the query into multiple related searches, executes them in parallel, and aggregates the results.

**Endpoint:** `POST /dreamwalker/search`

**Request Body:**
```json
{
  "query": "Latest developments in quantum computing",
  "workflow_type": "swarm",
  "model": "coolhand/camina-search:24b"
}
```

**Response:**
```json
{
  "workflow_id": "1234567890abcdef",
  "status": "started",
  "message": "Workflow started successfully",
  "estimated_time": "30-60 seconds"
}
```

### Web Search

The Web Search endpoints provide access to various web search engines and APIs, allowing you to retrieve up-to-date information from the internet.

**Base Endpoint:** `/web`

#### DuckDuckGo Search

Search the web using the DuckDuckGo search engine.

**Endpoint:** `GET /web/duckduckgo`

**Query Parameters:**
- `query` (required): The search term to look up
- `region` (optional): Region for the search (default: "wt-wt")
- `safesearch` (optional): SafeSearch setting ("on", "moderate", "off") (default: "moderate")
- `timelimit` (optional): Time limit for results ("d", "w", "m", "y" for day, week, month, year)
- `max_results` (optional): Maximum number of results to return (default: 10)

**Example:** `GET /web/duckduckgo?query=python%20flask%20api&max_results=3`

**Response:**
```json
{
  "count": 3,
  "query": "python flask api",
  "results": [
    {
      "title": "Flask REST API Tutorial - Python Tutorial",
      "href": "https://pythonbasics.org/flask-rest-api/",
      "body": "In this Flask REST API tutorial, we'll show you exactly how to build an API with Flask. Creating an API with Flask can be done in many ways, in this example we'll create a simple Python API using Flask and test it."
    },
    {
      "title": "Python | Build a REST API using Flask - GeeksforGeeks",
      "href": "https://www.geeksforgeeks.org/python-build-a-rest-api-using-flask/",
      "body": "In this article, we will see how to create a REST API using Python and Flask. Flask is a micro web framework written in Python. It is classified as a microframework because it does not require particular tools or libraries."
    },
    {
      "title": "Building a RESTful API with Flask: A Step-by-Step Guide - Medium",
      "href": "https://medium.com/@aspen.wilson/building-a-restful-api-with-flask-a-step-by-step-guide-3bfb092f98a1",
      "body": "Flask is a lightweight web framework for Python that makes it easy to build web applications, including RESTful APIs. In this article, we'll walk through the process of creating a simple RESTful API using Flask."
    }
  ]
}
```

**Endpoint:** `POST /web/duckduckgo`

**Request Body:**
```json
{
  "query": "accessibility web design",
  "max_results": 2,
  "region": "us-en",
  "safesearch": "moderate"
}
```

**Response:**
```json
{
  "count": 2,
  "query": "accessibility web design",
  "results": [
    {
      "title": "Designing for Web Accessibility - Tips for Getting Started",
      "href": "https://www.w3.org/WAI/tips/designing/",
      "body": "These tips introduce some basic considerations to help you get started with accessible web design. They are grouped into sections related to page structure, navigation, colors, text and images, and forms."
    },
    {
      "title": "Guide to Accessible Web Design & Development | Section508.gov",
      "href": "https://www.section508.gov/content/guide-accessible-web-design-development/",
      "body": "The Web Content Accessibility Guidelines (WCAG) 2.0 Level AA requirements apply to websites, web applications, and digital content. The WCAG requirements cover a wide range of recommendations for making web content more accessible for all users."
    }
  ]
}
```

#### SearXNG Search

Search the web using SearXNG meta search engine and scrape the first N pages of results.

**Endpoint:** `GET /web/searxng`

**Query Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 3)
- `api_url` (optional): SearXNG API URL (default: "https://paulgo.io/search")
- `ignored_websites` (optional): Comma-separated list of websites to ignore
- `max_words_per_page` (optional): Maximum number of words to include per page (default: 5000)

**Example:** `GET /web/searxng?query=machine%20learning&max_results=2`

**Response:**
```json
{
  "count": 2,
  "query": "machine learning",
  "results": [
    {
      "title": "Machine Learning - Wikipedia",
      "url": "https://en.wikipedia.org/wiki/Machine_learning",
      "content": "Machine learning (ML) is a field of study in artificial intelligence concerned with the development and study of statistical algorithms that can learn from data and generalize to unseen data, and thus perform tasks without explicit instructions. Recently, generative artificial intelligence has also become a major focus of machine learning...",
      "snippet": "Machine learning (ML) is a field of study in artificial intelligence..."
    },
    {
      "title": "What is Machine Learning? A Definition - Expert.ai",
      "url": "https://www.expert.ai/blog/machine-learning-definition/",
      "content": "Machine learning is an application of artificial intelligence (AI) that enables systems to learn and improve from experience without being explicitly programmed. Machine learning focuses on developing computer programs that can access data and use it to learn for themselves...",
      "snippet": "Machine learning is an application of artificial intelligence..."
    }
  ]
}
```

**Endpoint:** `POST /web/searxng`

**Request Body:**
```json
{
  "query": "climate change research",
  "max_results": 2,
  "ignored_websites": "wikipedia.org,youtube.com",
  "max_words_per_page": 2000
}
```

**Response:**
```json
{
  "count": 2,
  "query": "climate change research",
  "results": [
    {
      "title": "Climate Change Research - NASA",
      "url": "https://climate.nasa.gov/",
      "content": "NASA's role in climate change research is centered around providing the global science community with observations of our planet that are critical to understanding Earth's changing climate...",
      "snippet": "NASA's role in climate change research..."
    },
    {
      "title": "Latest Climate Change Research - NOAA",
      "url": "https://www.noaa.gov/climate",
      "content": "NOAA conducts research to develop the knowledge, information, and tools needed to prepare for and respond to climate variability and change...",
      "snippet": "NOAA conducts research to develop the knowledge..."
    }
  ]
}
```

#### Website Scraper

Scrape content from a specified website URL.

**Endpoint:** `GET /web/website`

**Query Parameters:**
- `url` (required): The URL of the website to scrape
- `max_words` (optional): Maximum number of words to include (default: 5000)

**Example:** `GET /web/website?url=https%3A%2F%2Fexample.com`

**Response:**
```json
{
  "url": "https://example.com",
  "result": {
    "title": "Example Domain",
    "url": "https://example.com",
    "content": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission. More information...",
    "excerpt": "This domain is for use in illustrative examples in documents..."
  }
}
```

**Endpoint:** `POST /web/website`

**Request Body:**
```json
{
  "url": "https://example.com",
  "max_words": 1000
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "result": {
    "title": "Example Domain",
    "url": "https://example.com",
    "content": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission. More information...",
    "excerpt": "This domain is for use in illustrative examples in documents..."
  }
}
```

#### Reader API

Use the Reader API to extract content from a URL in readable format.

**Endpoint:** `GET /web/reader`

**Query Parameters:**
- `url` (required): The URL to read from

**Example:** `GET /web/reader?url=https%3A%2F%2Fnews.ycombinator.com`

**Response:**
```json
{
  "url": "https://news.ycombinator.com",
  "title": "Content from news.ycombinator.com",
  "content": "Hacker News new | past | comments | ask | show | jobs | submit... [Clean, readable content extracted from the page]..."
}
```

**Endpoint:** `POST /web/reader`

**Request Body:**
```json
{
  "url": "https://news.ycombinator.com"
}
```

**Response:**
```json
{
  "url": "https://news.ycombinator.com",
  "title": "Content from news.ycombinator.com",
  "content": "Hacker News new | past | comments | ask | show | jobs | submit... [Clean, readable content extracted from the page]..."
}
```

#### Search Engine APIs

Perform a search using various search engines through the Reader API.

**Endpoint:** `GET /web/search/<engine>`

**Path Parameter:**
- `engine`: Search engine to use ('google', 'bing', or 'baidu')

**Query Parameters:**
- `query` (required): The search term to look up

**Example:** `GET /web/search/google?query=artificial%20intelligence%20news`

**Response:**
```json
{
  "engine": "google",
  "query": "artificial intelligence news",
  "content": "[Extracted search results from Google in a readable format]..."
}
```

**Endpoint:** `POST /web/search/<engine>`

**Path Parameter:**
- `engine`: Search engine to use ('google', 'bing', or 'baidu')

**Request Body:**
```json
{
  "query": "artificial intelligence news"
}
```

**Response:**
```json
{
  "engine": "google",
  "query": "artificial intelligence news",
  "content": "[Extracted search results from Google in a readable format]..."
}
```

### Academic Research

The Academic Research endpoints provide access to various scholarly databases and academic search engines, allowing you to search for scientific papers, academic articles, and research publications.

**Base Endpoint:** `/research`

#### Semantic Scholar Search

Search academic papers using the Semantic Scholar API.

**Endpoint:** `GET /research/semantic-scholar`

**Query Parameters:**
- `query` (required): The search term to look up
- `limit` (optional): Maximum number of results to return (default: 10)
- `fields` (optional): Fields to include in response (comma-separated, default: "url,abstract,authors,title,venue,year,publicationTypes,tldr")
- `fieldsOfStudy` (optional): Filter by specific field(s)
- `year` (optional): Filter by publication year

**Example:** `GET /research/semantic-scholar?query=machine%20learning&limit=3&year=2023`

**Response:**
```json
{
  "query": "machine learning",
  "results": [
    {
      "paperId": "a1b2c3d4e5f6",
      "title": "Advances in Machine Learning: A 2023 Perspective",
      "abstract": "This paper provides an overview of recent advances in machine learning research and applications in 2023...",
      "authors": [
        {
          "authorId": "123456789",
          "name": "Jane Smith"
        },
        {
          "authorId": "987654321",
          "name": "John Doe"
        }
      ],
      "venue": "Journal of Machine Learning Research",
      "year": 2023,
      "url": "https://example.org/papers/advances-ml-2023"
    },
    {
      "paperId": "f6e5d4c3b2a1",
      "title": "Machine Learning for Climate Change Prediction",
      "abstract": "We present a novel approach using machine learning techniques to improve climate change predictions...",
      "authors": [
        {
          "authorId": "111222333",
          "name": "Alice Johnson"
        }
      ],
      "venue": "Nature Climate Change",
      "year": 2023,
      "url": "https://example.org/papers/ml-climate-change"
    }
  ],
  "count": 2,
  "total": 15783,
  "next_offset": 2,
  "offset": 0
}
```

**Endpoint:** `POST /research/semantic-scholar`

**Request Body:**
```json
{
  "query": "machine learning",
  "limit": 3,
  "fields": "url,abstract,authors,title,venue,year",
  "fieldsOfStudy": "Computer Science",
  "year": "2023"
}
```

#### arXiv Search

Search preprints on arXiv.

**Endpoint:** `GET /research/arxiv`

**Query Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 10)
- `sort_by` (optional): Sorting criteria (default: "relevance")
- `sort_order` (optional): Sorting order (default: "descending")
- `category` (optional): Filter by arXiv category (e.g., "cs.AI", "physics.optics")

**Example:** `GET /research/arxiv?query=quantum%20computing&max_results=2&category=quant-ph`

**Response:**
```json
{
  "query": "quantum computing",
  "results": [
    {
      "id": "2304.12345",
      "title": "Advances in Quantum Computing Algorithms",
      "summary": "This paper describes recent advances in quantum computing algorithms...",
      "authors": ["John Doe", "Jane Smith"],
      "published": "2023-04-15T12:00:00Z",
      "updated": "2023-04-20T12:00:00Z",
      "categories": ["quant-ph", "cs.ET"],
      "pdf_url": "https://arxiv.org/pdf/2304.12345.pdf"
    },
    {
      "id": "2305.67890",
      "title": "Quantum Error Correction: New Approaches",
      "summary": "We present new approaches to quantum error correction...",
      "authors": ["Alice Johnson", "Bob Williams"],
      "published": "2023-05-10T12:00:00Z",
      "updated": "2023-05-15T12:00:00Z",
      "categories": ["quant-ph"],
      "pdf_url": "https://arxiv.org/pdf/2305.67890.pdf"
    }
  ],
  "count": 2,
  "total_results": 5672
}
```

**Endpoint:** `POST /research/arxiv`

**Request Body:**
```json
{
  "query": "quantum computing",
  "max_results": 2,
  "category": "quant-ph",
  "sort_by": "relevance",
  "sort_order": "descending"
}
```

#### PubMed Search

Search medical literature on PubMed.

**Endpoint:** `GET /research/pubmed`

**Query Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 10)
- `sort` (optional): Sort by relevance or publication date (default: "relevance")
- `date_range` (optional): Filter by date range (e.g., "2020/01/01:2023/01/01")
- `journal` (optional): Filter by journal name

**Example:** `GET /research/pubmed?query=covid%20vaccination&max_results=2`

**Response:**
```json
{
  "query": "covid vaccination",
  "results": [
    {
      "id": "34567890",
      "title": "Efficacy of COVID-19 Vaccination in High-Risk Populations",
      "abstract": "This study examines the efficacy of COVID-19 vaccination in high-risk populations...",
      "authors": ["Robert Johnson", "Sarah Williams"],
      "journal": "The New England Journal of Medicine",
      "publication_date": "2022-06-15",
      "publication_types": ["Journal Article", "Research Support"],
      "pmid": "34567890",
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/34567890/"
    },
    {
      "id": "34567891",
      "title": "Long-term Effects of COVID-19 Vaccination",
      "abstract": "This longitudinal study investigates the long-term effects of COVID-19 vaccination...",
      "authors": ["Michael Brown", "Emily Davis"],
      "journal": "JAMA",
      "publication_date": "2022-08-20",
      "publication_types": ["Journal Article", "Clinical Trial"],
      "pmid": "34567891",
      "source": "PubMed",
      "url": "https://pubmed.ncbi.nlm.nih.gov/34567891/"
    }
  ],
  "count": 2,
  "total": 12345
}
```

**Endpoint:** `POST /research/pubmed`

**Request Body:**
```json
{
  "query": "covid vaccination",
  "max_results": 2,
  "sort": "relevance",
  "date_range": "2022/01/01:2023/01/01",
  "journal": "NEJM"
}
```

#### Google Scholar Search

Search academic papers on Google Scholar. Note: This endpoint uses Semantic Scholar as a proxy since Google Scholar doesn't provide an official API.

**Endpoint:** `GET /research/google-scholar`

**Query Parameters:**
- `query` (required): The search term to look up
- `max_results` (optional): Maximum number of results to return (default: 10)

**Example:** `GET /research/google-scholar?query=natural%20language%20processing&max_results=2`

**Response:**
```json
{
  "query": "natural language processing",
  "results": [
    {
      "title": "Attention Is All You Need",
      "abstract": "This paper introduces the Transformer, a novel neural network architecture based on self-attention...",
      "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
      "venue": "Advances in Neural Information Processing Systems",
      "year": 2017,
      "citations": 45000,
      "influential_citations": 8500,
      "url": "https://example.org/papers/transformer",
      "source": "Google Scholar (via Semantic Scholar)"
    },
    {
      "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
      "abstract": "We introduce a new language representation model called BERT...",
      "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
      "venue": "NAACL",
      "year": 2019,
      "citations": 30000,
      "influential_citations": 6000,
      "url": "https://example.org/papers/bert",
      "source": "Google Scholar (via Semantic Scholar)"
    }
  ],
  "count": 2,
  "note": "Google Scholar results are approximated via Semantic Scholar as Google Scholar has no official API."
}
```

**Endpoint:** `POST /research/google-scholar`

**Request Body:**
```json
{
  "query": "natural language processing",
  "max_results": 2
}
```

### Tool Calling

The Tool Calling section remains unchanged.

### Client Examples

The following examples demonstrate how to use the API with different programming languages.

### Python - Basic Chat Request
```python
import requests
import json

API_URL = "http://localhost:8435/v2"

def chat_with_model(provider="openai", model="gpt-3.5-turbo", prompt="Hello, how are you?", stream=False):
    endpoint = f"{API_URL}/chat/{provider}"
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 16192,
        "stream": stream
    }
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}: {response.text}"}

# Example usage
result = chat_with_model(provider="cohere", model="command-light", prompt="Explain quantum computing")
print(json.dumps(result, indent=2))
```

### JavaScript - Streaming Chat Example
```javascript
async function streamChat(provider = "openai", model = "gpt-3.5-turbo", prompt = "Tell me a story") {
  const API_URL = "http://localhost:8435/v2";
  const endpoint = `${API_URL}/chat/${provider}`;
  
  const payload = {
    model: model,
    prompt: prompt,
    max_tokens: 16192,
    stream: true
  };
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }
      
      // Convert the Uint8Array to a string and append to buffer
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete lines
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep the last incomplete line in the buffer
      
      for (const line of lines) {
        if (line.trim() === '') continue;
        
        try {
          const data = JSON.parse(line);
          
          // Handle the streamed content
          if (data.message && data.message.content) {
            console.log(data.message.content);
            // Append to UI or process as needed
          }
        } catch (e) {
          console.error('Error parsing JSON:', e);
        }
      }
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Example usage
streamChat("cohere", "command-light", "Write a short poem about technology");
```

### Python - Dreamwalker Example
```python
import requests
import time
import json

API_URL = "http://localhost:8435/v2"

def run_dreamwalker_search(query, model=None):
    """
    Run a Dreamwalker search workflow and wait for the results.
    
    Args:
        query: The query to search for
        model: Optional model to use
        
    Returns:
        The search results
    """
    # Start the workflow
    start_response = requests.post(
        f"{API_URL}/dreamwalker/search",
        json={
            "query": query,
            "workflow_type": "swarm",
            "model": model
        }
    )
    
    if start_response.status_code != 200:
        print(f"Error starting workflow: {start_response.text}")
        return None
    
    workflow_id = start_response.json()["workflow_id"]
    print(f"Started workflow: {workflow_id}")
    
    # Poll for status updates
    while True:
        status_response = requests.get(f"{API_URL}/dreamwalker/status/{workflow_id}")
        
        if status_response.status_code != 200:
            print(f"Error checking status: {status_response.text}")
            return None
        
        status = status_response.json()
        print(f"Progress: {status['progress']}% - {status.get('step_description', '')}")
        
        if status["status"] == "completed":
            break
        elif status["status"] == "failed":
            print(f"Workflow failed: {status.get('error', 'Unknown error')}")
            return None
        
        time.sleep(5)  # Wait 5 seconds before checking again
    
    # Get the results
    result_response = requests.get(f"{API_URL}/dreamwalker/result/{workflow_id}")
    
    if result_response.status_code != 200:
        print(f"Error getting results: {result_response.text}")
        return None
    
    return result_response.json()

# Example usage
results = run_dreamwalker_search("Latest developments in quantum computing")

if results:
    print(f"\nQuery: {results['query']}")
    print(f"Variant Queries: {', '.join(results['variant_queries'])}")
    print(f"Search Results Count: {results['search_results_count']}")
    print(f"URLs Extracted: {results['urls_extracted']}")
    print("\nSummary:")
    print(results["summary"])
```

### JavaScript - Dreamwalker Status Monitoring
```javascript
async function monitorDreamwalkerWorkflow(workflowId, onProgress, onComplete, onError) {
  const API_URL = "http://localhost:8435/v2";
  
  try {
    let isCompleted = false;
    
    while (!isCompleted) {
      const response = await fetch(`${API_URL}/dreamwalker/status/${workflowId}`);
      
      if (!response.ok) {
        throw new Error(`Error checking status: ${await response.text()}`);
      }
      
      const status = await response.json();
      
      // Call the progress callback
      if (onProgress) {
        onProgress(status);
      }
      
      if (status.status === "completed") {
        isCompleted = true;
        
        // Get the results
        const resultResponse = await fetch(`${API_URL}/dreamwalker/result/${workflowId}`);
        
        if (!resultResponse.ok) {
          throw new Error(`Error getting results: ${await resultResponse.text()}`);
        }
        
        const results = await resultResponse.json();
        
        // Call the complete callback
        if (onComplete) {
          onComplete(results);
        }
        
        return results;
      } else if (status.status === "failed") {
        throw new Error(`Workflow failed: ${status.error || "Unknown error"}`);
      }
      
      // Wait 2 seconds before checking again
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  } catch (error) {
    console.error("Error monitoring workflow:", error);
    if (onError) {
      onError(error);
    }
  }
}

// Example usage
monitorDreamwalkerWorkflow(
  "1234567890abcdef",
  (status) => console.log(`Progress: ${status.progress}% - ${status.step_description || ''}`),
  (results) => {
    console.log("\nFINAL SUMMARY:");
    console.log(results.summary);
    console.log("\nSOURCES:");
    for (let i = 0; i < results.sources.length; i++) {
      console.log(`${i+1}. ${results.sources[i].title} - ${results.sources[i].url}`);
    }
  },
  (error) => console.error("Workflow error:", error)
);
```

### curl - Simple Model List Request
```bash
curl -X GET "http://localhost:8435/v2/models/cohere"
```

### curl - Chat Request
```bash
curl -X POST "http://localhost:8435/v2/chat/cohere" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "command-light",
    "prompt": "What are the main principles of good API design?",
    "max_tokens": 500,
    "stream": false
  }'
```

### curl - Tool Calling Example
```bash
curl -X POST "http://localhost:8435/v2/tools/cohere" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "command-r-plus-08-2024",
    "prompt": "What is the weather in New York?",
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
                "description": "The city and state, e.g. San Francisco, CA"
              },
              "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit of temperature to use"
              }
            },
            "required": ["location"]
          }
        }
      }
    ],
    "max_tokens": 200
  }'
```

### curl - Dreamwalker Swarm Example (Coming Soon)
```bash
curl -X POST "http://localhost:8435/v2/dreamwalker/swarm" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Impact of artificial intelligence on job markets",
    "search_count": 10,
    "max_tokens": 1500,
    "expansion_model": "deepseek-r1-32b",
    "summarization_model": "mistral-small"
  }'
```

### Python - MLX Chat Example
```python
import requests
import json

API_URL = "http://localhost:8435/v2"

def chat_with_mlx(prompt, model_id="mistral-7b"):
    """
    Chat with MLX using the specified model.
    
    Args:
        prompt: The user prompt
        model_id: The MLX model ID
        
    Returns:
        The model's response
    """
    endpoint = f"{API_URL}/chat/mlx"
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Example usage
response = chat_with_mlx("What are the main features of Python 3.12?")
print(response)
```

### Python - Web Search Example
```python
import requests
import json

API_URL = "http://localhost:8435/v2"

def search_duckduckgo(query, max_results=5):
    """
    Search the web using DuckDuckGo through the API.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        The search results
    """
    # Method 1: Using GET request with parameters
    endpoint = f"{API_URL}/web/duckduckgo"
    params = {
        "query": query,
        "max_results": max_results,
        "safesearch": "moderate"
    }
    
    response = requests.get(endpoint, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"

def search_duckduckgo_post(query, max_results=5, region="us-en"):
    """
    Search the web using DuckDuckGo through the API using POST.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        region: Region for the search
        
    Returns:
        The search results
    """
    # Method 2: Using POST request with JSON body
    endpoint = f"{API_URL}/web/duckduckgo"
    payload = {
        "query": query,
        "max_results": max_results,
        "region": region,
        "safesearch": "moderate"
    }
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"

# Example usage
print("GET Method Example:")
results = search_duckduckgo("Python Flask API tutorial")
print(f"Found {results['count']} results for '{results['query']}'")
for i, result in enumerate(results['results']):
    print(f"{i+1}. {result['title']}")
    print(f"   {result['href']}")
    print(f"   {result['body'][:100]}...")
    print()

print("\nPOST Method Example:")
results = search_duckduckgo_post("accessibility design principles")
print(f"Found {results['count']} results for '{results['query']}'")
for i, result in enumerate(results['results']):
    print(f"{i+1}. {result['title']}")
    print(f"   {result['href']}")
    print(f"   {result['body'][:100]}...")
    print()
```

### JavaScript - Web Search Example
```javascript
// DuckDuckGo Search Example using JavaScript

const API_URL = "http://localhost:8435/v2";

// Method 1: Using GET request with parameters
async function searchDuckDuckGo(query, maxResults = 5) {
  try {
    // Build the URL with query parameters
    const url = new URL(`${API_URL}/web/duckduckgo`);
    url.searchParams.append('query', query);
    url.searchParams.append('max_results', maxResults);
    url.searchParams.append('safesearch', 'moderate');
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${await response.text()}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Search error:", error);
    return { error: error.message };
  }
}

// Method 2: Using POST request with JSON body
async function searchDuckDuckGoPost(query, maxResults = 5, region = "us-en") {
  try {
    const response = await fetch(`${API_URL}/web/duckduckgo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: query,
        max_results: maxResults,
        region: region,
        safesearch: 'moderate'
      })
    });
    
    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${await response.text()}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Search error:", error);
    return { error: error.message };
  }
}

// Example usage
async function runExamples() {
  console.log("GET Method Example:");
  const getResults = await searchDuckDuckGo("JavaScript API tutorial");
  console.log(`Found ${getResults.count} results for '${getResults.query}'`);
  getResults.results.forEach((result, index) => {
    console.log(`${index + 1}. ${result.title}`);
    console.log(`   ${result.href}`);
    console.log(`   ${result.body.substring(0, 100)}...`);
    console.log();
  });
  
  console.log("\nPOST Method Example:");
  const postResults = await searchDuckDuckGoPost("web accessibility standards");
  console.log(`Found ${postResults.count} results for '${postResults.query}'`);
  postResults.results.forEach((result, index) => {
    console.log(`${index + 1}. ${result.title}`);
    console.log(`   ${result.href}`);
    console.log(`   ${result.body.substring(0, 100)}...`);
    console.log();
  });
}

// Run the examples
runExamples().catch(error => console.error("Example error:", error));
```

### Code Execution Tool

Use the code execution tool to safely run Python code in a restricted environment.

**Endpoint:** `POST /v2/tools/execute/code`

**Request Body:**
```json
{
  "code": "import math\nprint(math.sqrt(16))"
}
```

**Response:**
```json
{
  "success": true,
  "result": "4.0\n",
  "code": "import math\nprint(math.sqrt(16))"
}
```

### Text Analysis Tool

Analyze text for sentiment, entities, and offensive content using the Tisane API.

**Endpoint:** `POST /v2/tools/analyze/text`

**Request Body:**
```json
{
  "text": "I love this product! It's the best purchase I've made this year.",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "result": "Text Analysis Results:\n\n  Sentiment: Unknown\n  No key entities found.\n  No offensive content detected.\n",
  "text": "I love this product! It's the best purchase I've made this year.",
  "language": "en"
}
```

### Data Formatting Tool

Convert data between different formats including JSON, YAML, TOML, XML, and CSV.

**Endpoint:** `POST /v2/tools/process/format`

**Request Body:**
```json
{
  "data": {"name": "John", "age": 30, "city": "New York"},
  "target_format": "yaml",
  "style": "pretty"
}
```

**Response:**
```json
{
  "success": true,
  "result": "name: John\nage: 30\ncity: New York\n",
  "original_data": {"name": "John", "age": 30, "city": "New York"},
  "target_format": "yaml",
  "style": "pretty"
}
```

### Direct Tool Execution Endpoints

These endpoints allow direct execution of tools without going through AI models:

- `POST /v2/tools/execute/analyze_text`: Directly analyze text 
- `POST /v2/tools/execute/format_data`: Directly convert data between formats

### Extension Tool Schemas Endpoint

Get the JSON schemas for all extension tools.

**Endpoint:** `GET /v2/tools/schemas/extensions`

**Response:**
```json
[
  {
    "type": "function",
    "function": {
      "name": "execute_code",
      "description": "Execute Python code in a restricted environment",
      "parameters": {
        "type": "object",
        "properties": {
          "code": {
            "type": "string",
            "description": "The Python code to execute"
          }
        },
        "required": ["code"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "analyze_text",
      "description": "Analyze text for sentiment, key entities, and offensive content",
      "parameters": {
        "type": "object",
        "properties": {
          "text": {
            "type": "string",
            "description": "The text to analyze"
          },
          "language": {
            "type": "string",
            "description": "The language code (default: 'en')"
          }
        },
        "required": ["text"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "format_data",
      "description": "Convert data between JSON and other formats (YAML, TOML, XML, CSV)",
      "parameters": {
        "type": "object",
        "properties": {
          "data": {
            "type": "object",
            "description": "The data to convert (as JSON object or string)"
          },
          "target_format": {
            "type": "string",
            "enum": ["json", "yaml", "toml", "xml", "csv"],
            "description": "The target format"
          },
          "style": {
            "type": "string",
            "enum": ["pretty", "compact", "single_line"],
            "description": "Output style"
          }
        },
        "required": ["data", "target_format"]
      }
    }
  }
]
```