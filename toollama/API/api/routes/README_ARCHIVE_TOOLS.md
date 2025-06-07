# Archive Tools

This module provides tools for retrieving archived versions of web pages from various archive services.

## Available Providers

### 1. Wayback Machine (Internet Archive)

The Wayback Machine is a digital archive of the World Wide Web maintained by the Internet Archive. It allows users to view archived versions of web pages across time.

**Provider ID:** `wayback`

**Example:**
```
GET /v2/tools/archive?url=https://example.com&provider=wayback
```

### 2. Archive.is

Archive.is (also known as archive.today) is a time capsule for web pages that takes snapshots of web pages and stores them permanently.

**Provider ID:** `archiveis`

**Example:**
```
POST /v2/tools/archive
{
  "url": "https://example.com",
  "provider": "archiveis",
  "capture": false
}
```

Setting `capture` to `true` will create a new snapshot if one doesn't exist.

### 3. Memento Aggregator

The Memento Aggregator provides a unified interface to multiple web archives, allowing users to find archived versions across different services.

**Provider ID:** `memento`

**Example:**
```
POST /v2/tools/archive
{
  "url": "https://example.com",
  "provider": "memento"
}
```

### 4. 12ft.io

12ft.io is a service that helps bypass paywalls and remove visual distractions from webpages by disabling JavaScript. It works by prepending "12ft.io/" to the URL.

**Provider ID:** `12ft`

**Example:**
```
POST /v2/tools/archive
{
  "url": "https://example.com",
  "provider": "12ft"
}
```

## API Endpoints

### Get Archived Webpage

Retrieve an archived version of a webpage from various archive services.

**Endpoint:** `GET /v2/tools/archive`

**Query Parameters:**
- `url` (required): The URL to find an archived version for
- `provider` (optional): The archive provider to use (wayback, archiveis, memento, 12ft). Default is 'wayback'
- `capture` (optional): Whether to capture a new snapshot (for archiveis only). Default is false

**Response:**
```json
{
  "original_url": "https://example.com",
  "provider": "wayback",
  "timestamp": "2023-01-01T12:00:00.000000",
  "success": true,
  "archived_url": "https://web.archive.org/web/20230101120000/https://example.com",
  "message": "Successfully retrieved the most recent snapshot from the Wayback Machine"
}
```

### Execute Archive Tool Directly

Execute the archive tool directly without going through a provider's tool calling mechanism.

**Endpoint:** `POST /v2/tools/execute/get_archived_webpage`

**Request Body:**
```json
{
  "url": "https://example.com",
  "provider": "wayback"
}
```

**Response:** Same as the GET endpoint.

### Get Archive Tool Schema

Get the JSON schema for the archive tool.

**Endpoint:** `GET /v2/tools/archive/schema`

**Response:**
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
          "enum": ["wayback", "archiveis", "memento", "12ft"],
          "description": "The archive provider to use (wayback, archiveis, memento, 12ft)"
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

## Testing

You can test the archive tools using the provided test script:

```bash
python -m api.tests.test_archive_tool
```

This will run tests for all providers and endpoints. 

## Implementation Details and Troubleshooting

### Dependencies

The archive tools rely on the following Python packages:

- `waybackpy` (version 2.4.4): For accessing the Wayback Machine API
- `archiveis`: For accessing the Archive.is API
- `requests`: For making HTTP requests to the Memento Aggregator and 12ft.io

### Common Issues

1. **Wayback Machine API Issues**:
   - The Wayback Machine API may not have snapshots for all URLs
   - The API may return different response formats depending on the version of `waybackpy`
   - If you encounter issues, try using the `save()` method to create a new snapshot

2. **Archive.is Timeouts**:
   - Archive.is may sometimes time out when retrieving snapshots
   - Setting `capture=true` can help create a new snapshot if one doesn't exist

3. **Memento Aggregator URL Format**:
   - The Memento Aggregator requires a specific URL format
   - Make sure the URL includes the http:// or https:// prefix

4. **12ft.io Redirects**:
   - 12ft.io often returns a 302 redirect status code, which is normal
   - The service may not work for all websites, especially those with advanced anti-scraping measures

### Example Usage

```python
import requests

# Example: Get a 12ft.io link for a paywalled article
response = requests.post("http://localhost:8435/v2/tools/archive", json={
    "url": "https://www.nytimes.com/2023/01/01/world/europe/ukraine-russia-war.html",
    "provider": "12ft"
})

if response.status_code == 200:
    result = response.json()
    if result["success"]:
        print(f"12ft.io URL: {result['archived_url']}")
    else:
        print(f"Error: {result['message']}")
else:
    print(f"Error: {response.status_code}")
```

For more examples, see the `api/examples/12ft_example.py` script. 