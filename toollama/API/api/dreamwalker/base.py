"""
Base Dreamwalker class for implementing complex multi-step AI workflows
"""

import time
import uuid
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BaseDreamwalker(ABC):
    """
    Abstract base class for all Dreamwalker workflows.
    
    Dreamwalker workflows are complex multi-step AI processes that can involve
    multiple models, tools, and data sources to accomplish sophisticated tasks.
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        """
        Initialize a new Dreamwalker workflow.
        
        Args:
            workflow_id: Optional unique identifier for this workflow instance.
                         If not provided, a UUID will be generated.
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.start_time = time.time()
        self.end_time = None
        self.progress = 0  # Progress from 0-100
        self.status = "initialized"  # initialized, running, completed, failed, cancelled
        self.results = {}
        self.error = None
        self.steps_completed = []
        self.steps_remaining = []
        self.metadata = {}
        self.step_description = None  # Current step description
        
        logger.info(f"Initialized {self.__class__.__name__} workflow with ID: {self.workflow_id}")
    
    @abstractmethod
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the workflow with the given query and parameters.
        
        Args:
            query: The user query or input to process
            **kwargs: Additional parameters specific to the workflow
            
        Returns:
            A dictionary containing the results of the workflow
        """
        pass
    
    def update_progress(self, progress: int, status: Optional[str] = None, step_description: Optional[str] = None):
        """
        Update the progress of the workflow.
        
        Args:
            progress: Progress value from 0-100
            status: Optional status update
            step_description: Optional description of the current step
        """
        self.progress = min(max(progress, 0), 100)  # Ensure progress is between 0-100
        
        if status:
            self.status = status
            
        if step_description:
            self.step_description = step_description  # Update the current step description
            self.steps_completed.append({
                "description": step_description,
                "timestamp": time.time()
            })
            
        logger.info(f"Workflow {self.workflow_id} progress: {self.progress}% - {status or self.status} - {step_description or 'No description'}")
    
    def complete(self, results: Dict[str, Any]):
        """
        Mark the workflow as completed with the given results.
        
        Args:
            results: The final results of the workflow
        """
        self.end_time = time.time()
        self.progress = 100
        self.status = "completed"
        self.results = results
        
        duration = self.end_time - self.start_time
        logger.info(f"Workflow {self.workflow_id} completed in {duration:.2f} seconds")
        
        return self.get_status()
    
    def fail(self, error: str):
        """
        Mark the workflow as failed with the given error.
        
        Args:
            error: Description of the error that caused the failure
        """
        self.end_time = time.time()
        self.status = "failed"
        self.error = error
        
        duration = self.end_time - self.start_time
        logger.error(f"Workflow {self.workflow_id} failed after {duration:.2f} seconds: {error}")
        
        return self.get_status()
    
    def cancel(self):
        """Cancel the workflow execution."""
        self.end_time = time.time()
        self.status = "cancelled"
        
        duration = self.end_time - self.start_time
        logger.info(f"Workflow {self.workflow_id} cancelled after {duration:.2f} seconds")
        
        return self.get_status()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the workflow.
        
        Returns:
            A dictionary containing the current status and progress information
        """
        duration = (self.end_time or time.time()) - self.start_time
        
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.__class__.__name__,
            "status": self.status,
            "progress": self.progress,
            "step_description": self.step_description,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": duration,
            "steps_completed": self.steps_completed,
            "steps_remaining": self.steps_remaining,
            "error": self.error,
            "results": self.results,
            "metadata": self.metadata
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the workflow to a dictionary for serialization.
        
        Returns:
            A dictionary representation of the workflow
        """
        return self.get_status()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseDreamwalker':
        """
        Create a workflow instance from a dictionary.
        
        Args:
            data: Dictionary containing workflow data
            
        Returns:
            A new workflow instance with the restored state
        """
        workflow = cls(workflow_id=data.get("workflow_id"))
        workflow.start_time = data.get("start_time", time.time())
        workflow.end_time = data.get("end_time")
        workflow.progress = data.get("progress", 0)
        workflow.status = data.get("status", "initialized")
        workflow.step_description = data.get("step_description")
        workflow.results = data.get("results", {})
        workflow.error = data.get("error")
        workflow.steps_completed = data.get("steps_completed", [])
        workflow.steps_remaining = data.get("steps_remaining", [])
        workflow.metadata = data.get("metadata", {})
        
        return workflow 