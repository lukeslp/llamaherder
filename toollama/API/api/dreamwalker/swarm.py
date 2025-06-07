"""
SwarmDreamwalker - Implementation of the query expansion and parallel search workflow
"""

import json
import requests
import asyncio
import re
import time
import logging
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse

from api.dreamwalker.base import BaseDreamwalker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the Tools class from the infinite_search module
try:
    from api.tools.infinite_search import Tools
except ImportError:
    try:
        from api_tools.tools.tools.tools2.infinite_search import Tools
        logger.warning("Using fallback import path for Tools class")
    except ImportError:
        try:
            # Try another common path
            import sys
            import os
            # Add the api-tools directory to the path
            api_tools_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'api-tools')
            sys.path.append(api_tools_path)
            from tools.tools.tools2.infinite_search import Tools
            logger.warning("Using api-tools path for Tools class")
        except ImportError:
            try:
                # Try relative import from current directory
                current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                tools_path = os.path.join(current_dir, 'api-tools', 'tools', 'tools', 'tools2')
                sys.path.append(tools_path)
                from infinite_search import Tools
                logger.warning("Using direct path to tools directory for Tools class")
            except ImportError:
                logger.error("Could not import Tools from infinite_search. Search functionality will be limited.")
                Tools = None

# Default model to use for search
DEFAULT_MODEL = "coolhand/camina-search:24b"

class SwarmDreamwalker(BaseDreamwalker):
    """
    SwarmDreamwalker implements the query expansion and parallel search workflow.
    
    This workflow:
    1. Expands a user query into multiple related search queries
    2. Executes searches in parallel across multiple search engines
    3. Extracts and processes the results
    4. Generates a comprehensive summary with proper citations
    """
    
    def __init__(self, workflow_id: Optional[str] = None, api_base_url: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize a new SwarmDreamwalker workflow.
        
        Args:
            workflow_id: Optional unique identifier for this workflow instance
            api_base_url: Base URL for the API
            model: Model to use for query expansion and summarization
        """
        super().__init__(workflow_id)
        
        self.api_base_url = api_base_url or "https://api.assisted.space/v2"
        self.model = model or DEFAULT_MODEL
        self.conversation_history = []
        
        # Initialize the tools if available
        if Tools is not None:
            self.tools = Tools()
        else:
            self.tools = None
            logger.warning("Tools not available. Search functionality will be limited.")
        
        # Define the tools that will be available to the model
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "google_search",
                    "description": "Search the web using Google search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on Google"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "bing_search",
                    "description": "Search the web using Bing search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on Bing"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "baidu_search",
                    "description": "Search the web using Baidu search engine",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to look up on Baidu"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_url",
                    "description": "Extract and read content from a specified URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to extract content from"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]
        
        # Set up metadata
        self.metadata = {
            "model": self.model,
            "api_base_url": self.api_base_url,
            "tools_available": Tools is not None
        }
        
        logger.info(f"Initialized SwarmDreamwalker with model {self.model}")
    
    async def _google_search(self, query: str) -> str:
        """Implementation of the google_search tool"""
        if self.tools is None:
            return f"Error: Search tools not available"
        
        try:
            self.update_progress(
                progress=self.progress + 5, 
                step_description=f"Executing Google search for: {query}"
            )
            result = await self.tools.google_search(query)
            return result
        except Exception as e:
            logger.error(f"Error performing Google search: {str(e)}")
            return f"Error performing Google search: {str(e)}"
    
    async def _bing_search(self, query: str) -> str:
        """Implementation of the bing_search tool"""
        if self.tools is None:
            return f"Error: Search tools not available"
        
        try:
            self.update_progress(
                progress=self.progress + 5, 
                step_description=f"Executing Bing search for: {query}"
            )
            result = await self.tools.bing_search(query)
            return result
        except Exception as e:
            logger.error(f"Error performing Bing search: {str(e)}")
            return f"Error performing Bing search: {str(e)}"
    
    async def _baidu_search(self, query: str) -> str:
        """Implementation of the baidu_search tool"""
        if self.tools is None:
            return f"Error: Search tools not available"
        
        try:
            self.update_progress(
                progress=self.progress + 5, 
                step_description=f"Executing Baidu search for: {query}"
            )
            result = await self.tools.baidu_search(query)
            return result
        except Exception as e:
            logger.error(f"Error performing Baidu search: {str(e)}")
            return f"Error performing Baidu search: {str(e)}"
    
    async def _read_url(self, url: str) -> str:
        """Implementation of the read_url tool"""
        if self.tools is None:
            return f"Error: URL reading tools not available"
        
        try:
            self.update_progress(
                progress=self.progress + 2, 
                step_description=f"Reading content from URL: {url}"
            )
            result = await self.tools.read_url(url)
            return result
        except Exception as e:
            logger.error(f"Error reading URL {url}: {str(e)}")
            return f"Error reading URL {url}: {str(e)}"
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the result"""
        try:
            function_name = tool_call.get("function", {}).get("name")
            function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
            
            # Execute the appropriate tool function
            if function_name == "google_search":
                result = await self._google_search(function_args.get("query", ""))
            elif function_name == "bing_search":
                result = await self._bing_search(function_args.get("query", ""))
            elif function_name == "baidu_search":
                result = await self._baidu_search(function_args.get("query", ""))
            elif function_name == "read_url":
                result = await self._read_url(function_args.get("url", ""))
            else:
                result = f"Error: Tool '{function_name}' not implemented"
            
            return {
                "tool_call_id": tool_call.get("id"),
                "role": "tool",
                "content": result
            }
        except Exception as e:
            logger.error(f"Error executing tool call: {str(e)}")
            return {
                "tool_call_id": tool_call.get("id", "unknown"),
                "role": "tool",
                "content": f"Error executing tool: {str(e)}"
            }
    
    def _extract_urls_from_search_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract and organize URLs from search results
        Returns a list of dictionaries with url, title, and domain information
        """
        organized_urls = []
        url_set = set()  # To track unique URLs
        
        for result in search_results:
            content = result.get("result", "")
            
            # Extract URLs with titles using regex patterns
            # Look for patterns like "Title - URL" or "[Title](URL)"
            title_url_patterns = [
                r'([^\n]+) - (https?://[^\s\)"]+)',  # Title - URL format
                r'\[(.*?)\]\((https?://[^\s\)"]+)\)',  # [Title](URL) format
                r'\"(.*?)\" (https?://[^\s\)"]+)'  # "Title" URL format
            ]
            
            for pattern in title_url_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) >= 2:
                        title = match[0].strip()
                        url = match[1].strip()
                        
                        # Skip if URL already processed
                        if url in url_set:
                            continue
                        
                        url_set.add(url)
                        
                        # Get domain name
                        try:
                            domain = urlparse(url).netloc
                        except:
                            domain = "unknown"
                        
                        organized_urls.append({
                            "url": url,
                            "title": title,
                            "domain": domain
                        })
            
            # Also extract any standalone URLs
            standalone_urls = re.findall(r'https?://[^\s\)"]+', content)
            for url in standalone_urls:
                url = url.strip()
                
                # Skip if URL already processed
                if url in url_set:
                    continue
                
                url_set.add(url)
                
                # Get domain name
                try:
                    domain = urlparse(url).netloc
                except:
                    domain = "unknown"
                
                # Try to extract a title from nearby text
                title_match = re.search(r'([^.!?]+)[.!?]\s+' + re.escape(url), content)
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = domain
                
                organized_urls.append({
                    "url": url,
                    "title": title,
                    "domain": domain
                })
        
        return organized_urls
    
    def _format_references_section(self, urls: List[Dict[str, Any]]) -> str:
        """Format a comprehensive references section"""
        if not urls:
            return "## References\nNo references available."
        
        # Group URLs by domain
        domains = {}
        for url_info in urls:
            domain = url_info.get("domain", "unknown")
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(url_info)
        
        # Format the references section
        references = "## References\n\n"
        
        # Add each domain as a subsection
        for domain, url_list in domains.items():
            references += f"### {domain}\n"
            for i, url_info in enumerate(url_list):
                title = url_info.get("title", "Untitled")
                url = url_info.get("url", "")
                references += f"{i+1}. [{title}]({url})\n"
            references += "\n"
        
        return references
    
    async def _generate_variant_queries(self, query: str) -> List[str]:
        """
        Generate variant search queries based on the original query.
        
        Args:
            query: The original user query
            
        Returns:
            A list of variant search queries
        """
        self.update_progress(
            progress=5, 
            status="running",
            step_description="Generating variant search queries"
        )
        
        # Add the user query to the conversation history
        self.conversation_history.append({"role": "user", "content": query})
        
        # Ask the model to generate variant search queries
        variant_generation_url = f"{self.api_base_url}/chat/ollama"
        variant_payload = {
            "model": self.model,
            "messages": self.conversation_history + [{
                "role": "system", 
                "content": "Generate five variant search queries based on the user's original query. These should be related but different angles or aspects to explore the topic more comprehensively. Format your response as a JSON array of strings. ONLY respond with the JSON array, nothing else."
            }],
            "stream": False
        }
        
        try:
            # Get variant search queries from the model
            logger.info(f"Generating variant search queries for: {query}")
            variant_response = requests.post(variant_generation_url, json=variant_payload)
            variant_response.raise_for_status()
            variant_result = variant_response.json()
            
            variant_content = variant_result.get("message", {}).get("content", "")
            
            # Try to extract the JSON array of variant queries
            try:
                # Find anything that looks like a JSON array in the response
                json_match = re.search(r'\[.*\]', variant_content, re.DOTALL)
                if json_match:
                    variant_queries_json = json_match.group(0)
                    variant_queries = json.loads(variant_queries_json)
                else:
                    # If no JSON array is found, create some basic variants
                    variant_queries = [
                        query,
                        f"latest information about {query}",
                        f"{query} background and history",
                        f"{query} notable achievements",
                        f"{query} current status"
                    ]
            except json.JSONDecodeError:
                # If JSON parsing fails, create some basic variants
                variant_queries = [
                    query,
                    f"latest information about {query}",
                    f"{query} background and history",
                    f"{query} notable achievements",
                    f"{query} current status"
                ]
            
            # Ensure we have exactly 5 queries
            if len(variant_queries) > 5:
                variant_queries = variant_queries[:5]
            while len(variant_queries) < 5:
                variant_queries.append(f"{query} additional information {len(variant_queries) + 1}")
            
            # Log the variant queries
            logger.info(f"Generated {len(variant_queries)} variant queries")
            for i, variant in enumerate(variant_queries):
                logger.info(f"  {i+1}. {variant}")
            
            self.update_progress(
                progress=10, 
                step_description=f"Generated {len(variant_queries)} variant search queries"
            )
            
            return variant_queries
            
        except Exception as e:
            logger.error(f"Error generating variant queries: {str(e)}")
            # Fall back to basic variants
            basic_variants = [
                query,
                f"latest information about {query}",
                f"{query} background and history",
                f"{query} notable achievements",
                f"{query} current status"
            ]
            return basic_variants
    
    async def _execute_searches(self, variant_queries: List[str]) -> List[Dict[str, Any]]:
        """
        Execute searches for each variant query.
        
        Args:
            variant_queries: List of search queries to execute
            
        Returns:
            List of search results
        """
        self.update_progress(
            progress=15, 
            step_description="Executing searches for variant queries"
        )
        
        all_search_results = []
        progress_increment = 30 / len(variant_queries)  # Allocate 30% of progress to searches
        
        for i, query in enumerate(variant_queries):
            logger.info(f"Executing search {i+1}/{len(variant_queries)}: '{query}'")
            
            # Create a tool call for this query
            tool_call = {
                "id": f"variant_search_{int(time.time())}_{i}",
                "type": "function",
                "function": {
                    "name": "google_search",
                    "arguments": json.dumps({"query": query})
                }
            }
            
            # Execute the tool call
            tool_result = await self._execute_tool_call(tool_call)
            
            # Add the result to our collection
            all_search_results.append({
                "query": query,
                "result": tool_result.get("content", "No results found.")
            })
            
            # Update progress
            current_progress = 15 + (i + 1) * progress_increment
            self.update_progress(
                progress=int(current_progress),
                step_description=f"Completed search {i+1}/{len(variant_queries)}"
            )
        
        logger.info(f"Completed all {len(variant_queries)} searches")
        return all_search_results
    
    async def _generate_summary(self, query: str, all_search_results: List[Dict[str, Any]], organized_urls: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive summary of the search results.
        
        Args:
            query: The original user query
            all_search_results: List of search results
            organized_urls: List of organized URLs extracted from search results
            
        Returns:
            A comprehensive summary with citations
        """
        self.update_progress(
            progress=50,
            step_description="Generating comprehensive summary of search results"
        )
        
        # Prepare a message with all search results
        summary_messages = self.conversation_history.copy()
        
        # Add a system message with instructions
        summary_messages.append({
            "role": "system",
            "content": """You are tasked with summarizing search results from multiple queries related to the user's original question. 

RESPONSE REQUIREMENTS:
1. Provide an EXTREMELY COMPREHENSIVE and DETAILED summary (at least 1000-1500 words) that includes ALL factual information found in the search results.
2. Include EVERY relevant link from the search results as proper citations.
3. Format your response in a clear, organized manner with multiple sections, subsections, and bullet points.
4. For each piece of information, include a citation in the format [Source: URL].
5. Explore ALL aspects of the topic found in the search results - background, achievements, personal details, professional work, projects, etc.
6. Include direct quotes where relevant, always with proper attribution.
7. IMPORTANT: Do NOT use tool calls in your response. Simply provide a text summary with the information you've found.
8. NEVER make up information not found in the search results.
9. If contradictory information exists, present both sides with their respective sources.
10. End with a "References" section listing all sources used.

Your summary should be MUCH more detailed and comprehensive than a typical response, covering ALL available information from the search results."""
        })
        
        # Add an assistant message explaining what we're doing
        summary_messages.append({
            "role": "assistant",
            "content": f"I'll search for information about '{query}' using multiple related queries to get comprehensive results. I'll provide an extremely detailed summary with proper citations."
        })
        
        # Add all the search results
        for result in all_search_results:
            summary_messages.append({
                "role": "user",
                "content": f"Search results for query: '{result['query']}'\n\n{result['result']}"
            })
        
        # Add information about the organized URLs
        url_info_message = "Here are the organized URLs from the search results:\n\n"
        for url_info in organized_urls:
            url_info_message += f"Title: {url_info['title']}\nURL: {url_info['url']}\nDomain: {url_info['domain']}\n\n"
        
        summary_messages.append({
            "role": "user",
            "content": url_info_message
        })
        
        # Request the summary
        summary_payload = {
            "model": self.model,
            "messages": summary_messages,
            "stream": False,
            "tools": []  # Explicitly disable tools for this request
        }
        
        try:
            logger.info("Generating comprehensive summary of search results")
            summary_response = requests.post(f"{self.api_base_url}/chat/ollama", json=summary_payload)
            summary_response.raise_for_status()
            summary_result = summary_response.json()
            
            final_summary = summary_result.get("message", {}).get("content", "Unable to generate summary.")
            
            # Clean up any tool calls that might still be in the response
            if "[TOOL_CALLS]" in final_summary or "[tool_calls]" in final_summary.lower():
                # Remove everything from [TOOL_CALLS] or [tool_calls] onwards
                if "[TOOL_CALLS]" in final_summary:
                    final_summary = final_summary.split("[TOOL_CALLS]")[0].strip()
                elif "[tool_calls]" in final_summary.lower():
                    final_summary = final_summary.split("[tool_calls]")[0].strip()
            
            # Fix citation formats
            # Replace [REF]X[/REF] format with proper links
            ref_pattern = r'\[REF\](\d+)\[/REF\]'
            ref_matches = re.findall(ref_pattern, final_summary)
            
            # Extract URLs from the search results
            all_urls = []
            for result in all_search_results:
                # Extract URLs using regex
                urls = re.findall(r'https?://[^\s\)"]+', result["result"])
                all_urls.extend(urls)
            
            # Remove duplicates while preserving order
            unique_urls = []
            for url in all_urls:
                if url not in unique_urls:
                    unique_urls.append(url)
            
            # Replace REF tags with actual URLs if possible
            for ref_num in ref_matches:
                try:
                    idx = int(ref_num)
                    if idx < len(unique_urls):
                        url = unique_urls[idx]
                        final_summary = re.sub(r'\[REF\]' + ref_num + r'\[/REF\]', f'[Source: {url}]', final_summary)
                    else:
                        final_summary = re.sub(r'\[REF\]' + ref_num + r'\[/REF\]', '[Source: Citation needed]', final_summary)
                except ValueError:
                    pass
            
            # If the model is still trying to use read_url, we should extract those URLs and include them in the summary
            url_matches = re.findall(r'"url"\s*:\s*"([^"]+)"', final_summary)
            if url_matches:
                # Extract the URLs and add them to the summary
                final_summary = re.sub(r'\[TOOL_CALLS\].*', '', final_summary, flags=re.DOTALL).strip()
                
                # Add the URLs as references
                if "## References" not in final_summary and "# References" not in final_summary:
                    final_summary += "\n\n## Additional References\n"
                    for i, url in enumerate(url_matches):
                        final_summary += f"{i+1}. [{url}]({url})\n"
            
            # Ensure there's a References section if not already present
            if "## References" not in final_summary and "# References" not in final_summary:
                # Generate a formatted references section
                references_section = self._format_references_section(organized_urls)
                final_summary += "\n\n" + references_section
            
            # Add the summary to the conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_summary
            })
            
            self.update_progress(
                progress=90,
                step_description="Completed summary generation"
            )
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the SwarmDreamwalker workflow.
        
        Args:
            query: The user query to process
            **kwargs: Additional parameters
                - model: Override the default model
                - stream: Whether to stream the response (not implemented yet)
                
        Returns:
            A dictionary containing the results of the workflow
        """
        try:
            # Update model if provided
            if "model" in kwargs:
                self.model = kwargs.get("model")
                self.metadata["model"] = self.model
            
            # Start the workflow
            self.update_progress(
                progress=0,
                status="running",
                step_description=f"Starting SwarmDreamwalker workflow for query: {query}"
            )
            
            # Step 1: Generate variant search queries
            variant_queries = await self._generate_variant_queries(query)
            
            # Step 2: Execute searches for each variant query
            all_search_results = await self._execute_searches(variant_queries)
            
            # Step 3: Extract and organize URLs from search results
            self.update_progress(
                progress=45,
                step_description="Extracting and organizing URLs from search results"
            )
            organized_urls = self._extract_urls_from_search_results(all_search_results)
            
            # Step 4: Generate a comprehensive summary
            final_summary = await self._generate_summary(query, all_search_results, organized_urls)
            
            # Complete the workflow
            results = {
                "query": query,
                "variant_queries": variant_queries,
                "search_results_count": len(all_search_results),
                "urls_extracted": len(organized_urls),
                "summary": final_summary,
                "conversation_history": self.conversation_history
            }
            
            return self.complete(results)
            
        except Exception as e:
            logger.error(f"Error executing SwarmDreamwalker workflow: {str(e)}")
            return self.fail(str(e)) 