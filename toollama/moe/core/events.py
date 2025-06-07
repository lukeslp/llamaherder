"""
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

class ProgressStage(str, Enum):
    """Stages of task execution"""
    PLANNING = "planning"
    DATA_GATHERING = "data_gathering"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    REVIEW = "review"
    COMPLETE = "complete"
    FAILED = "failed"

class Event(BaseModel):
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

    class Config:
        """Pydantic model configuration"""
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        
    def dict(self, *args, **kwargs):
        """Convert to dictionary with ISO formatted dates"""
        d = super().dict(*args, **kwargs)
        d['timestamp'] = self.timestamp.isoformat()
        return d

class EventManager:
    """Manages event subscriptions and broadcasting"""
    
    def __init__(self):
        """Initialize the event manager"""
        self.subscribers: Dict[str, Set[Callable[[Event], Awaitable[None]]]] = {}
        self.task_progress: Dict[str, Dict[str, Any]] = {}
        
    def init_task(self, task_id: str) -> None:
        """
        Initialize tracking for a new task.
        
        Args:
            task_id: Task identifier
        """
        if task_id not in self.task_progress:
            now = datetime.utcnow()
            self.task_progress[task_id] = {
                "stage": ProgressStage.PLANNING,
                "started_at": now.isoformat(),
                "last_update": now.isoformat(),
                "components": {},
                "overall_progress": 0.0
            }
            logger.debug(f"Initialized tracking for task {task_id}")
            
    def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current state for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task state information or None if task not found
        """
        return self.task_progress.get(task_id)
        
    async def subscribe(
        self,
        task_id: str,
        callback: Callable[[Event], Awaitable[None]]
    ) -> None:
        """
        Subscribe to events for a specific task.
        
        Args:
            task_id: Task identifier
            callback: Async callback function to receive events
        """
        if task_id not in self.subscribers:
            self.subscribers[task_id] = set()
        self.subscribers[task_id].add(callback)
        logger.debug(f"Added subscriber for task {task_id}")
        
    async def unsubscribe(
        self,
        task_id: str,
        callback: Callable[[Event], Awaitable[None]]
    ) -> None:
        """
        Unsubscribe from task events.
        
        Args:
            task_id: Task identifier
            callback: Callback function to remove
        """
        if task_id in self.subscribers:
            self.subscribers[task_id].discard(callback)
            if not self.subscribers[task_id]:
                del self.subscribers[task_id]
        logger.debug(f"Removed subscriber for task {task_id}")
        
    async def emit(self, event: Event) -> None:
        """
        Emit an event and update task progress.
        
        Args:
            event: Event to emit
        """
        # Update task progress
        if event.task_id not in self.task_progress:
            self.init_task(event.task_id)
            
        progress = self.task_progress[event.task_id]
        progress["last_update"] = event.timestamp.isoformat()
        progress["stage"] = event.stage
        
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
        if progress["components"]:
            total = sum(comp["progress"] for comp in progress["components"].values())
            progress["overall_progress"] = total / len(progress["components"])
            
        # Notify subscribers
        if event.task_id in self.subscribers:
            for callback in self.subscribers[event.task_id]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
                    
    def get_task_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current progress for a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Progress information or None if task not found
        """
        return self.task_progress.get(task_id)

# Global event manager instance
event_manager = EventManager()

@dataclass
class ObservationEvent:
    """Event containing observer commentary and metadata."""
    timestamp: datetime
    content: str
    task_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "task_id": self.task_id,
            "metadata": self.metadata or {}
        }

class EventBus:
    """Central event bus for system-wide communication."""
    
    def __init__(self):
        self._subscribers: Dict[str, set[Callable[[Any], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event to all subscribers."""
        if not self._running:
            logger.warning("EventBus is not running. Starting now...")
            await self.start()
            
        await self._queue.put((event_type, data))
        logger.debug(f"Published event: {event_type}")
        
    async def subscribe(self, event_type: str, callback: Callable[[Any], Awaitable[None]]) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(callback)
        logger.debug(f"New subscriber added for event type: {event_type}")
        
    async def unsubscribe(self, event_type: str, callback: Callable[[Any], Awaitable[None]]) -> None:
        """Unsubscribe from events of a specific type."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
            logger.debug(f"Subscriber removed for event type: {event_type}")
        
    async def start(self) -> None:
        """Start processing events."""
        if self._running:
            return
            
        self._running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("EventBus started")
        
    async def stop(self) -> None:
        """Stop processing events."""
        if not self._running:
            return
            
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped")
        
    async def _process_events(self) -> None:
        """Process events from the queue."""
        while self._running:
            try:
                event_type, data = await self._queue.get()
                if event_type in self._subscribers:
                    for callback in self._subscribers[event_type]:
                        try:
                            await callback(data)
                        except Exception as e:
                            logger.error(f"Error in event handler: {e}", exc_info=True)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)

# Global event bus instance
event_bus = EventBus() 