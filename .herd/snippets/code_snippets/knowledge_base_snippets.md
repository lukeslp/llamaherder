# Code Snippets from toollama/moe/tools/knowledge/research/knowledge_base.py

File: `toollama/moe/tools/knowledge/research/knowledge_base.py`  
Language: Python  
Extracted: 2025-06-07 05:13:31  

## Snippet 1
Lines 1-19

```Python
"""
Knowledge base tools with enhanced accessibility and formatting
"""

import json
import requests
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union, List, Callable
import re
from pathlib import Path
import os
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import wolframalpha
from bs4 import BeautifulSoup
import markdown
import html2text
from langchain_community.document_loaders import YoutubeLoader
```

## Snippet 2
Lines 35-44

```Python
if self.event_emitter:
            await self.event_emitter({
                "type": "status",
                "data": {
                    "status": status,
                    "description": description,
                    "done": done,
                }
            })
```

## Snippet 3
Lines 48-54

```Python
class Valves(BaseModel):
        WIKIDATA_ENDPOINT: str = Field(
            default="https://query.wikidata.org/sparql",
            description="Wikidata SPARQL endpoint"
        )
        WIKIDATA_USER_AGENT: str = Field(
            default="ToolLama Knowledge Base/1.0",
```

## Snippet 4
Lines 56-58

```Python
)
        WOLFRAM_TIMEOUT: int = Field(
            default=30,
```

## Snippet 5
Lines 60-86

```Python
)
        PERPLEXITY_MODES: Dict[str, Dict[str, Any]] = Field(
            default={
                "search": {
                    "description": "General web search",
                    "focus_areas": ["general", "news", "tech", "science"]
                },
                "academic": {
                    "description": "Academic research",
                    "focus_areas": ["papers", "journals", "conferences", "books"]
                },
                "writing": {
                    "description": "Writing assistance",
                    "focus_areas": ["grammar", "style", "citations", "references"]
                },
                "analysis": {
                    "description": "Deep analysis",
                    "focus_areas": ["trends", "comparisons", "statistics", "insights"]
                }
            },
            description="Available Perplexity search modes"
        )
        YOUTUBE_LANGUAGES: List[str] = Field(
            default=["en", "en_auto"],
            description="Default YouTube transcript languages"
        )
```

## Snippet 6
Lines 87-91

```Python
def __init__(self):
        self.valves = self.Valves()
        self.sparql = SPARQLWrapper(self.valves.WIKIDATA_ENDPOINT)
        self.sparql.agent = self.valves.WIKIDATA_USER_AGENT
```

## Snippet 7
Lines 94-99

```Python
if wolfram_key:
            self.wolfram_client = wolframalpha.Client(wolfram_key)
        else:
            self.wolfram_client = None
            print("Warning: WOLFRAM_APP_ID not set", file=sys.stderr)
```

## Snippet 8
Lines 105-119

```Python
def _convert_to_sparql(self, query: str) -> str:
        """Convert natural language query to SPARQL"""
        # TODO: Implement natural language to SPARQL conversion
        # For now, return basic SPARQL query template
        return f"""
        SELECT ?item ?itemLabel ?date WHERE {{
            ?item wdt:P31 ?type .
            ?item wdt:P571 ?date .
            ?item rdfs:label ?itemLabel .
            FILTER(CONTAINS(LCASE(?itemLabel), LCASE("{query}")))
            FILTER(LANG(?itemLabel) = "en")
        }}
        LIMIT 10
        """
```

## Snippet 9
Lines 124-134

```Python
if not query.lower().startswith("select "):
                query = self._convert_to_sparql(query)

            # Set up query
            self.sparql.setQuery(query)
            self.sparql.setReturnFormat(JSON)

            # Execute query
            results = self.sparql.query().convert()

            # Process results based on format
```

## Snippet 10
Lines 135-138

```Python
if format == "raw":
                processed_results = results
            else:
                processed_results = []
```

## Snippet 11
Lines 140-146

```Python
if format == "simple":
                        processed_results.append({
                            "label": result.get("itemLabel", {}).get("value"),
                            "value": result.get("item", {}).get("value")
                        })
                    else:  # detailed
                        processed_results.append({
```

## Snippet 12
Lines 153-161

```Python
return {
                "status": "success",
                "data": {
                    "query": query,
                    "format": format,
                    "results": processed_results,
                    "count": len(processed_results)
                }
            }
```

## Snippet 13
Lines 162-167

```Python
except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying Wikidata: {str(e)}"
            }
```

## Snippet 14
Lines 171-179

```Python
if not self.wolfram_client:
                raise ValueError("Wolfram Alpha API key not configured")

            # Process options
            format_type = options.get("format", "plain")
            timeout = options.get("timeout", self.valves.WOLFRAM_TIMEOUT)
            show_steps = options.get("show_steps", False)
            units = options.get("units", "metric")
```

## Snippet 15
Lines 185-191

```Python
if show_steps:
                query = f"step-by-step {query}"

            # Make API request
            result = self.wolfram_client.query(query, timeout=timeout)

            # Process results based on format
```

## Snippet 16
Lines 213-221

```Python
return {
                "status": "success",
                "data": {
                    "query": query,
                    "format": format_type,
                    "result": processed_result,
                    "options": options
                }
            }
```

## Snippet 17
Lines 222-227

```Python
except Exception as e:
            return {
                "status": "error",
                "message": f"Error querying Wolfram Alpha: {str(e)}"
            }
```

## Snippet 18
Lines 228-230

```Python
def search_perplexity(self, query: str, mode: str = "search", options: dict = {}) -> Dict[str, Any]:
        """Search using Perplexity AI"""
        try:
```

## Snippet 19
Lines 231-234

```Python
if not self.perplexity_key:
                raise ValueError("Perplexity API key not configured")

            # Validate mode
```

## Snippet 20
Lines 235-243

```Python
if mode not in self.valves.PERPLEXITY_MODES:
                raise ValueError(f"Invalid mode: {mode}")

            # Process options
            focus = options.get("focus")
            max_results = options.get("max_results", 5)
            include_citations = options.get("include_citations", False)
            recent_only = options.get("recent_only", False)
```

## Snippet 21
Lines 248-259

```Python
# Prepare API request
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }

            data = {
                "query": query,
                "mode": mode,
                "max_results": max_results
            }
```

## Snippet 22
Lines 262-278

```Python
if recent_only:
                data["time_range"] = "recent"

            # Make API request
            response = requests.post(
                "https://api.perplexity.ai/search",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()

            # Process response
            results = response.json()

            # Format results
            processed_results = []
```

## Snippet 23
Lines 279-285

```Python
for result in results.get("results", []):
                processed_result = {
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "snippet": result.get("snippet")
                }
```

## Snippet 24
Lines 286-290

```Python
if include_citations and "citations" in result:
                    processed_result["citations"] = result["citations"]

                processed_results.append(processed_result)
```

## Snippet 25
Lines 291-300

```Python
return {
                "status": "success",
                "data": {
                    "query": query,
                    "mode": mode,
                    "focus": focus,
                    "results": processed_results,
                    "count": len(processed_results)
                }
            }
```

## Snippet 26
Lines 301-306

```Python
except Exception as e:
            return {
                "status": "error",
                "message": f"Error searching Perplexity: {str(e)}"
            }
```

## Snippet 27
Lines 307-311

```Python
async def get_youtube_transcript(self, url: str, options: dict = {}, __event_emitter__: Callable[[dict], Any] = None) -> Dict[str, Any]:
        """Get transcript from YouTube videos with enhanced options"""
        emitter = EventEmitter(__event_emitter__)

        try:
```

## Snippet 28
Lines 315-333

```Python
if not url or url == "" or "dQw4w9WgXcQ" in url:  # Block Rick Roll
                raise ValueError(f"Invalid YouTube URL: {url}")

            # Process options
            languages = options.get("language", self.valves.YOUTUBE_LANGUAGES)
            translate_to = options.get("translate_to", "en")
            include_metadata = options.get("include_metadata", False)

            # Initialize loader with options
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=True,
                language=languages,
                translation=translate_to
            )

            # Load transcript
            transcript = loader.load()
```

## Snippet 29
Lines 339-346

```Python
text = "\n".join(doc.page_content for doc in transcript)

            # Prepare result
            result = {
                "transcript": text,
                "url": url
            }
```

## Snippet 30
Lines 347-355

```Python
if include_metadata:
                result["metadata"] = {
                    "title": metadata.get("title"),
                    "author": metadata.get("author"),
                    "description": metadata.get("description"),
                    "view_count": metadata.get("view_count"),
                    "publish_date": str(metadata.get("publish_date"))
                }
```

## Snippet 31
Lines 356-362

```Python
await emitter.success_update(f"Successfully retrieved transcript for {metadata.get('title', url)}")

            return {
                "status": "success",
                "data": result
            }
```

## Snippet 32
Lines 363-369

```Python
except Exception as e:
            error_message = f"Error getting YouTube transcript: {str(e)}"
            await emitter.error_update(error_message)
            return {
                "status": "error",
                "message": error_message
            }
```

