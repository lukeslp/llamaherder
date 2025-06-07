# Code Snippets from toollama/moe/core/discovery.py

File: `toollama/moe/core/discovery.py`  
Language: Python  
Extracted: 2025-06-07 05:11:42  

## Snippet 1
Lines 2-20

```Python
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
```

## Snippet 2
Lines 24-48

```Python
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
```

## Snippet 3
Lines 66-75

```Python
def _discover_directory(self, directory: Path) -> None:
        """
        Recursively discover tools in directory.

        Args:
            directory: Directory to search
        """
        try:
            logger.debug(f"Scanning directory: {directory}")
```

## Snippet 4
Lines 78-82

```Python
if item.is_dir() and item.name in self.excluded_dirs:
                    logger.debug(f"Skipping excluded directory: {item}")
                    continue

                # Recursively search directories
```

## Snippet 5
Lines 84-89

```Python
if item.name.startswith('_'):
                        logger.debug(f"Skipping private directory: {item}")
                        continue
                    self._discover_directory(item)
                    continue
```

## Snippet 6
Lines 91-103

```Python
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
```

## Snippet 7
Lines 107-117

```Python
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
```

## Snippet 8
Lines 118-145

```Python
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
```

## Snippet 9
Lines 148-152

```Python
except Exception as e:
                                logger.error(f"Error instantiating tool {attr_name}: {str(e)}")
                                logger.debug(f"Instantiation error details:\n{traceback.format_exc()}")
                                continue
```

## Snippet 10
Lines 153-156

```Python
except Exception as e:
                    logger.error(f"Error importing {module_path}: {str(e)}")
                    logger.debug(f"Import error details:\n{traceback.format_exc()}")
```

## Snippet 11
Lines 157-160

```Python
except Exception as e:
            logger.error(f"Error discovering tools in {directory}: {str(e)}")
            logger.debug(f"Discovery error details:\n{traceback.format_exc()}")
```

## Snippet 12
Lines 161-168

```Python
def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tool by ID.

        Args:
            tool_id: Tool identifier

        Returns:
```

## Snippet 13
Lines 173-184

```Python
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
```

## Snippet 14
Lines 189-196

```Python
def get_categories(self) -> List[str]:
        """
        Get list of available categories.

        Returns:
            List of category names
        """
        return sorted(self.categories)
```

