# Code Snippets from toollama/moe/core/router.py

File: `toollama/moe/core/router.py`  
Language: Python  
Extracted: 2025-06-07 05:11:32  

## Snippet 1
Lines 2-16

```Python
Tool router for the MoE system.
Manages tool routing, dependencies, and execution.
"""

from typing import Dict, Any, Optional, List, Set, Callable, Awaitable
from pydantic import BaseModel, Field
import asyncio
import logging
from pathlib import Path
from .registry import ModelRegistry, ModelNotFoundError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 17-24

```Python
class ToolRequest(BaseModel):
    """Tool request configuration"""
    tool_id: str = Field(..., description="Unique tool identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    dependencies: List[str] = Field(default_factory=list, description="Required tool dependencies")
    timeout: Optional[int] = Field(None, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retry attempts")
```

## Snippet 3
Lines 25-29

```Python
class ToolResponse(BaseModel):
    """Tool response configuration"""
    tool_id: str = Field(..., description="Tool identifier")
    status: str = Field(..., description="Execution status")
    result: Optional[Any] = Field(None, description="Execution result")
```

## Snippet 4
Lines 34-36

```Python
"""Base class for tool handlers"""

    tool_id: str = None  # Should be overridden by subclasses
```

## Snippet 5
Lines 37-41

```Python
metadata: Dict[str, Any] = {  # Default metadata, should be overridden
        "category": "general",
        "capabilities": []
    }
```

## Snippet 6
Lines 42-46

```Python
def __init__(self, tool_id: Optional[str] = None):
        """
        Initialize the tool handler.

        Args:
```

## Snippet 7
Lines 54-57

```Python
async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute tool with parameters"""
        raise NotImplementedError
```

## Snippet 8
Lines 62-65

```Python
class ToolNotFoundError(RouterError):
    """Raised when a requested tool is not found"""
    pass
```

## Snippet 9
Lines 66-69

```Python
class DependencyError(RouterError):
    """Raised when tool dependencies cannot be satisfied"""
    pass
```

## Snippet 10
Lines 73-85

```Python
def __init__(self, registry: ModelRegistry):
        """
        Initialize the router.

        Args:
            registry: Model registry instance
        """
        self.registry = registry
        self.handlers: Dict[str, ToolHandler] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.metrics: Dict[str, Dict[str, Any]] = {}
        logger.debug("Initialized tool router")
```

## Snippet 11
Lines 86-94

```Python
def register_handler(self, tool_id: str, handler: ToolHandler) -> None:
        """
        Register a tool handler.

        Args:
            tool_id: Tool identifier
            handler: Tool handler instance
        """
        self.handlers[tool_id] = handler
```

## Snippet 12
Lines 97-105

```Python
def register_dependencies(self, tool_id: str, dependencies: List[str]) -> None:
        """
        Register tool dependencies.

        Args:
            tool_id: Tool identifier
            dependencies: List of required tool IDs
        """
        self.dependencies[tool_id] = set(dependencies)
```

## Snippet 13
Lines 108-122

```Python
async def execute_tool(self, request: ToolRequest) -> ToolResponse:
        """
        Execute tool request.

        Args:
            request: Tool request

        Returns:
            ToolResponse object

        Raises:
            ToolNotFoundError: If tool not found
            DependencyError: If dependencies not satisfied
        """
        try:
```

## Snippet 14
Lines 127-133

```Python
# Check dependencies
            await self._check_dependencies(request.tool_id)

            # Get handler
            handler = self.handlers[request.tool_id]

            # Execute with retry logic
```

## Snippet 15
Lines 134-158

```Python
for attempt in range(request.retry_count):
                try:
                    # Start timing
                    start_time = asyncio.get_event_loop().time()

                    # Execute
                    result = await handler.execute(request.parameters)

                    # Calculate metrics
                    execution_time = asyncio.get_event_loop().time() - start_time

                    # Update metrics
                    self._update_metrics(request.tool_id, execution_time)

                    return ToolResponse(
                        tool_id=request.tool_id,
                        status="success",
                        result=result,
                        metrics={
                            "execution_time": execution_time,
                            "attempt": attempt + 1
                        }
                    )

                except Exception as e:
```

## Snippet 16
Lines 165-171

```Python
logger.error(f"Tool {request.tool_id} execution failed: {str(e)}")
            return ToolResponse(
                tool_id=request.tool_id,
                status="error",
                error=str(e)
            )
```

## Snippet 17
Lines 174-181

```Python
Check if tool dependencies are satisfied.

        Args:
            tool_id: Tool identifier

        Raises:
            DependencyError: If dependencies not satisfied
        """
```

## Snippet 18
Lines 182-185

```Python
if tool_id not in self.dependencies:
            return

        missing = [
```

## Snippet 19
Lines 197-208

```Python
if tool_id not in self.metrics:
            self.metrics[tool_id] = {
                "total_executions": 0,
                "total_time": 0.0,
                "average_time": 0.0
            }

        metrics = self.metrics[tool_id]
        metrics["total_executions"] += 1
        metrics["total_time"] += execution_time
        metrics["average_time"] = metrics["total_time"] / metrics["total_executions"]
```

## Snippet 20
Lines 209-218

```Python
def get_metrics(self, tool_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get tool execution metrics.

        Args:
            tool_id: Optional tool identifier

        Returns:
            Dict of metrics
        """
```

## Snippet 21
Lines 219-221

```Python
if tool_id:
            return self.metrics.get(tool_id, {})
        return self.metrics
```

