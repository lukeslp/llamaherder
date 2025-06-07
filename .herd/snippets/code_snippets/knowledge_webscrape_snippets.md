# Code Snippets from toollama/moe/tools/knowledge/search/knowledge_webscrape.py

File: `toollama/moe/tools/knowledge/search/knowledge_webscrape.py`  
Language: Python  
Extracted: 2025-06-07 05:13:08  

## Snippet 1
Lines 1-20

```Python
"""
title: Enhanced Web Scrape
description: An improved web scraping tool that extracts text content using Jina Reader, now with better filtering, user-configuration, and UI feedback using emitters.
author: ekatiyar
author_url: https://github.com/ekatiyar
github: https://github.com/ekatiyar/open-webui-tools
original_author: Pyotr Growpotkin
original_author_url: https://github.com/christ-offer/
original_github: https://github.com/christ-offer/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.4
license: MIT
"""

import requests
from typing import Callable, Any
import re
from pydantic import BaseModel, Field
import unittest
```

## Snippet 2
Lines 21-25

```Python
def extract_title(text):
    """
    Extracts the title from a string containing structured text.

    :param text: The input string containing the title.
```

## Snippet 3
Lines 26-28

```Python
:return: The extracted title string, or None if the title is not found.
    """
    match = re.search(r'Title: (.*)\n', text)
```

## Snippet 4
Lines 31-39

```Python
def clean_urls(text) -> str:
    """
    Cleans URLs from a string containing structured text.

    :param text: The input string containing the URLs.
    :return: The cleaned string with URLs removed.
    """
    return re.sub(r'\((http[^)]+)\)', '', text)
```

## Snippet 5
Lines 54-65

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

## Snippet 6
Lines 67-75

```Python
class Valves(BaseModel):
        DISABLE_CACHING: bool = Field(
            default=False, description="Bypass Jina Cache when scraping"
        )
        GLOBAL_JINA_API_KEY: str = Field(
            default="",
            description="(Optional) Jina API key. Allows a higher rate limit when scraping. Used when a User-specific API key is not available."
        )
```

## Snippet 7
Lines 76-84

```Python
class UserValves(BaseModel):
        CLEAN_CONTENT: bool = Field(
            default=True, description="Remove links and image urls from scraped content. This reduces the number of tokens."
        )
        JINA_API_KEY: str = Field(
            default="",
            description="(Optional) Jina API key. Allows a higher rate limit when scraping."
        )
```

## Snippet 8
Lines 85-88

```Python
def __init__(self):
        self.valves = self.Valves()
        self.citation = True
```

## Snippet 9
Lines 89-101

```Python
async def web_scrape(self, url: str, __event_emitter__: Callable[[dict], Any] = None, __user__: dict = {}) -> str:
        """
        Scrape and process a web page using r.jina.ai

        :param url: The URL of the web page to scrape.
        :return: The scraped and processed webpage content, or an error message.
        """
        emitter = EventEmitter(__event_emitter__)

        await emitter.progress_update(f"Scraping {url}")
        jina_url = f"https://r.jina.ai/{url}"

        headers = {
```

## Snippet 10
Lines 108-115

```Python
elif self.valves.GLOBAL_JINA_API_KEY:
            headers["Authorization"] = f"Bearer {self.valves.GLOBAL_JINA_API_KEY}"

        try:
            response = requests.get(jina_url, headers=headers)
            response.raise_for_status()

            should_clean = "valves" not in __user__ or __user__["valves"].CLEAN_CONTENT
```

## Snippet 11
Lines 124-128

```Python
except requests.RequestException as e:
            error_message = f"Error scraping web page: {str(e)}"
            await emitter.error_update(error_message)
            return error_message
```

## Snippet 12
Lines 130-135

```Python
async def test_web_scrape(self):
        url = "https://toscrape.com/"
        content = await Tools().web_scrape(url)
        self.assertEqual("Scraping Sandbox", extract_title(content))
        self.assertEqual(len(content), 770)
```

