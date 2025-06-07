# OpenAI Responses API Documentation

The OpenAI Responses API endpoint (`/responses`) provides powerful document processing capabilities using OpenAI's models. This endpoint supports a wide range of advanced features that significantly enhance its analytical capabilities.

## Overview

The Responses API allows you to:

- Process PDF documents, text files, and other document formats
- Generate summaries, analyses, and other text-based outputs
- Stream responses for real-time feedback
- Utilize advanced capabilities like web search, file search, function calling, and computer use

## API Endpoints

### Create a Response

```
POST https://api.assisted.space/v2/responses
```

Creates a new document processing job with the provided files and parameters.

### Retrieve a Response

```
GET https://api.assisted.space/v2/responses/{response_id}
```

Retrieves the status or content of a previously created document processing job.

## Advanced Capabilities

### Web Search

Enable the model to perform real-time web searches to enhance responses with current information.

```json
{
  "web_search": true
}
```

**Example Use Cases:**
- Update document information with current facts
- Find recent developments related to topics in the document
- Validate information against current sources

### File Search

Allow the model to search within the uploaded documents for relevant information.

```json
{
  "file_search": true
}
```

**Example Use Cases:**
- Locate specific information across long documents
- Extract and summarize key sections from large files
- Compare information across multiple documents

### Function Calling

Define custom tools or functions that the model can invoke based on the user's prompt.

```json
{
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
              "enum": ["celsius", "fahrenheit"]
            }
          },
          "required": ["location"]
        }
      }
    }
  ]
}
```

**Example Use Cases:**
- Integrate with external APIs (weather, finance, etc.)
- Automate data retrieval based on document context
- Allow documents to trigger specific actions

### Computer Use (Code Interpreter)

Enable the model to perform calculations, execute code, and interact with files programmatically.

```json
{
  "computer_use": true
}
```

**Example Use Cases:**
- Perform advanced calculations based on document data
- Generate charts or visualizations from tabular information
- Execute code snippets to process data in documents

## Request Parameters

| Parameter      | Type               | Description                                                    | Default                 |
|----------------|--------------------|-----------------------------------------------------------------|------------------------|
| `file`         | File or File[]     | Document file(s) to process (PDF, docx, txt, etc.)             | Required               |
| `prompt`       | String             | Instruction for processing the document                        | Required               |
| `model`        | String             | OpenAI model to use for processing                             | gpt-4o-2024-11-20      |
| `max_tokens`   | Integer            | Maximum number of tokens in the response                       | 4096                   |
| `temperature`  | Number             | Sampling temperature between 0 and 2                           | 0.7                    |
| `stream`       | Boolean            | Whether to stream the response                                 | false                  |
| `tools`        | Array of Objects   | Custom tool definitions for function calling                   | None                   |
| `web_search`   | Boolean            | Enable web search capability                                   | false                  |
| `file_search`  | Boolean            | Enable file search capability                                  | false                  |
| `computer_use` | Boolean            | Enable computer use capability (code interpreter, file access) | false                  |
| `api_key`      | String             | The OpenAI API key (can also be provided in header)            | Required               |

## Request Examples

### Basic Request

```bash
curl -X POST https://api.assisted.space/v2/responses \
  -H "X-API-Key: your_api_key" \
  -F "file=@/path/to/your/document.pdf" \
  -F "prompt=Summarize the key points in this document" \
  -F "model=gpt-4o-2024-11-20" \
  -F "max_tokens=4096"
```

### Request with Web Search

```bash
curl -X POST https://api.assisted.space/v2/responses \
  -H "X-API-Key: your_api_key" \
  -F "file=@/path/to/your/document.pdf" \
  -F "prompt=Update this document with current information" \
  -F "model=gpt-4o-2024-11-20" \
  -F "web_search=true"
```

### Request with Function Calling

```bash
curl -X POST https://api.assisted.space/v2/responses \
  -H "X-API-Key: your_api_key" \
  -F "file=@/path/to/your/document.pdf" \
  -F "prompt=What's the weather like in the cities mentioned in this document?" \
  -F "model=gpt-4o-2024-11-20" \
  -F "tools=[{\"type\":\"function\",\"function\":{\"name\":\"get_weather\",\"description\":\"Get the current weather in a location\",\"parameters\":{\"type\":\"object\",\"properties\":{\"location\":{\"type\":\"string\",\"description\":\"The city and state, e.g. San Francisco, CA\"},\"unit\":{\"type\":\"string\",\"enum\":[\"celsius\",\"fahrenheit\"]}},\"required\":[\"location\"]}}}]"
```

### Request with Multiple Capabilities

```bash
curl -X POST https://api.assisted.space/v2/responses \
  -H "X-API-Key: your_api_key" \
  -F "file=@/path/to/your/document.pdf" \
  -F "prompt=Analyze this financial report, calculate key metrics, and compare with current market data" \
  -F "model=gpt-4o-2024-11-20" \
  -F "web_search=true" \
  -F "file_search=true" \
  -F "computer_use=true"
```

## Response Structure

### Initial Response

When first creating a processing job, you'll typically receive a status response:

```json
{
  "response_id": "resp_abc123",  // Unique identifier for the response
  "status": "in_progress",       // Status: in_progress, completed, failed
  "model": "gpt-4o-2024-11-20"   // Model used for processing
}
```

### Completed Response

When the processing is complete:

```json
{
  "response_id": "resp_abc123",  // Unique identifier for the response
  "status": "completed",         // Status: in_progress, completed, failed
  "model": "gpt-4o-2024-11-20",  // Model used for processing
  "content": "...",              // Generated response content
  "usage": {                     // Token usage information
    "prompt_tokens": 1522,
    "completion_tokens": 845,
    "total_tokens": 2367
  },
  "tool_calls": [                // Optional: Tools called during processing
    {
      "id": "call_123",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\":\"Seattle, WA\",\"unit\":\"celsius\"}"
      }
    }
  ]
}
```

### Error Response

If an error occurs:

```json
{
  "status": "failed",
  "response_id": "resp_abc123",
  "error": "Error message describing what went wrong"
}
```

## Streaming Responses

For long-running processes, you can enable streaming mode:

```bash
curl -X POST https://api.assisted.space/v2/responses \
  -H "X-API-Key: your_api_key" \
  -F "file=@/path/to/your/document.pdf" \
  -F "prompt=Provide a detailed analysis of this document" \
  -F "model=gpt-4o-2024-11-20" \
  -F "stream=true"
```

In streaming mode, the response will be sent as a series of chunks:

```json
{"type": "status", "status": "processing"}
{"type": "delta", "content": "Here"}
{"type": "delta", "content": " is"}
{"type": "delta", "content": " an"}
{"type": "delta", "content": " analysis"}
{"type": "tool_calls", "tool_calls": [...]}
```

## Best Practices

1. **Choose the right capabilities** - Only enable the capabilities you need to optimize performance and cost.
2. **Be specific in prompts** - Clear, detailed instructions yield better results.
3. **Use appropriate models** - More complex tasks typically require more advanced models like gpt-4o.
4. **Handle large documents appropriately** - Consider splitting very large documents or using file_search for targeted analysis.
5. **Cache results** - Use the response_id to retrieve previously generated content instead of reprocessing.
6. **Optimize file uploads** - Ensure files are in appropriate formats and sizes.
7. **Handle errors gracefully** - Implement robust error handling in your application.

## Error Handling

Common errors include:

- **400 Bad Request**: Missing required parameters or invalid format
- **401 Unauthorized**: Invalid API key
- **413 Payload Too Large**: Document size exceeds limits
- **429 Too Many Requests**: Rate limit exceeded
- **503 Service Unavailable**: Provider temporarily unavailable

Always check the response status code and error message for troubleshooting.

## Implementation Notes

- The API supports both direct API key inclusion in the request body and via the `X-API-Key` header
- Concurrent file uploads are supported by providing multiple file fields
- The API is fully asynchronous, so it will return a response ID immediately for large documents
- Document processing may take time depending on file size and complexity 