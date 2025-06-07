# Code Snippets from toollama/API/api-tools/tools/tools/tools2/web_search.py

File: `toollama/API/api-tools/tools/tools/tools2/web_search.py`  
Language: Python  
Extracted: 2025-06-07 05:25:37  

## Snippet 1
Lines 1-22

```Python
"""
title: Web Search using SearXNG and Scrape first N Pages
author: constLiakos with enhancements by justinh-rahb and ther3zz
funding_url: https://github.com/open-webui
version: 0.1.12
license: MIT
"""

import os
import requests
from datetime import datetime
import json
from requests import get
from bs4 import BeautifulSoup
import concurrent.futures
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin
import re
import unicodedata
from pydantic import BaseModel, Field
import asyncio
from typing import Callable, Any
```

## Snippet 2
Lines 29-33

```Python
def get_base_url(self, url):
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return base_url
```

## Snippet 3
Lines 37-45

```Python
def format_text(self, original_text):
        soup = BeautifulSoup(original_text, "html.parser")
        formatted_text = soup.get_text(separator=" ", strip=True)
        formatted_text = unicodedata.normalize("NFKC", formatted_text)
        formatted_text = re.sub(r"\s+", " ", formatted_text)
        formatted_text = formatted_text.strip()
        formatted_text = self.remove_emojis(formatted_text)
        return formatted_text
```

## Snippet 4
Lines 49-53

```Python
def process_search_result(self, result, valves):
        title_site = self.remove_emojis(result["title"])
        url_site = result["url"]
        snippet = result.get("content", "")
```

## Snippet 5
Lines 63-84

```Python
try:
            response_site = requests.get(url_site, timeout=20)
            response_site.raise_for_status()
            html_content = response_site.text

            soup = BeautifulSoup(html_content, "html.parser")
            content_site = self.format_text(soup.get_text(separator=" ", strip=True))

            truncated_content = self.truncate_to_n_words(
                content_site, valves.PAGE_CONTENT_WORDS_LIMIT
            )

            return {
                "title": title_site,
                "url": url_site,
                "content": truncated_content,
                "snippet": self.remove_emojis(snippet),
            }

        except requests.exceptions.RequestException as e:
            return None
```

## Snippet 6
Lines 85-88

```Python
def truncate_to_n_words(self, text, token_limit):
        tokens = text.split()
        truncated_tokens = tokens[:token_limit]
        return " ".join(truncated_tokens)
```

## Snippet 7
Lines 96-106

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

## Snippet 8
Lines 110-112

```Python
class Valves(BaseModel):
        SEARXNG_ENGINE_API_BASE_URL: str = Field(
            default="https://example.com/search",
```

## Snippet 9
Lines 114-128

```Python
)
        IGNORED_WEBSITES: str = Field(
            default="",
            description="Comma-separated list of websites to ignore",
        )
        RETURNED_SCRAPPED_PAGES_NO: int = Field(
            default=3,
            description="The number of Search Engine Results to Parse",
        )
        SCRAPPED_PAGES_NO: int = Field(
            default=5,
            description="Total pages scapped. Ideally greater than one of the returned pages",
        )
        PAGE_CONTENT_WORDS_LIMIT: int = Field(
            default=5000,
```

## Snippet 10
Lines 130-135

```Python
)
        CITATION_LINKS: bool = Field(
            default=False,
            description="If True, send custom citations with links",
        )
```

## Snippet 11
Lines 136-141

```Python
def __init__(self):
        self.valves = self.Valves()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
```

## Snippet 12
Lines 142-147

```Python
async def search_web(
        self,
        query: str,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
```

## Snippet 13
Lines 148-159

```Python
Search the web and get the content of the relevant pages. Search for unknown knowledge, news, info, public contact info, weather, etc.
        :params query: Web Query used in search engine.
        :return: The content of the pages in json format.
        """
        functions = HelpFunctions()
        emitter = EventEmitter(__event_emitter__)

        await emitter.emit(f"Initiating web search for: {query}")

        search_engine_url = self.valves.SEARXNG_ENGINE_API_BASE_URL

        # Ensure RETURNED_SCRAPPED_PAGES_NO does not exceed SCRAPPED_PAGES_NO
```

## Snippet 14
Lines 160-178

```Python
if self.valves.RETURNED_SCRAPPED_PAGES_NO > self.valves.SCRAPPED_PAGES_NO:
            self.valves.RETURNED_SCRAPPED_PAGES_NO = self.valves.SCRAPPED_PAGES_NO

        params = {
            "q": query,
            "format": "json",
            "number_of_results": self.valves.RETURNED_SCRAPPED_PAGES_NO,
        }

        try:
            await emitter.emit("Sending request to search engine")
            resp = requests.get(
                search_engine_url, params=params, headers=self.headers, timeout=120
            )
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            limited_results = results[: self.valves.SCRAPPED_PAGES_NO]
```

## Snippet 15
Lines 181-189

```Python
except requests.exceptions.RequestException as e:
            await emitter.emit(
                status="error",
                description=f"Error during search: {str(e)}",
                done=True,
            )
            return json.dumps({"error": str(e)})

        results_json = []
```

## Snippet 16
Lines 190-197

```Python
if limited_results:
            await emitter.emit(f"Processing search results")

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(
                        functions.process_search_result, result, self.valves
                    )
```

## Snippet 17
Lines 202-207

```Python
if result_json:
                        try:
                            json.dumps(result_json)
                            results_json.append(result_json)
                        except (TypeError, ValueError):
                            continue
```

## Snippet 18
Lines 214-225

```Python
for result in results_json:
                    await __event_emitter__(
                        {
                            "type": "citation",
                            "data": {
                                "document": [result["content"]],
                                "metadata": [{"source": result["url"]}],
                                "source": {"name": result["title"]},
                            },
                        }
                    )
```

## Snippet 19
Lines 230-233

```Python
)

        return json.dumps(results_json, ensure_ascii=False)
```

## Snippet 20
Lines 234-257

```Python
async def get_website(
        self, url: str, __event_emitter__: Callable[[dict], Any] = None
    ) -> str:
        """
        Web scrape the website provided and get the content of it.
        :params url: The URL of the website.
        :return: The content of the website in json format.
        """
        functions = HelpFunctions()
        emitter = EventEmitter(__event_emitter__)

        await emitter.emit(f"Fetching content from URL: {url}")

        results_json = []

        try:
            response_site = requests.get(url, headers=self.headers, timeout=120)
            response_site.raise_for_status()
            html_content = response_site.text

            await emitter.emit("Parsing website content")

            soup = BeautifulSoup(html_content, "html.parser")
```

## Snippet 21
Lines 258-279

```Python
page_title = soup.title.string if soup.title else "No title found"
            page_title = unicodedata.normalize("NFKC", page_title.strip())
            page_title = functions.remove_emojis(page_title)
            title_site = page_title
            url_site = url
            content_site = functions.format_text(
                soup.get_text(separator=" ", strip=True)
            )

            truncated_content = functions.truncate_to_n_words(
                content_site, self.valves.PAGE_CONTENT_WORDS_LIMIT
            )

            result_site = {
                "title": title_site,
                "url": url_site,
                "content": truncated_content,
                "excerpt": functions.generate_excerpt(content_site),
            }

            results_json.append(result_site)
```

## Snippet 22
Lines 280-297

```Python
if self.valves.CITATION_LINKS and __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "citation",
                        "data": {
                            "document": [truncated_content],
                            "metadata": [{"source": url_site}],
                            "source": {"name": title_site},
                        },
                    }
                )

            await emitter.emit(
                status="complete",
                description="Website content retrieved and processed successfully",
                done=True,
            )
```

## Snippet 23
Lines 298-312

```Python
except requests.exceptions.RequestException as e:
            results_json.append(
                {
                    "url": url,
                    "content": f"Failed to retrieve the page. Error: {str(e)}",
                }
            )

            await emitter.emit(
                status="error",
                description=f"Error fetching website content: {str(e)}",
                done=True,
            )

        return json.dumps(results_json, ensure_ascii=False)
```

