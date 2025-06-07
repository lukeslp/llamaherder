# Code Snippets from toollama/tests/integration/test_llm_integration.py

File: `toollama/tests/integration/test_llm_integration.py`  
Language: Python  
Extracted: 2025-06-07 05:11:28  

## Snippet 1
Lines 2-11

```Python
Integration tests for LLM integration.
Tests the interaction between LLM Belter and Drummers.
"""

import pytest
from unittest.mock import AsyncMock, patch
from moe.core import ModelCommunicator, TaskManager
from moe.models.belters.llm import LLMBelter
from moe.models.drummers.llm import LLMDrummer
```

## Snippet 2
Lines 13-57

```Python
async def test_llm_task_execution(
    model_communicator,
    task_manager,
    sample_llm_request
):
    """Test complete LLM task execution flow"""
    # Set up mocks
    mock_belter = AsyncMock(spec=LLMBelter)
    mock_drummer = AsyncMock(spec=LLMDrummer)

    # Mock responses
    mock_belter.process_request.return_value = {
        'task_id': 'test-task',
        'selected_model': 'mistral-small',
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 500
        }
    }

    mock_drummer.execute_task.return_value = {
        'content': 'Generated response',
        'usage': {
            'prompt_tokens': 10,
            'completion_tokens': 20,
            'total_tokens': 30
        }
    }

    # Execute task
    task = await task_manager.create_task(
        task_type='llm_generation',
        metadata=sample_llm_request
    )

    # Process with Belter
    belter_response = await mock_belter.process_request(task)
    assert belter_response['task_id'] == 'test-task'
    assert belter_response['selected_model'] == 'mistral-small'

    # Execute with Drummer
    drummer_response = await mock_drummer.execute_task(belter_response)
    assert drummer_response['content'] == 'Generated response'
    assert drummer_response['usage']['total_tokens'] == 30
```

## Snippet 3
Lines 59-73

```Python
async def test_model_selection_optimization(
    model_communicator,
    task_manager,
    sample_llm_request
):
    """Test model selection and cost optimization"""
    mock_belter = AsyncMock(spec=LLMBelter)

    # Test different priority scenarios
    scenarios = [
        ('speed', 'cohere-light'),
        ('quality', 'mistral-small'),
        ('cost', 'perplexity-7b')
    ]
```

## Snippet 4
Lines 74-98

```Python
for priority, expected_model in scenarios:
        # Update request priority
        request = sample_llm_request.copy()
        request['content']['preferences']['priority'] = priority

        # Create task
        task = await task_manager.create_task(
            task_type='llm_generation',
            metadata=request
        )

        # Mock Belter response
        mock_belter.process_request.return_value = {
            'task_id': f'test-task-{priority}',
            'selected_model': expected_model,
            'parameters': {
                'temperature': 0.7,
                'max_tokens': 500
            }
        }

        # Process request
        response = await mock_belter.process_request(task)
        assert response['selected_model'] == expected_model
```

## Snippet 5
Lines 100-111

```Python
async def test_error_handling_and_retry(
    model_communicator,
    task_manager,
    sample_llm_request
):
    """Test error handling and retry mechanism"""
    mock_belter = AsyncMock(spec=LLMBelter)
    mock_drummer = AsyncMock(spec=LLMDrummer)

    # Set up error then success scenario
    mock_drummer.execute_task.side_effect = [
        Exception("API Error"),  # First attempt fails
```

## Snippet 6
Lines 112-119

```Python
{  # Second attempt succeeds
            'content': 'Generated response',
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 20,
                'total_tokens': 30
            }
        }
```

## Snippet 7
Lines 120-138

```Python
]

    # Create and execute task
    task = await task_manager.create_task(
        task_type='llm_generation',
        metadata=sample_llm_request
    )

    # Process with Belter
    belter_response = await mock_belter.process_request(task)

    # First attempt should fail
    with pytest.raises(Exception):
        await mock_drummer.execute_task(belter_response)

    # Second attempt should succeed
    response = await mock_drummer.execute_task(belter_response)
    assert response['content'] == 'Generated response'
```

## Snippet 8
Lines 140-188

```Python
async def test_cost_tracking_and_limits(
    model_communicator,
    task_manager,
    sample_llm_request
):
    """Test cost tracking and budget limits"""
    mock_belter = AsyncMock(spec=LLMBelter)

    # Set budget limit
    request = sample_llm_request.copy()
    request['content']['preferences']['max_budget'] = 0.01  # 1 cent limit

    # Create task
    task = await task_manager.create_task(
        task_type='llm_generation',
        metadata=request
    )

    # Test with expensive model
    mock_belter.process_request.return_value = {
        'task_id': 'test-task',
        'selected_model': 'gpt4',
        'estimated_cost': 0.02,  # 2 cents, over budget
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 500
        }
    }

    # Should raise budget error
    with pytest.raises(Exception) as exc_info:
        await mock_belter.process_request(task)
    assert "Budget limit exceeded" in str(exc_info.value)

    # Test with affordable model
    mock_belter.process_request.return_value = {
        'task_id': 'test-task',
        'selected_model': 'mistral-small',
        'estimated_cost': 0.005,  # 0.5 cents, under budget
        'parameters': {
            'temperature': 0.7,
            'max_tokens': 500
        }
    }

    # Should succeed
    response = await mock_belter.process_request(task)
    assert response['estimated_cost'] <= request['content']['preferences']['max_budget']
```

## Snippet 9
Lines 190-199

```Python
async def test_parallel_execution(
    model_communicator,
    task_manager
):
    """Test parallel execution of LLM tasks"""
    mock_belter = AsyncMock(spec=LLMBelter)
    mock_drummer = AsyncMock(spec=LLMDrummer)

    # Create multiple tasks
    tasks = []
```

## Snippet 10
Lines 200-218

```Python
for i in range(3):
        request = {
            'message_type': 'task',
            'content': {
                'task': 'generate',
                'provider': 'auto',
                'content': {
                    'prompt': f'Test prompt {i}',
                    'max_tokens': 100
                }
            }
        }
        task = await task_manager.create_task(
            task_type='llm_generation',
            metadata=request
        )
        tasks.append(task)

    # Mock responses
```

