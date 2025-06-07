# Code Snippets from toollama/moe/core/smart_router.py

File: `toollama/moe/core/smart_router.py`  
Language: Python  
Extracted: 2025-06-07 05:11:43  

## Snippet 1
Lines 1-20

```Python
"""
Enhanced router with natural language understanding and automatic tool selection.
Extends the base ToolRouter with intelligent routing capabilities.
"""

from typing import Dict, Any, Optional, List, Tuple, Set
from pydantic import BaseModel, Field
import asyncio
import logging
from pathlib import Path
import re
from dataclasses import dataclass
try:
    from .router import ToolRouter, ToolRequest, ToolResponse, RouterError
except ImportError:
    from router import ToolRouter, ToolRequest, ToolResponse, RouterError

# Configure logging
logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 22-29

```Python
class ToolCapability:
    """Represents a tool's capabilities"""
    name: str
    description: str
    keywords: Set[str]
    examples: List[str]
    priority: int = 1
```

## Snippet 3
Lines 31-35

```Python
"""Pattern for matching tool requirements"""
    pattern: str = Field(..., description="Regex pattern to match")
    tool_id: str = Field(..., description="Tool to use when pattern matches")
    priority: int = Field(default=1, description="Priority level (1-5)")
```

## Snippet 4
Lines 39-44

```Python
def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities: Dict[str, ToolCapability] = {}
        self.patterns: List[ToolPattern] = []
        logger.debug("Initialized SmartRouter")
```

## Snippet 5
Lines 47-53

```Python
Register a tool's capabilities for smart routing.

        Args:
            tool_id: Tool identifier
            capability: Tool capability definition
        """
        self.capabilities[tool_id] = capability
```

## Snippet 6
Lines 54-56

```Python
logger.debug(f"Registered capabilities for tool {tool_id}: {capability}")

        # Auto-generate patterns from examples
```

## Snippet 7
Lines 57-63

```Python
for example in capability.examples:
            pattern = self._generate_pattern(example)
            self.patterns.append(ToolPattern(
                pattern=pattern,
                tool_id=tool_id,
                priority=capability.priority
            ))
```

## Snippet 8
Lines 66-73

```Python
def _generate_pattern(self, example: str) -> str:
        """Generate regex pattern from example"""
        # Replace specific values with wildcards
        pattern = re.escape(example)
        pattern = re.sub(r'\\\{[^}]+\\\}', '.*?', pattern)
        pattern = re.sub(r'\\\<[^>]+\\\>', '.*?', pattern)
        return f"(?i){pattern}"  # Case insensitive
```

## Snippet 9
Lines 74-87

```Python
async def route_request(self, query: str) -> ToolRequest:
        """
        Route a natural language query to the appropriate tool.

        Args:
            query: Natural language query

        Returns:
            ToolRequest object
        """
        logger.debug(f"Routing query: {query}")

        # Find all matching patterns
        matches: List[Tuple[ToolPattern, re.Match]] = []
```

## Snippet 10
Lines 93-106

```Python
if not matches:
            logger.debug("No pattern matches found, falling back to keyword matching")
            return await self._route_by_keywords(query)

        # Select best match based on priority and pattern specificity
        best_match = max(matches, key=lambda m: (
            m[0].priority,  # Higher priority first
            len(m[1].group(0)),  # Longer matches preferred
            -len(m[0].pattern)  # Simpler patterns preferred
        ))

        pattern, match = best_match
        parameters = self._extract_parameters(query, match)
```

## Snippet 11
Lines 107-113

```Python
logger.debug(f"Selected tool {pattern.tool_id} with parameters: {parameters}")

        return ToolRequest(
            tool_id=pattern.tool_id,
            parameters=parameters
        )
```

## Snippet 12
Lines 114-118

```Python
async def _route_by_keywords(self, query: str) -> ToolRequest:
        """Route based on keyword matching"""
        scores: Dict[str, int] = {}

        # Calculate scores based on keyword matches
```

## Snippet 13
Lines 134-137

```Python
# Select tool with highest score
        tool_id = max(scores.items(), key=lambda x: x[1])[0]
        parameters = self._extract_parameters(query, None)
```

## Snippet 14
Lines 138-144

```Python
logger.debug(f"Selected tool {tool_id} by keywords with parameters: {parameters}")

        return ToolRequest(
            tool_id=tool_id,
            parameters=parameters
        )
```

## Snippet 15
Lines 150-153

```Python
# Extract named groups if any
            params.update(match.groupdict())
            logger.debug(f"Extracted parameters from match: {match.groupdict()}")
```

## Snippet 16
Lines 154-158

```Python
# Add any additional parameters based on query analysis
        # This can be extended with more sophisticated parameter extraction

        return params
```

## Snippet 17
Lines 159-171

```Python
async def execute_query(self, query: str) -> ToolResponse:
        """
        Execute a natural language query.

        Args:
            query: Natural language query

        Returns:
            ToolResponse object
        """
        logger.debug(f"Executing query: {query}")
        request = await self.route_request(query)
        return await self.execute_tool(request)
```

