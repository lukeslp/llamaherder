# Code Snippets from toollama/moe/core/events.py

File: `toollama/moe/core/events.py`  
Language: Python  
Extracted: 2025-06-07 05:11:40  

## Snippet 1
Lines 2-15

```Python
Event system for real-time feedback in the MoE system.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List, Set, Callable, Awaitable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from dataclasses import dataclass

logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 16-38

```Python
class EventType(str, Enum):
    """Types of events that can be emitted"""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    BELTER_ASSIGNED = "belter_assigned"
    BELTER_STARTED = "belter_started"
    BELTER_COMPLETED = "belter_completed"
    BELTER_FAILED = "belter_failed"
    DRUMMER_ASSIGNED = "drummer_assigned"
    DRUMMER_STARTED = "drummer_started"
    DRUMMER_COMPLETED = "drummer_completed"
    DRUMMER_FAILED = "drummer_failed"
    DATA_GATHERING = "data_gathering"
    DATA_PROCESSING = "data_processing"
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    SYNTHESIS_STARTED = "synthesis_started"
    SYNTHESIS_COMPLETED = "synthesis_completed"
    PROGRESS_UPDATE = "progress_update"
    WARNING = "warning"
    ERROR = "error"
```

## Snippet 3
Lines 39-48

```Python
class ProgressStage(str, Enum):
    """Stages of task execution"""
    PLANNING = "planning"
    DATA_GATHERING = "data_gathering"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    REVIEW = "review"
    COMPLETE = "complete"
    FAILED = "failed"
```

## Snippet 4
Lines 50-60

```Python
"""Event model for real-time updates"""
    event_type: EventType
    task_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    component: str  # e.g., "camina", "property_belter", "location_drummer"
    stage: ProgressStage
    message: str
    details: Optional[Dict[str, Any]] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    estimated_time_remaining: Optional[str] = None
```

## Snippet 5
Lines 61-66

```Python
class Config:
        """Pydantic model configuration"""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
```

## Snippet 6
Lines 67-72

```Python
def dict(self, *args, **kwargs):
        """Convert to dictionary with ISO formatted dates"""
        d = super().dict(*args, **kwargs)
        d['timestamp'] = self.timestamp.isoformat()
        return d
```

## Snippet 7
Lines 76-80

```Python
def __init__(self):
        """Initialize the event manager"""
        self.subscribers: Dict[str, Set[Callable[[Event], Awaitable[None]]]] = {}
        self.task_progress: Dict[str, Dict[str, Any]] = {}
```

## Snippet 8
Lines 83-87

```Python
Initialize tracking for a new task.

        Args:
            task_id: Task identifier
        """
```

## Snippet 9
Lines 88-96

```Python
if task_id not in self.task_progress:
            now = datetime.utcnow()
            self.task_progress[task_id] = {
                "stage": ProgressStage.PLANNING,
                "started_at": now.isoformat(),
                "last_update": now.isoformat(),
                "components": {},
                "overall_progress": 0.0
            }
```

## Snippet 10
Lines 101-106

```Python
Get current state for a task.

        Args:
            task_id: Task identifier

        Returns:
```

## Snippet 11
Lines 111-116

```Python
async def subscribe(
        self,
        task_id: str,
        callback: Callable[[Event], Awaitable[None]]
    ) -> None:
        """
```

## Snippet 12
Lines 117-120

```Python
Subscribe to events for a specific task.

        Args:
            task_id: Task identifier
```

## Snippet 13
Lines 123-125

```Python
if task_id not in self.subscribers:
            self.subscribers[task_id] = set()
        self.subscribers[task_id].add(callback)
```

## Snippet 14
Lines 128-137

```Python
async def unsubscribe(
        self,
        task_id: str,
        callback: Callable[[Event], Awaitable[None]]
    ) -> None:
        """
        Unsubscribe from task events.

        Args:
            task_id: Task identifier
```

## Snippet 15
Lines 146-153

```Python
async def emit(self, event: Event) -> None:
        """
        Emit an event and update task progress.

        Args:
            event: Event to emit
        """
        # Update task progress
```

## Snippet 16
Lines 154-160

```Python
if event.task_id not in self.task_progress:
            self.init_task(event.task_id)

        progress = self.task_progress[event.task_id]
        progress["last_update"] = event.timestamp.isoformat()
        progress["stage"] = event.stage
```

## Snippet 17
Lines 161-172

```Python
if event.component not in progress["components"]:
            progress["components"][event.component] = {
                "status": event.event_type,
                "progress": event.progress or 0.0
            }
        else:
            progress["components"][event.component].update({
                "status": event.event_type,
                "progress": event.progress or progress["components"][event.component]["progress"]
            })

        # Calculate overall progress
```

## Snippet 18
Lines 179-184

```Python
for callback in self.subscribers[event.task_id]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
```

## Snippet 19
Lines 187-192

```Python
Get current progress for a task.

        Args:
            task_id: Task identifier

        Returns:
```

## Snippet 20
Lines 201-207

```Python
class ObservationEvent:
    """Event containing observer commentary and metadata."""
    timestamp: datetime
    content: str
    task_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

## Snippet 21
Lines 208-216

```Python
def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "task_id": self.task_id,
            "metadata": self.metadata or {}
        }
```

## Snippet 22
Lines 220-225

```Python
def __init__(self):
        self._subscribers: Dict[str, set[Callable[[Any], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None
```

## Snippet 23
Lines 228-234

```Python
if not self._running:
            logger.warning("EventBus is not running. Starting now...")
            await self.start()

        await self._queue.put((event_type, data))
        logger.debug(f"Published event: {event_type}")
```

## Snippet 24
Lines 237-239

```Python
if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(callback)
```

## Snippet 25
Lines 250-256

```Python
if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")
```

## Snippet 26
Lines 259-262

```Python
if not self._running:
            return

        self._running = False
```

## Snippet 27
Lines 263-270

```Python
if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped")
```

## Snippet 28
Lines 273-275

```Python
while self._running:
            try:
                event_type, data = await self._queue.get()
```

## Snippet 29
Lines 277-281

```Python
for callback in self._subscribers[event_type]:
                        try:
                            await callback(data)
                        except Exception as e:
                            logger.error(f"Error in event handler: {e}", exc_info=True)
```

## Snippet 30
Lines 283-287

```Python
except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
```

