"""
Client for interacting with the MoE system.
"""

import sys
import json
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Callable, Awaitable
import httpx
from pydantic import BaseModel
from datetime import datetime

from .core.events import event_bus, ObservationEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class MoEClient:
    """Client for interacting with the MoE system"""
    
    def __init__(
        self,
        base_url: str = "http://localhost",
        camina_port: int = 6000,
        belter_port: int = 6001,
        drummer_port: int = 6002,
        observer_port: int = 6003,
        observation_callback: Optional[Callable[[ObservationEvent], Awaitable[None]]] = None
    ):
        """Initialize the MoE client"""
        self.endpoints = {
            "camina": f"{base_url}:{camina_port}/chat",
            "belter": f"{base_url}:{belter_port}/chat",
            "drummer": f"{base_url}:{drummer_port}/chat",
            "observer": f"{base_url}:{observer_port}/chat"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.current_task_id = None
        self.observation_callback = observation_callback
        
        # Start event bus and subscribe to observations
        asyncio.create_task(self._setup_observation_handling())
        
    async def _setup_observation_handling(self):
        """Set up observation event handling"""
        await event_bus.start()
        await event_bus.subscribe("observation", self._handle_observation)
        
    async def _handle_observation(self, event: ObservationEvent):
        """Handle incoming observation events"""
        if event.task_id == self.current_task_id:
            if self.observation_callback:
                await self.observation_callback(event)
            else:
                # Default behavior: print to console
                print(f"\n[Observer] {event.content}")
                if event.metadata:
                    print(f"[Metadata] {json.dumps(event.metadata, indent=2)}")
                    
    async def ask(
        self,
        target: str,
        content: str,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generic ask method for all agent types
        """
        if target not in self.endpoints:
            raise ValueError(f"Invalid target: {target}. Valid targets are: {list(self.endpoints.keys())}")
            
        self.current_task_id = task_id or str(uuid.uuid4())
        return await self._send_message(self.endpoints[target], content, self.current_task_id)
        
    async def _send_message(self, endpoint: str, content: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to a server endpoint"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"Sending request to {endpoint}")
                response = await client.post(
                    endpoint,
                    json={
                        "content": content,
                        "task_id": task_id
                    }
                )
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Received response: {data}")
                
                # Notify observer of message completion
                await event_bus.publish(
                    "observation",
                    ObservationEvent(
                        timestamp=datetime.now(),
                        content=f"Message processed by {endpoint.split('/')[-2]}",
                        task_id=task_id,
                        metadata={"endpoint": endpoint, "status": "completed"}
                    )
                )
                
                return data
        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with {endpoint}: {e}")
            # Notify observer of error
            await event_bus.publish(
                "observation",
                ObservationEvent(
                    timestamp=datetime.now(),
                    content=f"Error communicating with {endpoint.split('/')[-2]}: {str(e)}",
                    task_id=task_id,
                    metadata={"endpoint": endpoint, "status": "error", "error": str(e)}
                )
            )
            raise Exception(f"Failed to communicate with server: {e}")
        except Exception as e:
            logger.error(f"Error sending message to {endpoint}: {e}")
            # Notify observer of error
            await event_bus.publish(
                "observation",
                ObservationEvent(
                    timestamp=datetime.now(),
                    content=f"Unexpected error in {endpoint.split('/')[-2]}: {str(e)}",
                    task_id=task_id,
                    metadata={"endpoint": endpoint, "status": "error", "error": str(e)}
                )
            )
            raise
                
    async def ask_camina(self, content: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to Camina (primary agent)"""
        return await self.ask("camina", content, task_id)
        
    async def ask_belter(self, content: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to a Belter (domain specialist)"""
        return await self.ask("belter", content, task_id)
        
    async def ask_drummer(self, content: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to a Drummer (task executor)"""
        return await self.ask("drummer", content, task_id)
        
    async def ask_observer(self, content: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to the Observer (system monitor)"""
        return await self.ask("observer", content, task_id)
        
    async def close(self):
        """Clean up resources"""
        await event_bus.stop()

async def main():
    """Interactive client demo"""
    client = MoEClient()
    
    print("\nMoE System Interactive Client")
    print("============================")
    print("Available commands:")
    print("  camina: Ask the primary agent")
    print("  belter: Ask a domain specialist")
    print("  drummer: Ask a task executor")
    print("  observer: Ask the system monitor")
    print("  quit: Exit the client")
    print("\nEnter your command followed by your message.")
    print("Example: camina What is the current task status?\n")
    
    while True:
        try:
            # Get input
            user_input = input("> ").strip()
            if not user_input:
                continue
                
            if user_input.lower() == "quit":
                break
                
            # Parse command and message
            try:
                command, message = user_input.split(" ", 1)
            except ValueError:
                print("Error: Please provide both a command and a message")
                continue
                
            command = command.lower()
            
            # Send to appropriate endpoint
            try:
                if command == "camina":
                    response = await client.ask_camina(message)
                elif command == "belter":
                    response = await client.ask_belter(message)
                elif command == "drummer":
                    response = await client.ask_drummer(message)
                elif command == "observer":
                    response = await client.ask_observer(message)
                else:
                    print(f"Unknown command: {command}")
                    continue
                    
                # Pretty print response
                print("\nResponse:")
                print("=========")
                
                # Handle different response types
                if isinstance(response, dict):
                    if "error" in response:
                        print(f"Error: {response['error']}")
                    elif "content" in response:
                        content = response["content"]
                        if isinstance(content, (dict, list)):
                            print(json.dumps(content, indent=2))
                        else:
                            print(content)
                    else:
                        print(json.dumps(response, indent=2))
                else:
                    print(response)
                print()
                    
            except Exception as e:
                print(f"Error: {str(e)}")
                
        except KeyboardInterrupt:
            break
            
    print("\nGoodbye!")

if __name__ == "__main__":
    asyncio.run(main()) 