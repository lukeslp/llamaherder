# Code Snippets from toollama/moe/cli.py

File: `toollama/moe/cli.py`  
Language: Python  
Extracted: 2025-06-07 05:10:35  

## Snippet 1
Lines 2-23

```Python
Command-line interface for the MoE system.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

import click

# Support both package and direct imports
try:
    from moe.core.registry import ModelRegistry
    from moe.core.smart_router import SmartRouter
    from moe.core.discovery import ToolDiscovery
    from moe.core.communicator import ModelCommunicator
    from moe.core.task_manager import TaskManager
    from moe.core.tool_capabilities import TOOL_CAPABILITIES
except ImportError:
```

## Snippet 2
Lines 24-32

```Python
# Add parent directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.registry import ModelRegistry
    from core.smart_router import SmartRouter
    from core.discovery import ToolDiscovery
    from core.communicator import ModelCommunicator
    from core.task_manager import TaskManager
    from core.tool_capabilities import TOOL_CAPABILITIES
```

## Snippet 3
Lines 33-47

```Python
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_CONFIG_DIR = Path(__file__).parent / "config"
DEFAULT_MODELS_DIR = Path(__file__).parent / "models"
DEFAULT_TOOLS_DIR = Path(__file__).parent / "tools"
```

## Snippet 4
Lines 51-58

```Python
def __init__(
        self,
        config_dir: Path = DEFAULT_CONFIG_DIR,
        models_dir: Path = DEFAULT_MODELS_DIR,
        tools_dir: Path = DEFAULT_TOOLS_DIR,
        debug: bool = False
    ):
        """Initialize the MoE system"""
```

## Snippet 5
Lines 59-89

```Python
if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")

        self.config_dir = config_dir
        self.models_dir = models_dir
        self.tools_dir = tools_dir

        logger.info(f"Initializing MoE system with:")
        logger.info(f"  Config dir: {config_dir}")
        logger.info(f"  Models dir: {models_dir}")
        logger.info(f"  Tools dir: {tools_dir}")

        # Load configuration
        self.registry = ModelRegistry(config_dir / "models.yaml")
        self.router = SmartRouter(self.registry)  # Use SmartRouter instead of ToolRouter
        self.discovery = ToolDiscovery(str(tools_dir), self.router, self.registry)
        self.task_manager = TaskManager()

        # Initialize model endpoints
        self.model_endpoints = {
            'camina': os.getenv('CAMINA_ENDPOINT', 'http://localhost:6000/camina'),
            'property_belter': os.getenv('PROPERTY_BELTER_ENDPOINT', 'http://localhost:6001/belter'),
            'knowledge_belter': os.getenv('KNOWLEDGE_BELTER_ENDPOINT', 'http://localhost:6002/belter'),
            'location_drummer': os.getenv('LOCATION_DRUMMER_ENDPOINT', 'http://localhost:6003/drummer')
        }

        self.communicator = ModelCommunicator({
            'model_endpoints': self.model_endpoints
        })
```

## Snippet 6
Lines 90-98

```Python
async def start(self):
        """Start the MoE system"""
        logger.info("Starting MoE system...")

        try:
            # Discover available tools
            self.discovery.discover_tools()

            # Register tool capabilities
```

## Snippet 7
Lines 105-108

```Python
logger.info(f"Registered {len(TOOL_CAPABILITIES)} tool capabilities")

            return self
```

## Snippet 8
Lines 109-112

```Python
except Exception as e:
            logger.error(f"Error starting MoE system: {e}")
            raise
```

## Snippet 9
Lines 113-121

```Python
async def stop(self):
        """Stop the MoE system"""
        logger.info("Stopping MoE system...")
        try:
            await self.communicator.close()
        except Exception as e:
            logger.error(f"Error stopping MoE system: {e}")
            raise
```

## Snippet 10
Lines 122-140

```Python
async def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a natural language query"""
        logger.info(f"Executing query: {query}")

        try:
            # Create task
            task = await self.task_manager.create_task(
                task_type='query',
                metadata={
                    'message_type': 'query',
                    'content': query
                }
            )

            # Route query to appropriate tool
            tool_response = await self.router.execute_query(query)
            logger.info(f"Routed to tool: {tool_response.tool_id}")

            # For now, return the tool response directly
```

## Snippet 11
Lines 141-148

```Python
# Later we'll add Camina for orchestration
            return {
                'status': 'success',
                'task_id': task.task_id,
                'tool_id': tool_response.tool_id,
                'result': tool_response.result
            }
```

## Snippet 12
Lines 149-153

```Python
except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                'status': 'error',
                'error': str(e),
```

## Snippet 13
Lines 158-161

```Python
def cli():
    """ToolLama MoE - Mixture of Experts System"""
    pass
```

## Snippet 14
Lines 167-170

```Python
def start(config_dir: Optional[str], models_dir: Optional[str], tools_dir: Optional[str], debug: bool):
    """Start the MoE system"""
    try:
        system = MoESystem(
```

## Snippet 15
Lines 177-180

```Python
async def run():
            await system.start()
            try:
                # Keep system running
```

## Snippet 16
Lines 188-191

```Python
except Exception as e:
        logger.error(f"Error starting system: {e}")
        sys.exit(1)
```

## Snippet 17
Lines 198-208

```Python
def chat(
    query: str,
    config_dir: Optional[str],
    models_dir: Optional[str],
    tools_dir: Optional[str],
    debug: bool
):
    """Chat with the MoE system using natural language"""
    try:
        # Initialize system
        system = MoESystem(
```

## Snippet 18
Lines 215-224

```Python
async def run():
            await system.start()
            try:
                response = await system.execute_query(query)
                print(json.dumps(response, indent=2))
            finally:
                await system.stop()

        asyncio.run(run())
```

## Snippet 19
Lines 225-228

```Python
except Exception as e:
        logger.error(f"Error in chat: {e}")
        sys.exit(1)
```

