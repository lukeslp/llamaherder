# Code Snippets from toollama/API/api-tools/tools/search/arxiv.py

File: `toollama/API/api-tools/tools/search/arxiv.py`  
Language: Python  
Extracted: 2025-06-07 05:19:32  

## Snippet 1
Lines 1-6

```Python
"""arXiv API tool for the MoE system."""

import arxiv
from typing import Dict, Any, Optional, Callable, Awaitable, List
from ..base import BaseTool
```

## Snippet 2
Lines 14-22

```Python
async def execute(
        self,
        query: str,
        max_results: int = 5,
        sort_by: str = "relevance",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None
    ) -> str:
        """
```

## Snippet 3
Lines 23-29

```Python
Search for arXiv papers.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            sort_by: Sort order (relevance or lastUpdatedDate)
            __user__: User context
```

## Snippet 4
Lines 32-36

```Python
Returns:
            Formatted paper results
        """
        await self.emit_event(
            "status",
```

## Snippet 5
Lines 40-46

```Python
)

        try:
            # Create search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
```

## Snippet 6
Lines 54-56

```Python
if not papers:
                await self.emit_event(
                    "status",
```

## Snippet 7
Lines 71-79

```Python
await self.emit_event(
                "status",
                "Search completed",
                True,
                __event_emitter__
            )

            return results
```

## Snippet 8
Lines 80-88

```Python
except Exception as e:
            error_msg = f"Error searching arXiv: {str(e)}"
            await self.emit_event(
                "status",
                error_msg,
                True,
                __event_emitter__
            )
            return error_msg
```

