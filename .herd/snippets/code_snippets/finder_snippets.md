# Code Snippets from toollama/API/api-tools/tools/location/finder.py

File: `toollama/API/api-tools/tools/location/finder.py`  
Language: Python  
Extracted: 2025-06-07 05:20:36  

## Snippet 1
Lines 2-10

```Python
Location finder tool for finding places and businesses.
"""

import logging
from typing import Dict, Any
from moe.core.router import ToolHandler

logger = logging.getLogger(__name__)
```

## Snippet 2
Lines 12-23

```Python
"""Handler for location-based queries"""

    tool_id = "location_drummer"  # Match the capability ID
    metadata = {
        "category": "location",
        "capabilities": [
            "find_businesses",
            "find_places",
            "search_nearby"
        ]
    }
```

## Snippet 3
Lines 24-26

```Python
def __init__(self):
        """Initialize the location finder tool"""
        super().__init__(self.tool_id)
```

## Snippet 4
Lines 29-74

```Python
async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute location search.

        Args:
            parameters: Search parameters

        Returns:
            Search results
        """
        query = parameters.get("query", "")
        logger.info(f"Searching locations: {query}")

        # TODO: Integrate with actual location API
        # For now, return mock response
        return {
            "status": "success",
            "results": [
                {
                    "name": "Starbucks Downtown",
                    "address": "1912 Pike Place, Seattle, WA 98101",
                    "type": "coffee_shop",
                    "rating": 4.5,
                    "distance": "0.2 miles"
                },
                {
                    "name": "Seattle Coffee Works",
                    "address": "107 Pike St, Seattle, WA 98101",
                    "type": "coffee_shop",
                    "rating": 4.8,
                    "distance": "0.3 miles"
                },
                {
                    "name": "Ghost Alley Espresso",
                    "address": "1499 Post Alley, Seattle, WA 98101",
                    "type": "coffee_shop",
                    "rating": 4.6,
                    "distance": "0.4 miles"
                }
            ],
            "metadata": {
                "location": "downtown Seattle",
                "radius": "1 mile",
                "total_results": 3
            }
        }
```

