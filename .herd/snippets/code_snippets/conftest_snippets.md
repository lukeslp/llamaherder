# Code Snippets from toollama/tests/conftest.py

File: `toollama/tests/conftest.py`  
Language: Python  
Extracted: 2025-06-07 05:10:59  

## Snippet 1
Lines 2-32

```Python
Test configuration and fixtures for the MoE system.
"""

import os
import pytest
import asyncio
from typing import Dict, Any
from pathlib import Path
from moe.core import (
    ModelRegistry,
    ToolRouter,
    ToolDiscovery,
    ModelCommunicator,
    TaskManager
)

# Test configuration
TEST_CONFIG = {
    'model_endpoints': {
        'camina': 'http://localhost:8000/camina',
        'property_belter': 'http://localhost:8001/belter',
        'location_drummer': 'http://localhost:8002/drummer'
    },
    'test_data_dir': Path(__file__).parent / 'data',
    'mock_credentials': {
        'COHERE_API_KEY': 'test-cohere-key',
        'MISTRAL_API_KEY': 'test-mistral-key',
        'PERPLEXITY_API_KEY': 'test-perplexity-key'
    }
}
```

## Snippet 2
Lines 34-37

```Python
def test_config() -> Dict[str, Any]:
    """Provide test configuration"""
    return TEST_CONFIG
```

## Snippet 3
Lines 41-44

```Python
for key, value in TEST_CONFIG['mock_credentials'].items():
        monkeypatch.setenv(key, value)
    return TEST_CONFIG['mock_credentials']
```

## Snippet 4
Lines 46-50

```Python
async def model_registry(test_config):
    """Provide configured model registry"""
    registry = ModelRegistry('tests/data/models.yaml')
    yield registry
```

## Snippet 5
Lines 52-56

```Python
async def tool_router(model_registry):
    """Provide configured tool router"""
    router = ToolRouter(model_registry)
    yield router
```

## Snippet 6
Lines 58-62

```Python
async def tool_discovery(tool_router, model_registry):
    """Provide configured tool discovery"""
    discovery = ToolDiscovery('tests/data/tools', tool_router, model_registry)
    yield discovery
```

## Snippet 7
Lines 64-70

```Python
async def model_communicator(test_config):
    """Provide configured model communicator"""
    communicator = ModelCommunicator(test_config)
    yield communicator
    # Cleanup
    await communicator.close()
```

## Snippet 8
Lines 72-76

```Python
async def task_manager():
    """Provide configured task manager"""
    manager = TaskManager()
    yield manager
```

## Snippet 9
Lines 86-96

```Python
def sample_property_request():
    """Sample property analysis request"""
    return {
        'message_type': 'task',
        'content': {
            'address': '309 Por La Mar Circle, Santa Barbara, CA',
            'analysis_type': 'comprehensive',
            'include': ['location', 'market', 'environment']
        }
    }
```

## Snippet 10
Lines 98-108

```Python
def sample_research_request():
    """Sample research request"""
    return {
        'message_type': 'task',
        'content': {
            'query': 'Recent advances in speech pathology',
            'depth': 'detailed',
            'domains': ['academic', 'web']
        }
    }
```

## Snippet 11
Lines 110-126

```Python
def sample_llm_request():
    """Sample LLM task request"""
    return {
        'message_type': 'task',
        'content': {
            'task': 'generate',
            'provider': 'auto',
            'content': {
                'prompt': 'Explain quantum computing',
                'max_tokens': 500
            },
            'preferences': {
                'model_size': 'medium',
                'priority': 'quality'
            }
        }
    }
```

