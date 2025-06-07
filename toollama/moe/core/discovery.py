"""
Tool discovery system for finding and registering available tools.
"""

import os
import sys
import importlib
import logging
import traceback
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Type
try:
    from .router import ToolRouter, ToolHandler
    from .registry import ModelRegistry
except ImportError:
    from router import ToolRouter, ToolHandler
    from registry import ModelRegistry

logger = logging.getLogger(__name__)

class ToolDiscovery:
    """Discovers and registers available tools"""
    
    def __init__(
        self,
        tools_dir: str,
        router: ToolRouter,
        registry: ModelRegistry,
        excluded_dirs: Optional[List[str]] = None
    ):
        """
        Initialize tool discovery.
        
        Args:
            tools_dir: Directory containing tools
            router: Tool router instance
            registry: Model registry instance
            excluded_dirs: List of directories to exclude
        """
        self.tools_dir = Path(tools_dir)
        self.router = router
        self.registry = registry
        self.excluded_dirs = excluded_dirs or ['__pycache__', 'tests']
        self.discovered_tools: Dict[str, Any] = {}
        self.categories: Set[str] = set()
        
        logger.debug(f"Initialized tool discovery with directory: {tools_dir}")
        
    def discover_tools(self) -> None:
        """Discover and register available tools"""
        if not self.tools_dir.exists():
            logger.warning(f"Tools directory {self.tools_dir} does not exist")
            return
            
        # Add parent directory to Python path to support absolute imports
        parent_dir = str(self.tools_dir.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            logger.debug(f"Added {parent_dir} to Python path")
            
        # Discover tools recursively
        self._discover_directory(self.tools_dir)
        
        logger.info(f"Discovered {len(self.discovered_tools)} tools in {len(self.categories)} categories")
        
    def _discover_directory(self, directory: Path) -> None:
        """
        Recursively discover tools in directory.
        
        Args:
            directory: Directory to search
        """
        try:
            logger.debug(f"Scanning directory: {directory}")
            
            for item in directory.iterdir():
                # Skip excluded directories
                if item.is_dir() and item.name in self.excluded_dirs:
                    logger.debug(f"Skipping excluded directory: {item}")
                    continue
                    
                # Recursively search directories
                if item.is_dir():
                    if item.name.startswith('_'):
                        logger.debug(f"Skipping private directory: {item}")
                        continue
                    self._discover_directory(item)
                    continue
                    
                # Only process Python files
                if not item.name.endswith('.py') or item.name.startswith('_'):
                    continue
                    
                # Import module
                try:
                    # Convert path to module path relative to parent directory
                    rel_path = item.relative_to(self.tools_dir.parent)
                    module_path = str(rel_path).replace('/', '.')[:-3]  # Remove .py
                    logger.debug(f"Attempting to import module: {module_path}")
                    
                    module = importlib.import_module(module_path)
                    logger.debug(f"Successfully imported module: {module_path}")
                    
                    # Look for tool classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type) and
                            issubclass(attr, ToolHandler) and
                            attr is not ToolHandler
                        ):
                            try:
                                # Found a tool class
                                tool_class: Type[ToolHandler] = attr
                                
                                # Get tool ID from class
                                tool_id = getattr(tool_class, 'tool_id', None)
                                if not tool_id:
                                    tool_id = f"{module_path}.{attr_name}"
                                    logger.debug(f"Using default tool ID: {tool_id}")
                                
                                logger.debug(f"Found tool class: {tool_id}")
                                
                                # Create instance
                                instance = tool_class()
                                
                                # Get metadata
                                metadata = getattr(instance, 'metadata', {})
                                category = metadata.get('category', 'general')
                                
                                # Register tool
                                self.discovered_tools[tool_id] = {
                                    'class': tool_class,
                                    'instance': instance,
                                    'module': module,
                                    'category': category,
                                    'metadata': metadata
                                }
                                
                                # Register with router
                                self.router.register_handler(tool_id, instance)
                                
                                # Update categories
                                self.categories.add(category)
                                
                                logger.info(f"Discovered tool {tool_id} in category {category}")
                                
                            except Exception as e:
                                logger.error(f"Error instantiating tool {attr_name}: {str(e)}")
                                logger.debug(f"Instantiation error details:\n{traceback.format_exc()}")
                                continue
                            
                except Exception as e:
                    logger.error(f"Error importing {module_path}: {str(e)}")
                    logger.debug(f"Import error details:\n{traceback.format_exc()}")
                    
        except Exception as e:
            logger.error(f"Error discovering tools in {directory}: {str(e)}")
            logger.debug(f"Discovery error details:\n{traceback.format_exc()}")
            
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tool by ID.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool information or None if not found
        """
        return self.discovered_tools.get(tool_id)
        
    def get_tools_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all tools in a category.
        
        Args:
            category: Tool category
            
        Returns:
            Dictionary of matching tools
        """
        return {
            tool_id: info
            for tool_id, info in self.discovered_tools.items()
            if info['category'] == category
        }
        
    def get_categories(self) -> List[str]:
        """
        Get list of available categories.
        
        Returns:
            List of category names
        """
        return sorted(self.categories)