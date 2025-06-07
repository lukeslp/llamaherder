# Dreamwalker Framework

Dreamwalker is an advanced multi-step AI workflow framework for complex tasks. It provides a structured approach to implementing AI-powered workflows that require multiple steps, parallel processing, and comprehensive result generation.

## Overview

The Dreamwalker framework is designed to handle complex AI workflows that involve multiple steps and require coordination between different components. It provides a foundation for implementing workflows that can:

1. Break down complex tasks into manageable steps
2. Execute steps in parallel or sequence
3. Track progress and provide status updates
4. Handle errors and recover from failures
5. Generate comprehensive results

## Components

The framework consists of the following components:

### BaseDreamwalker

The `BaseDreamwalker` class serves as the foundation for all Dreamwalker workflows. It provides:

- Workflow lifecycle management (initialization, execution, completion, failure)
- Progress tracking and status updates
- Error handling and recovery
- Serialization for API responses

### SwarmDreamwalker

The `SwarmDreamwalker` class implements a specific workflow for comprehensive web search and summarization. It:

1. Expands a user query into multiple related search queries
2. Executes searches in parallel across multiple search engines
3. Extracts and processes the results
4. Generates a comprehensive summary with proper citations

## API Endpoints

The Dreamwalker framework exposes the following API endpoints:

- `POST /dreamwalker/search`: Start a new search workflow
- `GET /dreamwalker/status/{workflow_id}`: Get the status of a workflow
- `GET /dreamwalker/result/{workflow_id}`: Get the result of a completed workflow
- `DELETE /dreamwalker/cancel/{workflow_id}`: Cancel a running workflow
- `GET /dreamwalker/list`: List active workflows
- `DELETE /dreamwalker/cleanup`: Clean up old workflows

## Usage

### Starting a Search Workflow

```python
import requests

# Start a new search workflow
response = requests.post(
    "http://localhost:8000/dreamwalker/search",
    json={
        "query": "What are the latest developments in quantum computing?",
        "workflow_type": "swarm",
        "model": "coolhand/camina-search:24b"  # Optional
    }
)

# Get the workflow ID
workflow_id = response.json()["workflow_id"]
```

### Checking Workflow Status

```python
# Check the status of the workflow
status_response = requests.get(
    f"http://localhost:8000/dreamwalker/status/{workflow_id}"
)

status = status_response.json()
print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")
print(f"Step: {status['step_description']}")
```

### Getting Workflow Results

```python
# Get the results of the workflow
result_response = requests.get(
    f"http://localhost:8000/dreamwalker/result/{workflow_id}"
)

result = result_response.json()
print(f"Query: {result['query']}")
print(f"Variant Queries: {result['variant_queries']}")
print(f"Summary: {result['summary']}")
```

## Extending the Framework

The Dreamwalker framework is designed to be extensible. To create a new workflow:

1. Create a new class that inherits from `BaseDreamwalker`
2. Implement the `execute` method to define the workflow logic
3. Use the `update_progress`, `complete`, and `fail` methods to manage the workflow lifecycle
4. Register the workflow type in the API routes

Example:

```python
from api.dreamwalker.base import BaseDreamwalker

class CustomDreamwalker(BaseDreamwalker):
    async def execute(self, query: str, **kwargs):
        try:
            # Initialize the workflow
            self.update_progress(0, "Starting custom workflow")
            
            # Step 1: Process the query
            self.update_progress(25, "Processing query")
            # ... implementation ...
            
            # Step 2: Generate results
            self.update_progress(50, "Generating results")
            # ... implementation ...
            
            # Step 3: Format the response
            self.update_progress(75, "Formatting response")
            # ... implementation ...
            
            # Complete the workflow
            results = {
                "query": query,
                "result": "Custom workflow result"
            }
            return self.complete(results)
            
        except Exception as e:
            return self.fail(str(e))
```

## Requirements

The Dreamwalker framework requires:

- Python 3.8+
- FastAPI
- Pydantic
- Requests
- AsyncIO

For the SwarmDreamwalker implementation, it also requires:

- Access to the Assisted.Space API
- The `infinite_search` module for web search capabilities

## Error Handling

The Dreamwalker framework includes comprehensive error handling:

- Workflow execution errors are caught and reported
- API endpoints return appropriate HTTP status codes and error messages
- Background tasks are properly managed to prevent resource leaks

## Future Enhancements

Planned enhancements for the Dreamwalker framework include:

- Support for streaming responses
- Persistent storage for workflow state
- Additional workflow types for different use cases
- Enhanced parallelism and distributed execution
- User authentication and authorization 