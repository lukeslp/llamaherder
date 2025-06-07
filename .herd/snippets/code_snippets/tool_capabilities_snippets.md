# Code Snippets from toollama/moe/core/tool_capabilities.py

File: `toollama/moe/core/tool_capabilities.py`  
Language: Python  
Extracted: 2025-06-07 05:11:31  

## Snippet 1
Lines 2-27

```Python
Tool capability definitions for the smart router.
"""

import logging
from typing import Dict, Set
try:
    from .smart_router import ToolCapability
except ImportError:
    from smart_router import ToolCapability

logger = logging.getLogger(__name__)

# Define standard tool capabilities
TOOL_CAPABILITIES: Dict[str, ToolCapability] = {
    "research_belter": ToolCapability(
        name="Research Belter",
        description="Academic research and knowledge synthesis",
        keywords={
            "research", "paper", "academic", "study", "analysis",
            "literature", "review", "scientific", "journal", "publication"
        },
        examples=[
            "Find research papers about {topic}",
            "Analyze recent studies on {topic}",
            "Summarize academic literature about {topic}",
            "What does research say about {topic}",
```

## Snippet 2
Lines 31-43

```Python
),

    "document_belter": ToolCapability(
        name="Document Belter",
        description="Document processing and content generation",
        keywords={
            "document", "file", "content", "text", "write",
            "generate", "create", "format", "edit", "process"
        },
        examples=[
            "Create a document about {topic}",
            "Write a report on {topic}",
            "Format this {content}",
```

## Snippet 3
Lines 48-57

```Python
),

    "finance_belter": ToolCapability(
        name="Finance Belter",
        description="Financial analysis and calculations",
        keywords={
            "finance", "money", "investment", "market", "stock",
            "price", "cost", "value", "calculate", "analyze"
        },
        examples=[
```

## Snippet 4
Lines 65-74

```Python
),

    "code_belter": ToolCapability(
        name="Code Belter",
        description="Code generation and review",
        keywords={
            "code", "program", "function", "class", "module",
            "develop", "implement", "debug", "test", "review"
        },
        examples=[
```

## Snippet 5
Lines 82-92

```Python
),

    "property_belter": ToolCapability(
        name="Property Belter",
        description="Real estate and location analysis",
        keywords={
            "property", "real estate", "location", "area", "market",
            "house", "apartment", "commercial", "residential", "price"
        },
        examples=[
            "Analyze property values in {location}",
```

## Snippet 6
Lines 99-109

```Python
),

    "location_drummer": ToolCapability(
        name="Location Drummer",
        description="Location-based services and mapping",
        keywords={
            "location", "map", "distance", "route", "navigate",
            "find", "nearby", "place", "address", "directions",
            "coffee", "restaurant", "shop", "store", "business"
        },
        examples=[
```

## Snippet 7
Lines 112-116

```Python
"Show route from {start} to {end}",
            "List amenities near {place}",
            "Get directions to {destination}",
            "Find coffee shops near {location}",
            "Show restaurants around {area}"
```

## Snippet 8
Lines 119-128

```Python
),

    "search_drummer": ToolCapability(
        name="Search Drummer",
        description="Web search and information retrieval",
        keywords={
            "search", "find", "lookup", "information", "web",
            "google", "bing", "results", "articles", "news"
        },
        examples=[
```

## Snippet 9
Lines 136-146

```Python
),

    "knowledge_drummer": ToolCapability(
        name="Knowledge Drummer",
        description="Knowledge base and fact retrieval",
        keywords={
            "knowledge", "fact", "information", "definition", "explain",
            "what is", "how to", "tell me about", "describe", "details"
        },
        examples=[
            "What is {concept}",
```

## Snippet 10
Lines 157-162

```Python
for tool_id, capability in TOOL_CAPABILITIES.items():
    logger.debug(f"Tool {tool_id}:")
    logger.debug(f"  Name: {capability.name}")
    logger.debug(f"  Keywords: {capability.keywords}")
    logger.debug(f"  Examples: {capability.examples}")
```

