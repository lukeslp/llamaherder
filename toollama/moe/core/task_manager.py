"""
Task manager for coordinating execution and observation across the MoE system.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
import uuid

from .events import event_bus, ObservationEvent

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages task execution and coordination across the MoE system"""
    
    def __init__(self, max_concurrent: int = 5):
        """Initialize the task manager"""
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def create_task(
        self,
        content: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        self.active_tasks[task_id] = {
            "status": "created",
            "created_at": datetime.now(),
            "content": content,
            "type": task_type,
            "metadata": metadata or {},
            "history": []
        }
        
        # Notify observer of new task
        await event_bus.publish(
            "observation",
            ObservationEvent(
                timestamp=datetime.now(),
                content=f"New {task_type} task created: {content}",
                task_id=task_id,
                metadata={
                    "status": "created",
                    "type": task_type,
                    **metadata or {}
                }
            )
        )
        
        return task_id
        
    async def execute_task(
        self,
        task_id: str,
        executor_fn: Callable[..., Awaitable[Any]],
        *args,
        **kwargs
    ) -> Any:
        """Execute a task with real-time observation"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
            
        task_info = self.active_tasks[task_id]
        
        try:
            async with self.semaphore:
                # Update task status
                task_info["status"] = "running"
                task_info["started_at"] = datetime.now()
                
                # Notify observer of task start
                await event_bus.publish(
                    "observation",
                    ObservationEvent(
                        timestamp=datetime.now(),
                        content=f"Starting execution of {task_info['type']} task",
                        task_id=task_id,
                        metadata={
                            "status": "running",
                            "type": task_info["type"]
                        }
                    )
                )
                
                # Execute the task
                result = await executor_fn(*args, **kwargs)
                
                # Update task status and store result
                task_info["status"] = "completed"
                task_info["completed_at"] = datetime.now()
                task_info["result"] = result
                
                # Calculate execution time
                execution_time = (task_info["completed_at"] - task_info["started_at"]).total_seconds()
                
                # Notify observer of completion
                await event_bus.publish(
                    "observation",
                    ObservationEvent(
                        timestamp=datetime.now(),
                        content=f"Task completed successfully in {execution_time:.2f} seconds",
                        task_id=task_id,
                        metadata={
                            "status": "completed",
                            "type": task_info["type"],
                            "execution_time": execution_time
                        }
                    )
                )
                
                return result
                
        except Exception as e:
            # Update task status and store error
            task_info["status"] = "failed"
            task_info["error"] = str(e)
            task_info["failed_at"] = datetime.now()
            
            # Calculate time until failure
            failure_time = (task_info["failed_at"] - task_info["started_at"]).total_seconds()
            
            # Notify observer of failure
            await event_bus.publish(
                "observation",
                ObservationEvent(
                    timestamp=datetime.now(),
                    content=f"Task failed after {failure_time:.2f} seconds: {str(e)}",
                    task_id=task_id,
                    metadata={
                        "status": "failed",
                        "type": task_info["type"],
                        "error": str(e),
                        "execution_time": failure_time
                    }
                )
            )
            
            raise
            
    def get_task_info(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific task"""
        return self.active_tasks.get(task_id)
        
    def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all active tasks"""
        return {
            task_id: info
            for task_id, info in self.active_tasks.items()
            if info["status"] in ["created", "running"]
        }
        
    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up completed tasks older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        
        for task_id, info in self.active_tasks.items():
            if info["status"] in ["completed", "failed"]:
                completed_at = info.get("completed_at") or info.get("failed_at")
                if completed_at and (now - completed_at).total_seconds() > max_age_hours * 3600:
                    to_remove.append(task_id)
                    
        for task_id in to_remove:
            del self.active_tasks[task_id] 