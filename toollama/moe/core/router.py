"""
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

class ToolRequest(BaseModel):
    """Tool request configuration"""
    tool_id: str = Field(..., description="Unique tool identifier")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    dependencies: List[str] = Field(default_factory=list, description="Required tool dependencies")
    timeout: Optional[int] = Field(None, description="Request timeout in seconds")
    retry_count: int = Field(default=3, description="Number of retry attempts")

class ToolResponse(BaseModel):
    """Tool response configuration"""
    tool_id: str = Field(..., description="Tool identifier")
    status: str = Field(..., description="Execution status")
    result: Optional[Any] = Field(None, description="Execution result")
    error: Optional[str] = Field(None, description="Error message if any")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Execution metrics")

class ToolHandler:
    """Base class for tool handlers"""
    
    tool_id: str = None  # Should be overridden by subclasses
    metadata: Dict[str, Any] = {  # Default metadata, should be overridden
        "category": "general",
        "capabilities": []
    }
    
    def __init__(self, tool_id: Optional[str] = None):
        """
        Initialize the tool handler.
        
        Args:
            tool_id: Optional tool identifier (defaults to class tool_id)
        """
        self.tool_id = tool_id or self.tool_id
        if not self.tool_id:
            raise ValueError("Tool ID must be specified either in class or constructor")
        logger.debug(f"Initialized tool handler {self.tool_id}")
        
    async def execute(self, parameters: Dict[str, Any]) -> Any:
        """Execute tool with parameters"""
        raise NotImplementedError

class RouterError(Exception):
    """Base class for router exceptions"""
    pass

class ToolNotFoundError(RouterError):
    """Raised when a requested tool is not found"""
    pass

class DependencyError(RouterError):
    """Raised when tool dependencies cannot be satisfied"""
    pass

class ToolRouter:
    """Central router for managing tool execution"""
    
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
        
    def register_handler(self, tool_id: str, handler: ToolHandler) -> None:
        """
        Register a tool handler.
        
        Args:
            tool_id: Tool identifier
            handler: Tool handler instance
        """
        self.handlers[tool_id] = handler
        logger.info(f"Registered handler for tool {tool_id}")
        
    def register_dependencies(self, tool_id: str, dependencies: List[str]) -> None:
        """
        Register tool dependencies.
        
        Args:
            tool_id: Tool identifier
            dependencies: List of required tool IDs
        """
        self.dependencies[tool_id] = set(dependencies)
        logger.info(f"Registered dependencies for tool {tool_id}")
        
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
            # Check if tool exists
            if request.tool_id not in self.handlers:
                raise ToolNotFoundError(f"Tool {request.tool_id} not found")
                
            # Check dependencies
            await self._check_dependencies(request.tool_id)
            
            # Get handler
            handler = self.handlers[request.tool_id]
            
            # Execute with retry logic
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
                    if attempt == request.retry_count - 1:
                        raise
                    logger.warning(f"Tool {request.tool_id} failed attempt {attempt + 1}: {str(e)}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        except Exception as e:
            logger.error(f"Tool {request.tool_id} execution failed: {str(e)}")
            return ToolResponse(
                tool_id=request.tool_id,
                status="error",
                error=str(e)
            )
            
    async def _check_dependencies(self, tool_id: str) -> None:
        """
        Check if tool dependencies are satisfied.
        
        Args:
            tool_id: Tool identifier
            
        Raises:
            DependencyError: If dependencies not satisfied
        """
        if tool_id not in self.dependencies:
            return
            
        missing = [
            dep for dep in self.dependencies[tool_id]
            if dep not in self.handlers
        ]
        
        if missing:
            raise DependencyError(
                f"Tool {tool_id} missing dependencies: {', '.join(missing)}"
            )
            
    def _update_metrics(self, tool_id: str, execution_time: float) -> None:
        """Update tool execution metrics"""
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
        
    def get_metrics(self, tool_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get tool execution metrics.
        
        Args:
            tool_id: Optional tool identifier
            
        Returns:
            Dict of metrics
        """
        if tool_id:
            return self.metrics.get(tool_id, {})
        return self.metrics 