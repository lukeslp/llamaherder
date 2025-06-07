"""
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
            "Find scientific evidence for {claim}"
        ],
        priority=4
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
            "Generate documentation for {project}",
            "Process this {file_type} file"
        ],
        priority=3
    ),
    
    "finance_belter": ToolCapability(
        name="Finance Belter",
        description="Financial analysis and calculations",
        keywords={
            "finance", "money", "investment", "market", "stock",
            "price", "cost", "value", "calculate", "analyze"
        },
        examples=[
            "Analyze market trends for {sector}",
            "Calculate ROI for {investment}",
            "Evaluate financial metrics for {company}",
            "Project growth rate for {market}",
            "Compare investment options for {scenario}"
        ],
        priority=4
    ),
    
    "code_belter": ToolCapability(
        name="Code Belter",
        description="Code generation and review",
        keywords={
            "code", "program", "function", "class", "module",
            "develop", "implement", "debug", "test", "review"
        },
        examples=[
            "Write a function to {task}",
            "Debug this {language} code",
            "Implement a class for {purpose}",
            "Review this code for {criteria}",
            "Generate tests for {module}"
        ],
        priority=5
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
            "Find market trends for {property_type}",
            "Evaluate investment potential in {area}",
            "Compare properties in {region}",
            "Generate property report for {address}"
        ],
        priority=4
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
            "Find {business_type} near {location}",
            "Calculate distance between {points}",
            "Show route from {start} to {end}",
            "List amenities near {place}",
            "Get directions to {destination}",
            "Find coffee shops near {location}",
            "Show restaurants around {area}"
        ],
        priority=3
    ),
    
    "search_drummer": ToolCapability(
        name="Search Drummer",
        description="Web search and information retrieval",
        keywords={
            "search", "find", "lookup", "information", "web",
            "google", "bing", "results", "articles", "news"
        },
        examples=[
            "Search for information about {topic}",
            "Find recent news about {subject}",
            "Look up {term} online",
            "Get search results for {query}",
            "Find websites about {topic}"
        ],
        priority=2
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
            "Explain how {process} works",
            "Tell me about {topic}",
            "Define {term}",
            "Describe {subject}"
        ],
        priority=2
    )
}

logger.debug(f"Loaded {len(TOOL_CAPABILITIES)} tool capabilities")
for tool_id, capability in TOOL_CAPABILITIES.items():
    logger.debug(f"Tool {tool_id}:")
    logger.debug(f"  Name: {capability.name}")
    logger.debug(f"  Keywords: {capability.keywords}")
    logger.debug(f"  Examples: {capability.examples}")

# Helper function to get capability
def get_capability(tool_id: str) -> ToolCapability:
    """Get tool capability by ID"""
    if tool_id not in TOOL_CAPABILITIES:
        logger.error(f"No capability defined for tool {tool_id}")
        raise KeyError(f"No capability defined for tool {tool_id}")
    logger.debug(f"Retrieved capability for tool {tool_id}")
    return TOOL_CAPABILITIES[tool_id] 