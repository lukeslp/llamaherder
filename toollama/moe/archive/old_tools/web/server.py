"""
Web server for the MoE system.
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path

from ..core.events import event_manager, Event, EventType, ProgressStage
from ..client import MoEClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MoE System",
    description="Web interface for the Mixture of Experts system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize MoE client
moe_client = MoEClient()

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Request models
class TaskRequest(BaseModel):
    """Task request model"""
    command: str  # e.g., "camina", "belter", "drummer"
    message: str
    task_id: Optional[str] = None

class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    status: str
    content: Optional[Any] = None
    error: Optional[str] = None

# API routes
@app.get("/")
async def get_index():
    """Serve the index.html file."""
    return FileResponse(static_dir / "index.html")

@app.post("/api/task", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create a new task and return its ID."""
    task_id = None
    try:
        # Generate a unique task ID
        task_id = request.task_id or str(uuid.uuid4())
        
        # Initialize progress tracking for this task
        event_manager.init_task(task_id)
        
        # Return immediately so client can establish WebSocket connection
        return TaskResponse(
            task_id=task_id,
            status="started"
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return TaskResponse(
            task_id=task_id or str(uuid.uuid4()),
            status="error",
            error=str(e)
        )

@app.post("/api/task/{task_id}/execute")
async def execute_task(task_id: str, request: TaskRequest):
    """Execute a task after WebSocket connection is established."""
    try:
        # Start task processing
        asyncio.create_task(process_task(task_id, request.command, request.message))
        return {"status": "processing"}
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return {"status": "error", "error": str(e)}

@app.get("/api/task/{task_id}/progress")
async def get_task_progress(task_id: str):
    """Get current progress for a task"""
    progress = event_manager.get_task_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return progress

# WebSocket endpoint
@app.websocket("/ws/task/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """Handle WebSocket connections for task updates."""
    try:
        await websocket.accept()
        active_connections[task_id] = websocket
        
        # Create event callback
        async def event_callback(event: Event):
            try:
                await websocket.send_json(event.dict())
            except Exception as e:
                logger.error(f"Error sending event to WebSocket: {e}")
        
        # Subscribe to task events
        await event_manager.subscribe(task_id, event_callback)
        
        # Send initial task state
        task_state = event_manager.get_task_progress(task_id)
        if task_state:
            await websocket.send_json(task_state)
        
        # Keep connection alive and handle disconnection
        try:
            while True:
                # Wait for client messages (ping/pong)
                await websocket.receive_text()
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for task {task_id}")
        finally:
            # Cleanup
            await event_manager.unsubscribe(task_id, event_callback)
            active_connections.pop(task_id, None)
            
    except Exception as e:
        logger.error(f"WebSocket error for task {task_id}: {e}")
        if task_id in active_connections:
            active_connections.pop(task_id)
            
async def process_task(task_id: str, command: str, message: str):
    """Process a task and send updates through WebSocket."""
    try:
        # Send task started event
        event = Event(
            task_id=task_id,
            event_type=EventType.TASK_STARTED,
            component=command,
            stage=ProgressStage.PLANNING,
            message=f"Processing task: {message}",
            progress=0.0
        )
        await event_manager.emit(event)
        
        # Process command based on type
        try:
            # Send data gathering event
            event = Event(
                task_id=task_id,
                event_type=EventType.DATA_GATHERING,
                component=command,
                stage=ProgressStage.DATA_GATHERING,
                message="Gathering information...",
                progress=0.25
            )
            await event_manager.emit(event)
            
            # Process the command
            if command == "camina":
                response = await moe_client.ask("camina", message)
            elif command == "belter":
                response = await moe_client.ask("belter", message)
            elif command == "drummer":
                response = await moe_client.ask("drummer", message)
            else:
                raise ValueError(f"Unknown command type: {command}")
            
            # Send analysis event
            event = Event(
                task_id=task_id,
                event_type=EventType.ANALYSIS_COMPLETED,
                component=command,
                stage=ProgressStage.ANALYSIS,
                message="Processing response...",
                progress=0.75
            )
            await event_manager.emit(event)
            
            # Send task completed event
            event = Event(
                task_id=task_id,
                event_type=EventType.TASK_COMPLETED,
                component=command,
                stage=ProgressStage.COMPLETE,
                message=response if isinstance(response, str) else str(response),
                progress=1.0
            )
            await event_manager.emit(event)
            
        except Exception as e:
            # Send task failed event
            event = Event(
                task_id=task_id,
                event_type=EventType.TASK_FAILED,
                component=command,
                stage=ProgressStage.FAILED,
                message=f"Task failed: {str(e)}",
                progress=0.0
            )
            await event_manager.emit(event)
            raise
            
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        # This is for unexpected errors in the event handling itself
        try:
            event = Event(
                task_id=task_id,
                event_type=EventType.ERROR,
                component=command,
                stage=ProgressStage.FAILED,
                message=f"Unexpected error: {str(e)}",
                progress=0.0
            )
            await event_manager.emit(event)
        except Exception as e2:
            logger.error(f"Error sending error event: {e2}")

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the web server"""
    import uvicorn
    uvicorn.run(app, host=host, port=port) 