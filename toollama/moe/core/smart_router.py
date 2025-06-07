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

@dataclass
class ToolCapability:
    """Represents a tool's capabilities"""
    name: str
    description: str
    keywords: Set[str]
    examples: List[str]
    priority: int = 1

class ToolPattern(BaseModel):
    """Pattern for matching tool requirements"""
    pattern: str = Field(..., description="Regex pattern to match")
    tool_id: str = Field(..., description="Tool to use when pattern matches")
    priority: int = Field(default=1, description="Priority level (1-5)")
    
class SmartRouter(ToolRouter):
    """Enhanced router with natural language understanding"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities: Dict[str, ToolCapability] = {}
        self.patterns: List[ToolPattern] = []
        logger.debug("Initialized SmartRouter")
        
    def register_capability(self, tool_id: str, capability: ToolCapability) -> None:
        """
        Register a tool's capabilities for smart routing.
        
        Args:
            tool_id: Tool identifier
            capability: Tool capability definition
        """
        self.capabilities[tool_id] = capability
        logger.debug(f"Registered capabilities for tool {tool_id}: {capability}")
        
        # Auto-generate patterns from examples
        for example in capability.examples:
            pattern = self._generate_pattern(example)
            self.patterns.append(ToolPattern(
                pattern=pattern,
                tool_id=tool_id,
                priority=capability.priority
            ))
            logger.debug(f"Generated pattern for {tool_id}: {pattern}")
            
    def _generate_pattern(self, example: str) -> str:
        """Generate regex pattern from example"""
        # Replace specific values with wildcards
        pattern = re.escape(example)
        pattern = re.sub(r'\\\{[^}]+\\\}', '.*?', pattern)
        pattern = re.sub(r'\\\<[^>]+\\\>', '.*?', pattern)
        return f"(?i){pattern}"  # Case insensitive
        
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
        for pattern in self.patterns:
            if match := re.search(pattern.pattern, query):
                matches.append((pattern, match))
                logger.debug(f"Pattern match found: {pattern.pattern} -> {pattern.tool_id}")
                
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
        
        logger.debug(f"Selected tool {pattern.tool_id} with parameters: {parameters}")
        
        return ToolRequest(
            tool_id=pattern.tool_id,
            parameters=parameters
        )
        
    async def _route_by_keywords(self, query: str) -> ToolRequest:
        """Route based on keyword matching"""
        scores: Dict[str, int] = {}
        
        # Calculate scores based on keyword matches
        for tool_id, capability in self.capabilities.items():
            score = 0
            matched_keywords = []
            for keyword in capability.keywords:
                if re.search(fr'\b{re.escape(keyword)}\b', query, re.IGNORECASE):
                    score += 1
                    matched_keywords.append(keyword)
            if score > 0:
                scores[tool_id] = score * capability.priority
                logger.debug(f"Tool {tool_id} matched keywords: {matched_keywords}, score: {scores[tool_id]}")
                
        if not scores:
            logger.error("No matching tool found for query")
            raise RouterError("No matching tool found for query")
            
        # Select tool with highest score
        tool_id = max(scores.items(), key=lambda x: x[1])[0]
        parameters = self._extract_parameters(query, None)
        
        logger.debug(f"Selected tool {tool_id} by keywords with parameters: {parameters}")
        
        return ToolRequest(
            tool_id=tool_id,
            parameters=parameters
        )
        
    def _extract_parameters(self, query: str, match: Optional[re.Match]) -> Dict[str, Any]:
        """Extract parameters from query"""
        params: Dict[str, Any] = {"query": query}  # Always include original query
        
        if match:
            # Extract named groups if any
            params.update(match.groupdict())
            logger.debug(f"Extracted parameters from match: {match.groupdict()}")
            
        # Add any additional parameters based on query analysis
        # This can be extended with more sophisticated parameter extraction
        
        return params
        
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