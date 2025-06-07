#!/usr/bin/env python3
"""
Drummer Search Runner - Implementation for using drummer-search models

This script provides a complete implementation for using the drummer-search
models (3b, 7b, and 24b sizes) with web search capabilities through Ollama's tool calling API.
The implementation includes progress updates, model selection, and strategic backend model use.

Requirements:
- requests library
- The infinite_search.py tool (adapted from the original)
"""

import json
import requests
import asyncio
import sys
import re
import argparse
from typing import List, Dict, Any, Optional, Tuple
import time
import os
from urllib.parse import urlparse

# Import the Tools class from the infinite_search module
# Adjust the import path as needed for your setup
sys.path.append('./api-tools/tools/tools/tools2')
try:
    from infinite_search import Tools
except ImportError:
    print("Error: Could not import Tools from infinite_search.")
    print("Please ensure the infinite_search.py file is in the correct location.")
    print("Expected path: ./api-tools/tools/tools/tools2/infinite_search.py")
    sys.exit(1)

# API settings
API_BASE_URL = "https://api.assisted.space/v2"

# Available drummer-search model variants
DRUMMER_MODELS = {
    "small": "coolhand/drummer-search:3b",
    "medium": "coolhand/drummer-search:7b",
    "large": "coolhand/drummer-search:24b"
}

class DrummerSearchRunner:
    def __init__(self, default_model_size="large"):
        self.tools = Tools()
        self.conversation_history = []
        self.progress = 0
        self.current_step = ""
        
        # Select the default model based on model size
        self.default_model_size = default_model_size
        self.model_name = DRUMMER_MODELS.get(default_model_size, DRUMMER_MODELS["large"])
        
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
    
    def update_progress(self, progress: int, step_description: str):
        """Update and display progress to the user"""
        self.progress = min(max(progress, 0), 100)  # Ensure progress is between 0-100
        self.current_step = step_description
        
        # Display progress bar
        bar_length = 30
        filled_length = int(bar_length * self.progress / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Clear the current line and print progress
        print(f"\r[{bar}] {self.progress}% - {step_description}", end='', flush=True)
        
        # If progress is complete, add a new line
        if self.progress >= 100:
            print()
    
    async def _google_search(self, query: str) -> str:
        """Implementation of the google_search tool"""
        try:
            self.update_progress(self.progress + 2, f"Searching Google for: '{query}'")
            result = await self.tools.google_search(query)
            return result
        except Exception as e:
            return f"Error performing Google search: {str(e)}"
    
    async def _bing_search(self, query: str) -> str:
        """Implementation of the bing_search tool"""
        try:
            self.update_progress(self.progress + 2, f"Searching Bing for: '{query}'")
            result = await self.tools.bing_search(query)
            return result
        except Exception as e:
            return f"Error performing Bing search: {str(e)}"
    
    async def _baidu_search(self, query: str) -> str:
        """Implementation of the baidu_search tool"""
        try:
            self.update_progress(self.progress + 2, f"Searching Baidu for: '{query}'")
            result = await self.tools.baidu_search(query)
            return result
        except Exception as e:
            return f"Error performing Baidu search: {str(e)}"
    
    async def _read_url(self, url: str) -> str:
        """Implementation of the read_url tool"""
        try:
            self.update_progress(self.progress + 1, f"Reading content from: '{url}'")
            result = await self.tools.read_url(url)
            return result
        except Exception as e:
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
        self.update_progress(self.progress + 5, "Extracting URLs from search results")
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
    
    def _select_model_for_task(self, task: str, complexity: int = 1) -> str:
        """
        Strategically select the best model size for the task.
        
        Args:
            task: The task type (e.g., "query_generation", "search", "summarization")
            complexity: The complexity level (1-3, with 3 being most complex)
            
        Returns:
            The model name to use
        """
        # For complex summarization tasks, use the largest model
        if task == "summarization" and complexity >= 2:
            return DRUMMER_MODELS["large"]
        
        # For query generation, the smaller model is often sufficient
        if task == "query_generation" and complexity <= 2:
            return DRUMMER_MODELS["small"]
        
        # For initial search tasks, medium model is a good balance
        if task == "search":
            return DRUMMER_MODELS["medium"]
        
        # Default to the selected default model
        return self.model_name
    
    async def chat_with_model(self, user_message: str, model_size: Optional[str] = None) -> str:
        """
        Send a message to the model and get a response.
        Handles tool calls if the model requests them.
        
        Args:
            user_message: The user's message
            model_size: Optional model size override ("small", "medium", "large")
            
        Returns:
            The model's response
        """
        # Reset progress for this new query
        self.progress = 0
        self.update_progress(0, "Starting search process")
        
        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Determine query complexity to help with model selection
        complexity = min(3, max(1, len(user_message.split()) // 10))
        
        # If model_size is specified, use that model, otherwise use strategic selection
        if model_size and model_size in DRUMMER_MODELS:
            query_model = DRUMMER_MODELS[model_size]
        else:
            query_model = self._select_model_for_task("query_generation", complexity)
        
        # First, ask the model to generate variant search queries
        self.update_progress(5, f"Generating search queries using {query_model.split(':')[1]} model")
        variant_generation_url = f"{API_BASE_URL}/chat/ollama"
        variant_payload = {
            "model": query_model,
            "messages": self.conversation_history + [{
                "role": "system", 
                "content": "Generate five variant search queries based on the user's original query. These should be related but different angles or aspects to explore the topic more comprehensively. Format your response as a JSON array of strings. ONLY respond with the JSON array, nothing else."
            }],
            "stream": False
        }
        
        try:
            # Get variant search queries from the model
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
                        user_message,
                        f"latest information about {user_message}",
                        f"{user_message} background and history",
                        f"{user_message} notable achievements",
                        f"{user_message} current status"
                    ]
            except json.JSONDecodeError:
                # If JSON parsing fails, create some basic variants
                variant_queries = [
                    user_message,
                    f"latest information about {user_message}",
                    f"{user_message} background and history",
                    f"{user_message} notable achievements",
                    f"{user_message} current status"
                ]
            
            # Ensure we have exactly 5 queries
            if len(variant_queries) > 5:
                variant_queries = variant_queries[:5]
            while len(variant_queries) < 5:
                variant_queries.append(f"{user_message} additional information {len(variant_queries) + 1}")
            
            # Print the variant queries
            self.update_progress(15, "Search queries generated")
            print("\n[Using the following search queries:]")
            for i, query in enumerate(variant_queries):
                print(f"  {i+1}. {query}")
            
            # Execute each variant query and collect results
            all_search_results = []
            search_model = self._select_model_for_task("search", complexity)
            
            # Set progress based on number of searches (5% per search × 5 searches = 25%)
            search_progress_total = 25
            search_progress_per_query = search_progress_total / len(variant_queries)
            current_search_progress = 15  # Start from the current progress
            
            for i, query in enumerate(variant_queries):
                self.update_progress(
                    current_search_progress + (search_progress_per_query * i / len(variant_queries)),
                    f"Executing search {i+1}/{len(variant_queries)}: '{query}'"
                )
                
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
            
            # Extract and organize URLs from search results
            self.update_progress(45, "Processing search results")
            organized_urls = self._extract_urls_from_search_results(all_search_results)
            
            # Now, ask the model to summarize all the search results
            self.update_progress(50, "Generating comprehensive summary")
            
            # For summarization, use the largest model for the best results
            summary_model = self._select_model_for_task("summarization", complexity)
            self.update_progress(55, f"Summarizing with {summary_model.split(':')[1]} model")
            
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
                "content": f"I'll search for information about '{user_message}' using multiple related queries to get comprehensive results. I'll provide an extremely detailed summary with proper citations."
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
            
            # Request the summary with progress updates
            self.update_progress(60, "Generating summary from search results")
            summary_payload = {
                "model": summary_model,
                "messages": summary_messages,
                "stream": False,
                "tools": []  # Explicitly disable tools for this request
            }
            
            # Update progress as we wait for the summary
            for i in range(60, 90, 5):
                self.update_progress(i, "Generating comprehensive summary...")
                summary_response = requests.post(variant_generation_url, json=summary_payload)
                if summary_response.ok:
                    break
                time.sleep(2)  # Short delay between progress updates
            
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
            
            self.update_progress(90, "Finalizing summary and formatting references")
            
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
            
            self.update_progress(100, "Search and summary complete")
            return final_summary
                
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with API: {str(e)}"
            print(error_message)
            return error_message
    
    def save_conversation(self, filename: str = "conversation_history.json"):
        """Save the conversation history to a file"""
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        print(f"\nConversation saved to {filename}")
    
    async def run_interactive(self):
        """Run an interactive session with the model"""
        print("\n" + "="*80)
        print("Drummer Search Runner - Web Search & Summary Expert".center(80))
        print("="*80)
        print(f"\nUsing model: {self.model_name}")
        print("\nThis tool allows you to interact with the model and use web search capabilities.")
        print("Type 'exit' or 'quit' to end the session.")
        print("Type 'save' to save the conversation history.")
        print("Type 'clear' to start a new conversation.")
        print("Type 'model small|medium|large' to change the model size.\n")
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for special commands
            if user_input.lower() in ['exit', 'quit']:
                print("\nThank you for using Drummer Search Runner. Goodbye!")
                break
            elif user_input.lower() == 'save':
                filename = input("Enter filename to save (default: conversation_history.json): ").strip()
                if not filename:
                    filename = "conversation_history.json"
                self.save_conversation(filename)
                continue
            elif user_input.lower() == 'clear':
                self.conversation_history = []
                print("\nConversation history cleared. Starting a new conversation.")
                continue
            elif user_input.lower().startswith('model '):
                # Change the model size
                model_size = user_input.lower().split('model ')[1].strip()
                if model_size in ["small", "medium", "large"]:
                    self.default_model_size = model_size
                    self.model_name = DRUMMER_MODELS[model_size]
                    print(f"\nModel changed to {self.model_name}")
                else:
                    print(f"\nInvalid model size. Available options: small, medium, large")
                continue
            
            # Process the user input with the model
            print("\nProcessing your request...")
            start_time = time.time()
            
            response = await self.chat_with_model(user_input)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Display the response
            print(f"\nResponse: {response}")
            print(f"\n(Processing time: {processing_time:.2f} seconds)")

def check_model_availability():
    """Check if the API is accessible and the drummer-search models are available"""
    try:
        # Check if the API is accessible
        response = requests.get(f"{API_BASE_URL}/models/ollama")
        response.raise_for_status()
        
        # Parse the response
        models_data = response.json()
        
        # Check if models exist in the available models
        if isinstance(models_data, list):
            models = models_data
        else:
            # If the response is not a list, try to access the models property
            models = models_data.get("models", [])
        
        # Check for each drummer-search model
        available_models = []
        for size, model_name in DRUMMER_MODELS.items():
            if any(model.get("id") == model_name for model in models):
                available_models.append((size, model_name))
        
        if not available_models:
            print(f"Warning: No drummer-search models found. Available models:")
            for model in models:
                print(f"  - {model.get('id')}")
            print("\nThe script will continue, but you may encounter errors.")
            return True
        
        print("Available drummer-search models:")
        for size, model_name in available_models:
            print(f"  - {size}: {model_name}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to API at {API_BASE_URL}")
        print(f"Error details: {str(e)}")
        return False

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Drummer Search - Web search and summary tool")
    parser.add_argument('--model', choices=['small', 'medium', 'large'], default='large',
                        help='Model size to use (small=3b, medium=7b, large=24b)')
    parser.add_argument('--query', type=str, help='Run a single query instead of interactive mode')
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Check if the API is accessible
    if not check_model_availability():
        sys.exit(1)
    
    # Create the runner with selected model size
    runner = DrummerSearchRunner(default_model_size=args.model)
    
    # Run in interactive mode or execute a single query
    if args.query:
        result = asyncio.run(runner.chat_with_model(args.query))
        print(f"\nResult:\n{result}")
    else:
        # Run the interactive session
        asyncio.run(runner.run_interactive()) 