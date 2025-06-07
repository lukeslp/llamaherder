"""Tests for the MoE communication layer."""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch
from moe.core.communication import (
    ModelMessage,
    ModelResponse,
    ModelError,
    ModelTimeoutError,
    ModelNotFoundError,
    ModelCommunicator
)

@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return {
        'model_endpoints': {
            'test_model': 'http://localhost:8000/test',
            'another_model': 'http://localhost:8000/another'
        },
        'timeouts': {
            'test_model': 10,
            'another_model': 20
        },
        'retry_config': {
            'max_retries': 2,
            'backoff_factor': 1.0,
            'max_backoff': 5
        }
    }

@pytest.fixture
def communicator(test_config):
    """ModelCommunicator fixture"""
    return ModelCommunicator(test_config)

@pytest.mark.asyncio
async def test_send_message_success(communicator):
    """Test successful message sending"""
    message = {
        'message_type': 'test',
        'content': {'test': 'data'}
    }
    
    mock_response = {
        'model_id': 'test_model',
        'response_type': 'test_response',
        'content': {'result': 'success'},
        'execution_time': 0.1
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        response = await communicator.send_message('test_model', message)
        
        assert isinstance(response, ModelResponse)
        assert response.model_id == 'test_model'
        assert response.content == {'result': 'success'}
        assert response.execution_time > 0

@pytest.mark.asyncio
async def test_send_message_not_found(communicator):
    """Test sending message to non-existent model"""
    message = {
        'message_type': 'test',
        'content': {'test': 'data'}
    }
    
    with pytest.raises(ModelNotFoundError):
        await communicator.send_message('non_existent_model', message)

@pytest.mark.asyncio
async def test_send_message_timeout(communicator):
    """Test message timeout"""
    message = {
        'message_type': 'test',
        'content': {'test': 'data'}
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.side_effect = asyncio.TimeoutError()
        
        with pytest.raises(ModelTimeoutError):
            await communicator.send_message('test_model', message)

@pytest.mark.asyncio
async def test_broadcast_message(communicator):
    """Test broadcasting message to multiple models"""
    message = {
        'message_type': 'test',
        'content': {'test': 'data'}
    }
    
    mock_response = {
        'model_id': 'test_model',
        'response_type': 'test_response',
        'content': {'result': 'success'},
        'execution_time': 0.1
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        responses = await communicator.broadcast_message(
            message,
            ['test_model', 'another_model']
        )
        
        assert len(responses) == 2
        assert all(isinstance(r, ModelResponse) for r in responses)

@pytest.mark.asyncio
async def test_retry_logic(communicator):
    """Test retry logic with failing requests"""
    message = {
        'message_type': 'test',
        'content': {'test': 'data'}
    }
    
    mock_response = {
        'model_id': 'test_model',
        'response_type': 'test_response',
        'content': {'result': 'success'},
        'execution_time': 0.1
    }
    
    with patch('httpx.AsyncClient.post') as mock_post:
        # Fail twice, succeed on third try
        mock_post.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            AsyncMock(
                status_code=200,
                json=lambda: mock_response
            )
        ]
        
        with pytest.raises(ModelError):
            await communicator.send_message('test_model', message)
            
        assert mock_post.call_count == 2  # Should try twice based on config

def test_model_message_validation():
    """Test ModelMessage validation"""
    # Valid message
    message = ModelMessage(
        model_id='test_model',
        message_type='test',
        content={'test': 'data'}
    )
    assert message.model_id == 'test_model'
    assert message.content == {'test': 'data'}
    
    # Invalid message (missing required fields)
    with pytest.raises(ValueError):
        ModelMessage(
            message_type='test',
            content={'test': 'data'}
        )

def test_model_response_validation():
    """Test ModelResponse validation"""
    # Valid response
    response = ModelResponse(
        model_id='test_model',
        response_type='test',
        content={'result': 'success'},
        execution_time=0.1
    )
    assert response.model_id == 'test_model'
    assert response.execution_time == 0.1
    
    # Invalid response (missing required fields)
    with pytest.raises(ValueError):
        ModelResponse(
            model_id='test_model',
            content={'result': 'success'}
        )

@pytest.mark.asyncio
async def test_get_model_status(communicator):
    """Test getting model status"""
    status = await communicator.get_model_status('test_model')
    assert status['model_id'] == 'test_model'
    assert status['status'] == 'ready'
    assert status['endpoint'] == 'http://localhost:8000/test'
    
    with pytest.raises(ModelNotFoundError):
        await communicator.get_model_status('non_existent_model')

def test_update_model_config(communicator):
    """Test updating model configuration"""
    new_config = {
        'timeout': 30,
        'status': 'maintenance'
    }
    
    communicator.update_model_config('test_model', new_config)
    assert communicator.active_models['test_model']['timeout'] == 30
    assert communicator.active_models['test_model']['status'] == 'maintenance'
    
    with pytest.raises(ModelNotFoundError):
        communicator.update_model_config('non_existent_model', new_config) 