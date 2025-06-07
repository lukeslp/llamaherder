# Code Snippets from toollama/API/api-tools/tools/tools/tools2/arXiv.py

File: `toollama/API/api-tools/tools/tools/tools2/arXiv.py`  
Language: Python  
Extracted: 2025-06-07 05:25:32  

## Snippet 1
Lines 3-14

```Python
description: Tool to search arXiv.org for relevant papers on a topic
author: Haervwe
git: https://github.com/Haervwe/open-webui-tools/
version: 0.1.3
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel
import urllib.parse
```

## Snippet 2
Lines 23-26

```Python
def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.max_results = 5
```

## Snippet 3
Lines 27-33

```Python
async def search_papers(
        self,
        topic: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
```

## Snippet 4
Lines 34-36

```Python
Search arXiv.org for papers on a given topic and return formatted results.

        Args:
```

## Snippet 5
Lines 39-42

```Python
Returns:
            Formatted string containing paper details including titles, authors, dates,
            URLs and abstracts
        """
```

## Snippet 6
Lines 43-74

```Python
if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Searching arXiv database...",
                        "done": False,
                    },
                }
            )

        try:
            # Construct search query
            search_query = f'all:"{topic}" OR abs:"{topic}" OR ti:"{topic}"'
            encoded_query = urllib.parse.quote(search_query)

            params = {
                "search_query": encoded_query,
                "start": 0,
                "max_results": self.max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }

            # Make request to arXiv API
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)
            entries = root.findall("{http://www.w3.org/2005/Atom}entry")
```

## Snippet 7
Lines 76-84

```Python
if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "No papers found", "done": True},
                        }
                    )
                return f"No papers found on arXiv related to '{topic}'"
```

## Snippet 8
Lines 118-134

```Python
if published is not None and published.text:
                    try:
                        pub_date = datetime.strptime(
                            published.text, "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%Y-%m-%d")
                    except ValueError:
                        pub_date = "Unknown Date"
                else:
                    pub_date = "Unknown Date"

                # Format paper entry
                results += f"{i}. {title_text}\n"
                results += f"   Authors: {authors_str}\n"
                results += f"   Published: {pub_date}\n"
                results += f"   URL: {link_text}\n"
                results += f"   Summary: {summary_text}\n\n"
```

## Snippet 9
Lines 135-144

```Python
if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Search completed", "done": True},
                    }
                )

            return results
```

## Snippet 10
Lines 147-151

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

## Snippet 11
Lines 154-158

```Python
if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
```

