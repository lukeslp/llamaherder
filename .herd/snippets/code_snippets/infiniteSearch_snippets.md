# Code Snippets from toollama/API/api-tools/tools/tools/tools2/infiniteSearch.py

File: `toollama/API/api-tools/tools/tools/tools2/infiniteSearch.py`  
Language: Python  
Extracted: 2025-06-07 05:24:58  

## Snippet 1
Lines 1-13

```Python
"""
title: Infinite Search
author: Cook Sleep
author_urls: https://github.com/cooksleep
description: Fetches and summarizes content using the Reader API from URLs or web searches.
required_open_webui_version: 0.3.15
version: 0.3
licence: MIT
"""

import requests
from pydantic import BaseModel, Field
from typing import Callable, Any, Optional
```

## Snippet 2
Lines 16-24

```Python
class Valves(BaseModel):
    SEARXNG_URL: str = Field(
        default="https://paulgo.io/search",
        description="SearXNG search URL. You can find available SearXNG instances at https://searx.space/. The URL should end with '/search'.",
    )
    BAIDU_URL: str = Field(
        default="https://www.baidu.com/s", description="Baidu search URL"
    )
    TIMEOUT: int = Field(default=30, description="Request timeout in seconds")
```

## Snippet 3
Lines 32-42

```Python
if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )
```

## Snippet 4
Lines 45-47

```Python
def get_send_citation(
    __event_emitter__: Optional[Callable[[dict], Any]]
) -> Callable[[str, str, str], None]:
```

## Snippet 5
Lines 49-61

```Python
if __event_emitter__ is None:
            return
        await __event_emitter__(
            {
                "type": "citation",
                "data": {
                    "document": [content],
                    "metadata": [{"source": url, "html": False}],
                    "source": {"name": title},
                },
            }
        )
```

## Snippet 6
Lines 65-67

```Python
def get_send_status(
    __event_emitter__: Optional[Callable[[dict], Any]]
) -> Callable[[str, bool], None]:
```

## Snippet 7
Lines 69-77

```Python
if __event_emitter__ is None:
            return
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": status_message, "done": done},
            }
        )
```

## Snippet 8
Lines 82-85

```Python
def __init__(self):
        self.valves = Valves()
        self.reader_api = "https://r.jina.ai/"
```

## Snippet 9
Lines 86-112

```Python
async def read_url(
        self, url: str, __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Read and extract the main content from a given URL.

        :param url: The URL to read from.
        :return: The main content of the page in processed format.
        """
        send_status = get_send_status(__event_emitter__)
        send_citation = get_send_citation(__event_emitter__)

        try:
            await send_status(f"Reading content from {url}", False)

            data = {"url": url}
            response = requests.post(
                self.reader_api, data=data, timeout=self.valves.TIMEOUT
            )
            response.raise_for_status()
            content = response.text

            await send_citation(url, "Web Content", content)
            await send_status(f"Content retrieved from {url}", True)

            result_presentation = """
```

## Snippet 10
Lines 113-131

```Python
<system>
PLEASE strictly FOLLOW the instructions below!
PLEASE strictly FOLLOW the instructions below!
PLEASE strictly FOLLOW the instructions below!
PLEASE strictly FOLLOW the instructions below!

# Content Processing Instructions:
- Thoroughly examine retrieved content
- Identify key points and critical data
- Assess source credibility
- Provide concise yet comprehensive summaries
- Emphasize most relevant information
- Use clear structure in your response
- Indicate any ambiguities or contradictions
- Acknowledge when information is unavailable
- Cite sources appropriately
- Consider user's language preferences
- Anticipate potential follow-up questions
```

## Snippet 11
Lines 132-146

```Python
# Use the following format for presentation (do not include "---"):
---
## [Site Name - Title](URL)
Your summary
(Leave a blank line between each summary.)
---
</system>

"""

            return content + result_presentation
        except Exception as e:
            await send_status(f"Error reading URL: {str(e)}", True)
            return f"Error reading URL: {str(e)}"
```

## Snippet 12
Lines 147-157

```Python
async def search(
        self,
        query: str,
        engine: str = "google",
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        Perform a web search using the specified engine.

        :param query: The search query.
        :param engine: The search engine to use ('google', 'bing', or 'baidu').
```

## Snippet 13
Lines 158-166

```Python
:return: The search results as formatted text ready for display.
        """
        emitter = EventEmitter(__event_emitter__)

        try:
            await emitter.emit(
                f"Searching with {engine}: {query}", status="in_progress", done=False
            )
```

## Snippet 14
Lines 175-184

```Python
response = requests.get(url, headers=headers, timeout=self.valves.TIMEOUT)
            response.raise_for_status()
            content = response.text

            await emitter.emit(
                f"Search completed with {engine}", status="complete", done=True
            )

            search_result_processing = """
```

## Snippet 15
Lines 185-204

```Python
<system>
PLEASE strictly FOLLOW the instructions below!
PLEASE strictly FOLLOW the instructions below!
PLEASE strictly FOLLOW the instructions below!
PLEASE strictly FOLLOW the instructions below!

# Search Result Processing
1. Select 1-3 highly relevant results from the search
2. Read the full content of the selected result using read_url()
</system>

"""

            return content + search_result_processing
        except Exception as e:
            await emitter.emit(
                f"Error during search: {str(e)}", status="error", done=True
            )
            return f"Error during search: {str(e)}"
```

## Snippet 16
Lines 205-211

```Python
async def google_search(
        self, query: str, __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Perform a Google search using SearXNG.

        :param query: The search query.
```

## Snippet 17
Lines 212-215

```Python
:return: The formatted search results for processing.
        """
        return await self.search(query, "google", __event_emitter__)
```

## Snippet 18
Lines 216-221

```Python
async def bing_search(
        self, query: str, __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Perform a Bing search using SearXNG.
```

## Snippet 19
Lines 222-224

```Python
Note: Bing provides a balanced choice for searching both international and Simplified Chinese content.

        :param query: The search query.
```

## Snippet 20
Lines 225-228

```Python
:return: The search results in text format ready for processing.
        """
        return await self.search(query, "bing", __event_emitter__)
```

## Snippet 21
Lines 229-234

```Python
async def baidu_search(
        self, query: str, __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """
        Perform a Baidu search.
```

## Snippet 22
Lines 235-237

```Python
Note: Baidu is optimal for Simplified Chinese content searches.

        :param query: The search query.
```

## Snippet 23
Lines 238-240

```Python
:return: The search results in text format ready for processing.
        """
        return await self.search(query, "baidu", __event_emitter__)
```

