"""
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

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Provide test configuration"""
    return TEST_CONFIG

@pytest.fixture
def mock_credentials(monkeypatch):
    """Set up mock credentials for testing"""
    for key, value in TEST_CONFIG['mock_credentials'].items():
        monkeypatch.setenv(key, value)
    return TEST_CONFIG['mock_credentials']

@pytest.fixture
async def model_registry(test_config):
    """Provide configured model registry"""
    registry = ModelRegistry('tests/data/models.yaml')
    yield registry

@pytest.fixture
async def tool_router(model_registry):
    """Provide configured tool router"""
    router = ToolRouter(model_registry)
    yield router

@pytest.fixture
async def tool_discovery(tool_router, model_registry):
    """Provide configured tool discovery"""
    discovery = ToolDiscovery('tests/data/tools', tool_router, model_registry)
    yield discovery

@pytest.fixture
async def model_communicator(test_config):
    """Provide configured model communicator"""
    communicator = ModelCommunicator(test_config)
    yield communicator
    # Cleanup
    await communicator.close()

@pytest.fixture
async def task_manager():
    """Provide configured task manager"""
    manager = TaskManager()
    yield manager

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test data fixtures
@pytest.fixture
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

@pytest.fixture
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

@pytest.fixture
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
