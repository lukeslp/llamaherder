"""
FastAPI routes for the Dreamwalker framework.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.dreamwalker import BaseDreamwalker, SwarmDreamwalker

# Create router
router = APIRouter(prefix="/dreamwalker", tags=["dreamwalker"])

# Configure CORS
router.add_middleware(
    CORSMiddleware,
    allow_origins=["https://actuallyusefulai.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# In-memory storage for active workflows
active_workflows: Dict[str, BaseDreamwalker] = {}

# Request and response models
class DreamwalkerRequest(BaseModel):
    query: str = Field(..., description="The query to process")
    workflow_type: str = Field("swarm", description="Type of workflow to execute")
    model: Optional[str] = Field(None, description="Model to use for the workflow")
    
class DreamwalkerResponse(BaseModel):
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    status: str = Field(..., description="Current status of the workflow")
    progress: int = Field(..., description="Progress percentage (0-100)")
    step_description: Optional[str] = Field(None, description="Description of the current step")
    
class DreamwalkerStatusResponse(BaseModel):
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    status: str = Field(..., description="Current status of the workflow")
    progress: int = Field(..., description="Progress percentage (0-100)")
    step_description: Optional[str] = Field(None, description="Description of the current step")
    start_time: Optional[float] = Field(None, description="Timestamp when the workflow started")
    end_time: Optional[float] = Field(None, description="Timestamp when the workflow completed")
    steps_completed: Optional[List[str]] = Field(None, description="List of completed steps")
    steps_remaining: Optional[List[str]] = Field(None, description="List of remaining steps")
    results: Optional[Dict[str, Any]] = Field(None, description="Results of the workflow if completed")
    error: Optional[str] = Field(None, description="Error message if the workflow failed")
    
class DreamwalkerResultResponse(BaseModel):
    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    query: str = Field(..., description="Original query")
    variant_queries: List[str] = Field(..., description="Variant queries used for search")
    search_results_count: int = Field(..., description="Number of search results processed")
    urls_extracted: int = Field(..., description="Number of URLs extracted from search results")
    summary: str = Field(..., description="Comprehensive summary of search results")

async def _execute_workflow(workflow_id: str, query: str, workflow_type: str, model: Optional[str] = None):
    """
    Execute a workflow in the background.
    
    Args:
        workflow_id: Unique identifier for the workflow
        query: The query to process
        workflow_type: Type of workflow to execute
        model: Model to use for the workflow
    """
    try:
        # Get the workflow instance
        workflow = active_workflows.get(workflow_id)
        if not workflow:
            return
        
        # Execute the workflow
        await workflow.execute(query, model=model)
    except Exception as e:
        # If an error occurs, update the workflow status
        if workflow_id in active_workflows:
            active_workflows[workflow_id].fail(str(e))

@router.post("/search", response_model=DreamwalkerResponse)
async def start_search_workflow(
    request: DreamwalkerRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new search workflow.
    
    This endpoint initiates a new search workflow based on the provided query.
    The workflow runs asynchronously in the background, and the response includes
    a workflow_id that can be used to check the status and retrieve results.
    """
    # Generate a unique workflow ID
    workflow_id = str(uuid.uuid4())
    
    # Create the appropriate workflow instance
    if request.workflow_type.lower() == "swarm":
        workflow = SwarmDreamwalker(workflow_id=workflow_id, model=request.model)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported workflow type: {request.workflow_type}")
    
    # Store the workflow in memory
    active_workflows[workflow_id] = workflow
    
    # Start the workflow in the background
    background_tasks.add_task(_execute_workflow, workflow_id, request.query, request.workflow_type, request.model)
    
    # Return the initial response
    return {
        "workflow_id": workflow_id,
        "status": workflow.status,
        "progress": workflow.progress,
        "step_description": workflow.step_description
    }

@router.get("/status/{workflow_id}", response_model=DreamwalkerStatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get the status of a workflow.
    
    This endpoint returns the current status of a workflow, including progress,
    step description, and results if the workflow has completed.
    """
    # Check if the workflow exists
    if workflow_id not in active_workflows:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    
    # Get the workflow
    workflow = active_workflows[workflow_id]
    
    # Return the workflow status
    return workflow.to_dict()

@router.get("/result/{workflow_id}", response_model=DreamwalkerResultResponse)
async def get_workflow_result(workflow_id: str):
    """
    Get the result of a completed workflow.
    
    This endpoint returns the result of a completed workflow. If the workflow
    is still running or has failed, an appropriate error is returned.
    """
    # Check if the workflow exists
    if workflow_id not in active_workflows:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    
    # Get the workflow
    workflow = active_workflows[workflow_id]
    
    # Check if the workflow has completed
    if workflow.status != "completed":
        if workflow.status == "failed":
            raise HTTPException(status_code=400, detail=f"Workflow failed: {workflow.error}")
        else:
            raise HTTPException(status_code=400, detail=f"Workflow is still running (status: {workflow.status})")
    
    # Return the workflow result
    return workflow.results

@router.delete("/cancel/{workflow_id}", response_model=DreamwalkerStatusResponse)
async def cancel_workflow(workflow_id: str):
    """
    Cancel a running workflow.
    
    This endpoint cancels a running workflow and returns its final status.
    """
    # Check if the workflow exists
    if workflow_id not in active_workflows:
        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
    
    # Get the workflow
    workflow = active_workflows[workflow_id]
    
    # Cancel the workflow if it's still running
    if workflow.status == "running":
        workflow.cancel("Cancelled by user")
    
    # Return the workflow status
    return workflow.to_dict()

@router.get("/list", response_model=List[DreamwalkerStatusResponse])
async def list_workflows(
    status: Optional[str] = Query(None, description="Filter workflows by status"),
    limit: int = Query(10, description="Maximum number of workflows to return")
):
    """
    List active workflows.
    
    This endpoint returns a list of active workflows, optionally filtered by status.
    """
    # Filter workflows by status if provided
    if status:
        filtered_workflows = [w for w in active_workflows.values() if w.status == status]
    else:
        filtered_workflows = list(active_workflows.values())
    
    # Sort workflows by start time (newest first)
    sorted_workflows = sorted(filtered_workflows, key=lambda w: w.start_time or 0, reverse=True)
    
    # Limit the number of workflows returned
    limited_workflows = sorted_workflows[:limit]
    
    # Return the workflow statuses
    return [w.to_dict() for w in limited_workflows]

@router.delete("/cleanup", response_model=Dict[str, Any])
async def cleanup_workflows(
    status: Optional[str] = Query("completed", description="Status of workflows to clean up"),
    age_hours: int = Query(24, description="Age in hours of workflows to clean up")
):
    """
    Clean up old workflows.
    
    This endpoint removes old workflows from memory based on their status and age.
    """
    import time
    
    # Calculate the cutoff time
    cutoff_time = time.time() - (age_hours * 3600)
    
    # Find workflows to remove
    workflows_to_remove = []
    for workflow_id, workflow in active_workflows.items():
        if workflow.status == status and workflow.end_time and workflow.end_time < cutoff_time:
            workflows_to_remove.append(workflow_id)
    
    # Remove the workflows
    for workflow_id in workflows_to_remove:
        del active_workflows[workflow_id]
    
    # Return the result
    return {
        "status": "success",
        "removed_count": len(workflows_to_remove),
        "remaining_count": len(active_workflows)
    } 