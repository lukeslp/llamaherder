# Camina Chat API Tools

This directory contains the API endpoints for various tools that can be used by AI models through the Camina Chat API.

## Available Tools

### Archive Retrieval Tool

The Archive Retrieval Tool allows AI models to access archived versions of web pages through various archive services.

#### Supported Archive Services

- **Wayback Machine (Internet Archive)**: Retrieves the most recent snapshot from the Internet Archive's Wayback Machine.
- **Archive.is**: Retrieves or captures snapshots from Archive.is.
- **Memento Aggregator**: Retrieves snapshots from multiple archive services through the Memento protocol.

#### Endpoints

- `GET /v2/tools/archive`: Retrieve an archived version of a webpage
- `POST /v2/tools/archive`: Retrieve an archived version of a webpage
- `GET /v2/tools/archive/schema`: Get the JSON schema for the archive tool
- `POST /v2/tools/execute/get_archived_webpage`: Execute the archive tool directly

#### Usage Examples

**Retrieve a snapshot from the Wayback Machine:**

```bash
curl -X GET "http://localhost:8435/v2/tools/archive?url=https://example.com&provider=wayback"
```

**Capture a new snapshot with Archive.is:**

```bash
curl -X POST "http://localhost:8435/v2/tools/archive" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "provider": "archiveis",
    "capture": true
  }'
```

**Execute the tool directly:**

```bash
curl -X POST "http://localhost:8435/v2/tools/execute/get_archived_webpage" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "provider": "memento"
  }'
```

#### Tool Schema

The tool schema for the archive retrieval tool is:

```json
{
  "type": "function",
  "function": {
    "name": "get_archived_webpage",
    "description": "Retrieve an archived version of a webpage from various archive services",
    "parameters": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "The URL to find an archived version for"
        },
        "provider": {
          "type": "string",
          "enum": ["wayback", "archiveis", "memento"],
          "description": "The archive provider to use (wayback, archiveis, memento)"
        },
        "capture": {
          "type": "boolean",
          "description": "Whether to capture a new snapshot (for archiveis only)"
        }
      },
      "required": ["url"]
    }
  }
}
```

### Code Execution Tool

The Code Execution Tool allows AI models to execute Python code in a restricted sandbox environment.

#### Endpoints

- `POST /v2/tools/execute/code`: Execute Python code in a restricted environment
- `GET /v2/tools/schemas/extensions`: Get the JSON schemas for all extended tools

#### Usage Examples

**Execute Python code:**

```bash
curl -X POST "http://localhost:8435/v2/tools/execute/code" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import math\nprint(math.sqrt(16))"
  }'
```

#### Tool Schema

The tool schema for the code execution tool is:

```json
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
}
```

### Text Analysis Tool

The Text Analysis Tool allows AI models to analyze text for sentiment, key entities, and offensive content using the Tisane API.

#### Endpoints

- `POST /v2/tools/analyze/text`: Analyze text for sentiment, entities, and offensive content

#### Usage Examples

**Analyze text:**

```bash
curl -X POST "http://localhost:8435/v2/tools/analyze/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this product, it works great!",
    "language": "en"
  }'
```

#### Tool Schema

The tool schema for the text analysis tool is:

```json
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
        },
        "api_key": {
          "type": "string",
          "description": "The Tisane API key (optional, uses default if not provided)"
        }
      },
      "required": ["text"]
    }
  }
}
```

### Data Formatting Tool

The Data Formatting Tool allows AI models to convert data between different formats including JSON, YAML, TOML, XML, and CSV.

#### Endpoints

- `POST /v2/tools/process/format`: Convert data between different formats

#### Usage Examples

**Convert JSON to YAML:**

```bash
curl -X POST "http://localhost:8435/v2/tools/process/format" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"name": "John", "age": 30, "city": "New York"},
    "target_format": "yaml",
    "style": "pretty"
  }'
```

#### Tool Schema

The tool schema for the data formatting tool is:

```json
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
```

## Installation

To install the required dependencies for the tools, run:

```bash
pip install -r requirements-tools.txt
```

## Adding New Tools

To add a new tool:

1. Create a new endpoint in `tools.py` for the tool
2. Add a schema endpoint for the tool
3. Add an execute endpoint for direct tool calls
4. Update the `get_tool_schemas` function to include the new tool
5. Add any required dependencies to `requirements-tools.txt`
6. Document the tool in this README

## Accessibility Considerations

All tools are designed with accessibility in mind:

- JSON responses include descriptive messages for screen readers
- Error messages are clear and informative
- Tools can be accessed through both GET and POST methods for flexibility
- Documentation includes examples for all tools 

## Security Considerations

All tools are implemented with security in mind:

- Code execution is performed in a restricted environment with limited imports and system access
- API keys and sensitive information are handled securely
- Input validation is performed for all endpoints
- Rate limiting is recommended for production deployments

## Error Handling

All tools include comprehensive error handling:

- Descriptive error messages are returned for invalid inputs
- Timeouts are implemented for external API calls
- Dependencies are checked at runtime
- Proper HTTP status codes are returned for different error types 