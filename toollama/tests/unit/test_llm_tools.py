"""
Unit tests for LLM tools.
"""

import pytest
from unittest.mock import AsyncMock, patch
from moe.tools.llm.cohere import CohereTool
from moe.tools.llm.mistral import MistralTool
from moe.tools.llm.perplexity import PerplexityTool

# Cohere Tests
@pytest.mark.asyncio
async def test_cohere_initialization(mock_credentials):
    """Test Cohere tool initialization"""
    tool = CohereTool()
    assert tool.api_key == mock_credentials['COHERE_API_KEY']
    assert tool.client is not None

@pytest.mark.asyncio
async def test_cohere_generate():
    """Test Cohere text generation"""
    with patch('cohere.Client') as mock_client:
        # Set up mock response
        mock_response = AsyncMock()
        mock_response.generations = [
            AsyncMock(
                text="Generated text",
                finish_reason="complete",
                token_count=10
            )
        ]
        mock_client.return_value.generate.return_value = mock_response
        
        # Create tool and execute
        tool = CohereTool()
        result = await tool.execute({
            'task': 'generate',
            'prompt': 'Test prompt',
            'max_tokens': 100
        })
        
        # Verify result
        assert result['text'] == "Generated text"
        assert result['finish_reason'] == "complete"
        assert result['tokens'] == 10

@pytest.mark.asyncio
async def test_cohere_embed():
    """Test Cohere embeddings"""
    with patch('cohere.Client') as mock_client:
        # Set up mock response
        mock_response = AsyncMock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_response.meta = {'dimension': 3}
        mock_client.return_value.embed.return_value = mock_response
        
        # Create tool and execute
        tool = CohereTool()
        result = await tool.execute({
            'task': 'embed',
            'texts': ['Test text']
        })
        
        # Verify result
        assert result['embeddings'] == [[0.1, 0.2, 0.3]]
        assert result['meta']['dimension'] == 3

# Mistral Tests
@pytest.mark.asyncio
async def test_mistral_initialization(mock_credentials):
    """Test Mistral tool initialization"""
    tool = MistralTool()
    assert tool.api_key == mock_credentials['MISTRAL_API_KEY']
    assert tool.client is not None

@pytest.mark.asyncio
async def test_mistral_chat():
    """Test Mistral chat completion"""
    with patch('mistralai.client.MistralClient') as mock_client:
        # Set up mock response
        mock_response = AsyncMock()
        mock_response.choices = [
            AsyncMock(
                message=AsyncMock(
                    role="assistant",
                    content="Chat response"
                ),
                finish_reason="complete"
            )
        ]
        mock_response.usage = AsyncMock(
            prompt_tokens=5,
            completion_tokens=5,
            total_tokens=10
        )
        mock_client.return_value.chat.return_value = mock_response
        
        # Create tool and execute
        tool = MistralTool()
        result = await tool.execute({
            'task': 'chat',
            'messages': [
                {'role': 'user', 'content': 'Hello'}
            ]
        })
        
        # Verify result
        assert result['message']['role'] == "assistant"
        assert result['message']['content'] == "Chat response"
        assert result['usage']['total_tokens'] == 10

# Perplexity Tests
@pytest.mark.asyncio
async def test_perplexity_initialization(mock_credentials):
    """Test Perplexity tool initialization"""
    tool = PerplexityTool()
    assert tool.api_key == mock_credentials['PERPLEXITY_API_KEY']
    assert tool.client is not None

@pytest.mark.asyncio
async def test_perplexity_chat():
    """Test Perplexity chat completion"""
    with patch('httpx.AsyncClient') as mock_client:
        # Set up mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': 'Chat response'
                },
                'finish_reason': 'complete'
            }],
            'usage': {
                'prompt_tokens': 5,
                'completion_tokens': 5,
                'total_tokens': 10
            }
        }
        mock_client.return_value.post.return_value = mock_response
        
        # Create tool and execute
        tool = PerplexityTool()
        result = await tool.execute({
            'task': 'chat',
            'messages': [
                {'role': 'user', 'content': 'Hello'}
            ]
        })
        
        # Verify result
        assert result['message']['role'] == "assistant"
        assert result['message']['content'] == "Chat response"
        assert result['usage']['total_tokens'] == 10

# Error Handling Tests
@pytest.mark.asyncio
async def test_cohere_error_handling():
    """Test Cohere error handling"""
    with patch('cohere.Client') as mock_client:
        mock_client.return_value.generate.side_effect = Exception("API Error")
        
        tool = CohereTool()
        with pytest.raises(Exception) as exc_info:
            await tool.execute({
                'task': 'generate',
                'prompt': 'Test prompt'
            })
        assert str(exc_info.value) == "API Error"

@pytest.mark.asyncio
async def test_mistral_error_handling():
    """Test Mistral error handling"""
    with patch('mistralai.client.MistralClient') as mock_client:
        mock_client.return_value.chat.side_effect = Exception("API Error")
        
        tool = MistralTool()
        with pytest.raises(Exception) as exc_info:
            await tool.execute({
                'task': 'chat',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            })
        assert str(exc_info.value) == "API Error"

@pytest.mark.asyncio
async def test_perplexity_error_handling():
    """Test Perplexity error handling"""
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.post.side_effect = Exception("API Error")
        
        tool = PerplexityTool()
        with pytest.raises(Exception) as exc_info:
            await tool.execute({
                'task': 'chat',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            })
        assert str(exc_info.value) == "API Error" 