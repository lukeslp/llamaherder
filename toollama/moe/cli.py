"""
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
    # Add parent directory to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.registry import ModelRegistry
    from core.smart_router import SmartRouter
    from core.discovery import ToolDiscovery
    from core.communicator import ModelCommunicator
    from core.task_manager import TaskManager
    from core.tool_capabilities import TOOL_CAPABILITIES

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

class MoESystem:
    """Main MoE system class with natural language understanding"""
    
    def __init__(
        self,
        config_dir: Path = DEFAULT_CONFIG_DIR,
        models_dir: Path = DEFAULT_MODELS_DIR,
        tools_dir: Path = DEFAULT_TOOLS_DIR,
        debug: bool = False
    ):
        """Initialize the MoE system"""
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
        
    async def start(self):
        """Start the MoE system"""
        logger.info("Starting MoE system...")
        
        try:
            # Discover available tools
            self.discovery.discover_tools()
            
            # Register tool capabilities
            for tool_id, capability in TOOL_CAPABILITIES.items():
                self.router.register_capability(tool_id, capability)
            
            # Log discovered components
            logger.info(f"Discovered {len(self.discovery.discovered_tools)} tools")
            logger.info(f"Available categories: {', '.join(self.discovery.get_categories())}")
            logger.info(f"Registered {len(TOOL_CAPABILITIES)} tool capabilities")
            
            return self
            
        except Exception as e:
            logger.error(f"Error starting MoE system: {e}")
            raise
        
    async def stop(self):
        """Stop the MoE system"""
        logger.info("Stopping MoE system...")
        try:
            await self.communicator.close()
        except Exception as e:
            logger.error(f"Error stopping MoE system: {e}")
            raise
        
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
            # Later we'll add Camina for orchestration
            return {
                'status': 'success',
                'task_id': task.task_id,
                'tool_id': tool_response.tool_id,
                'result': tool_response.result
            }
            
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'task_id': task.task_id if 'task' in locals() else None
            }

@click.group()
def cli():
    """ToolLama MoE - Mixture of Experts System"""
    pass

@cli.command()
@click.option('--config-dir', type=click.Path(exists=True), help='Configuration directory')
@click.option('--models-dir', type=click.Path(exists=True), help='Models directory')
@click.option('--tools-dir', type=click.Path(exists=True), help='Tools directory')
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
def start(config_dir: Optional[str], models_dir: Optional[str], tools_dir: Optional[str], debug: bool):
    """Start the MoE system"""
    try:
        system = MoESystem(
            config_dir=Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR,
            models_dir=Path(models_dir) if models_dir else DEFAULT_MODELS_DIR,
            tools_dir=Path(tools_dir) if tools_dir else DEFAULT_TOOLS_DIR,
            debug=debug
        )
        
        async def run():
            await system.start()
            try:
                # Keep system running
                while True:
                    await asyncio.sleep(1)
            finally:
                await system.stop()
        
        asyncio.run(run())
        
    except Exception as e:
        logger.error(f"Error starting system: {e}")
        sys.exit(1)

@cli.command()
@click.argument('query', type=str)
@click.option('--config-dir', type=click.Path(exists=True), help='Configuration directory')
@click.option('--models-dir', type=click.Path(exists=True), help='Models directory')
@click.option('--tools-dir', type=click.Path(exists=True), help='Tools directory')
@click.option('--debug/--no-debug', default=False, help='Enable debug logging')
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
            config_dir=Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR,
            models_dir=Path(models_dir) if models_dir else DEFAULT_MODELS_DIR,
            tools_dir=Path(tools_dir) if tools_dir else DEFAULT_TOOLS_DIR,
            debug=debug
        )
        
        async def run():
            await system.start()
            try:
                response = await system.execute_query(query)
                print(json.dumps(response, indent=2))
            finally:
                await system.stop()
        
        asyncio.run(run())
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli() 