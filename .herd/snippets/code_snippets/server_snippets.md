# Code Snippets from toollama/moe/archive/old_tools/web/server.py

File: `toollama/moe/archive/old_tools/web/server.py`  
Language: Python  
Extracted: 2025-06-07 05:12:18  

## Snippet 1
Lines 2-26

```Python
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
```

## Snippet 2
Lines 29-50

```Python
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
```

## Snippet 3
Lines 51-56

```Python
class TaskRequest(BaseModel):
    """Task request model"""
    command: str  # e.g., "camina", "belter", "drummer"
    message: str
    task_id: Optional[str] = None
```

## Snippet 4
Lines 57-64

```Python
class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    status: str
    content: Optional[Any] = None
    error: Optional[str] = None

# API routes
```

## Snippet 5
Lines 66-69

```Python
async def get_index():
    """Serve the index.html file."""
    return FileResponse(static_dir / "index.html")
```

## Snippet 6
Lines 71-77

```Python
async def create_task(request: TaskRequest):
    """Create a new task and return its ID."""
    task_id = None
    try:
        # Generate a unique task ID
        task_id = request.task_id or str(uuid.uuid4())
```

## Snippet 7
Lines 78-85

```Python
# Initialize progress tracking for this task
        event_manager.init_task(task_id)

        # Return immediately so client can establish WebSocket connection
        return TaskResponse(
            task_id=task_id,
            status="started"
        )
```

## Snippet 8
Lines 86-93

```Python
except Exception as e:
        logger.error(f"Error creating task: {e}")
        return TaskResponse(
            task_id=task_id or str(uuid.uuid4()),
            status="error",
            error=str(e)
        )
```

## Snippet 9
Lines 95-104

```Python
async def execute_task(task_id: str, request: TaskRequest):
    """Execute a task after WebSocket connection is established."""
    try:
        # Start task processing
        asyncio.create_task(process_task(task_id, request.command, request.message))
        return {"status": "processing"}
    except Exception as e:
        logger.error(f"Error executing task: {e}")
        return {"status": "error", "error": str(e)}
```

## Snippet 10
Lines 109-112

```Python
if not progress:
        raise HTTPException(status_code=404, detail="Task not found")
    return progress
```

## Snippet 11
Lines 116-121

```Python
"""Handle WebSocket connections for task updates."""
    try:
        await websocket.accept()
        active_connections[task_id] = websocket

        # Create event callback
```

## Snippet 12
Lines 122-132

```Python
async def event_callback(event: Event):
            try:
                await websocket.send_json(event.dict())
            except Exception as e:
                logger.error(f"Error sending event to WebSocket: {e}")

        # Subscribe to task events
        await event_manager.subscribe(task_id, event_callback)

        # Send initial task state
        task_state = event_manager.get_task_progress(task_id)
```

## Snippet 13
Lines 133-137

```Python
if task_state:
            await websocket.send_json(task_state)

        # Keep connection alive and handle disconnection
        try:
```

## Snippet 14
Lines 153-180

```Python
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
```

## Snippet 15
Lines 185-206

```Python
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
```

## Snippet 16
Lines 212-224

```Python
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
```

## Snippet 17
Lines 227-240

```Python
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
```

## Snippet 18
Lines 241-244

```Python
def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the web server"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)
```

