"""
Tool-using setup for Ollama with Infinite Search integration
"""

import json
import requests
import aiohttp
from typing import Dict, Any, List
from tools.llm_tool_infinite_search import Tools
import re
import asyncio
from bs4 import BeautifulSoup
import os
from datetime import datetime

class OllamaInfiniteUser:
    def __init__(self, model: str = "belter-searcher:latest"):
        self.model = model
        self.search_tool = Tools()
        # Configure search engine URL and settings
        self.search_tool.valves.SEARXNG_URL = "https://searx.be/search"
        self.search_tool.valves.TIMEOUT = 60
        print(f"\nInitialized with search URL: {self.search_tool.valves.SEARXNG_URL}")
        self.base_url = "https://ai.assisted.space/api/chat"
        self.deepseek_url = "https://ai.assisted.space/api/chat"
        self.results_dir = "search_results"
        os.makedirs(self.results_dir, exist_ok=True)
        self.session = None
        
    async def ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def async_post(self, url: str, json_data: dict) -> dict:
        """Make async POST request"""
        session = await self.ensure_session()
        async with session.post(url, json=json_data) as response:
            return await response.json()

    def generate(self, prompt: str) -> str:
        """Generate a response from Ollama"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            print("\nLLM Response:", content)  # Debug print
            
            # Handle non-JSON responses
            if "Generate 4 different" in prompt:
                # For adjacent queries, return raw lines
                return content
                
            # For other responses requiring JSON
            try:
                # Clean up the response to ensure valid JSON
                content = content.strip()
                if not content.startswith("{"):
                    content = "{"
                if not content.endswith("}"):
                    content += "}"
                    
                # Validate JSON structure
                json.loads(content)
                return content
                
            except json.JSONDecodeError:
                print(f"Failed to parse JSON, returning raw content: {content}")
                return content
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
    
    def normalize_url(self, url: str) -> str:
        """Ensure URL has proper format"""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def extract_urls_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract URLs and titles from the search result text"""
        results = []
        lines = text.split('\n')
        current_title = ""
        
        for line in lines:
            if line.strip().startswith('http'):
                if current_title:
                    results.append({
                        "title": current_title,
                        "url": line.strip()
                    })
                    current_title = ""
            else:
                current_title = line.strip()
        
        return results
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            print(f"\nExecuting tool: {tool_name}")
            print(f"Parameters: {params}")
            
            if tool_name == "google_search":
                result = await self.search_tool.google_search(**params)
                print("\nRaw Google search result (first 1000 chars):")
                print(result[:1000])
                print("\nSearch result length:", len(result))
                print("\nSearch result type:", type(result))
                
                # Extract actual content from the search result
                try:
                    soup = BeautifulSoup(result, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text(separator='\n', strip=True)
                    
                    # Clean up text
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    text = '\n'.join(lines)
                    
                    return {"content": text, "type": "search"}
                except Exception as e:
                    print(f"Error extracting content: {e}")
                    return {"content": result, "type": "search"}
                    
            elif tool_name == "bing_search":
                result = await self.search_tool.bing_search(**params)
                print("\nRaw Bing search result (first 1000 chars):")
                print(result[:1000])
                print("\nSearch result length:", len(result))
                print("\nSearch result type:", type(result))
                
                # Extract actual content from the search result
                try:
                    soup = BeautifulSoup(result, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text(separator='\n', strip=True)
                    
                    # Clean up text
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    text = '\n'.join(lines)
                    
                    return {"content": text, "type": "search"}
                except Exception as e:
                    print(f"Error extracting content: {e}")
                    return {"content": result, "type": "search"}
                    
            elif tool_name == "baidu_search":
                result = await self.search_tool.baidu_search(**params)
                print("\nRaw Baidu search result (first 1000 chars):")
                print(result[:1000])
                print("\nSearch result length:", len(result))
                print("\nSearch result type:", type(result))
                
                # Extract actual content from the search result
                try:
                    soup = BeautifulSoup(result, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text(separator='\n', strip=True)
                    
                    # Clean up text
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    text = '\n'.join(lines)
                    
                    return {"content": text, "type": "search"}
                except Exception as e:
                    print(f"Error extracting content: {e}")
                    return {"content": result, "type": "search"}
                    
            elif tool_name == "read_url":
                if "url" in params:
                    params["url"] = self.normalize_url(params["url"])
                result = await self.search_tool.read_url(**params)
                return {"content": result, "type": "article"}
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            print(f"Error type: {type(e)}")
            return {"error": f"Error executing {tool_name}: {str(e)}"}

    def format_search_result(self, result: Dict[str, Any]) -> str:
        """Format the search or article results for display"""
        if "error" in result:
            return f"Error: {result['error']}"
            
        content = result.get("content", "")
        result_type = result.get("type", "unknown")
        
        print("\nFormatting result type:", result_type)
        print("\nRaw content preview (first 1000 chars):", content[:1000])
        print("\nContent length:", len(content))
        print("\nContent type:", type(content))
        
        if result_type == "search":
            # Extract the main content before any instruction tags
            search_section = content
            
            # Check for instruction tags
            s_pos = search_section.find("<s>")
            sys_pos = search_section.find("<system>")
            
            print(f"\nTag positions - <s>: {s_pos}, <system>: {sys_pos}")
            
            # Extract content before the first instruction tag
            if s_pos >= 0 and (sys_pos < 0 or s_pos < sys_pos):
                search_section = search_section[:s_pos]
            elif sys_pos >= 0:
                search_section = search_section[:sys_pos]
                
            search_section = search_section.strip()
            
            print("\nProcessed search section preview (first 1000 chars):", search_section[:1000])
            print("\nProcessed section length:", len(search_section))
            
            results = []
            
            # First try HTML parsing
            try:
                soup = BeautifulSoup(search_section, 'html.parser')
                
                # Try to find results in different HTML structures
                results_divs = soup.find_all(['div', 'article', 'section'])
                print(f"\nFound {len(results_divs)} potential result containers")
                
                for div in results_divs:
                    try:
                        # Look for title and URL
                        link = div.find('a', href=True)
                        if not link:
                            continue
                            
                        url = link['href']
                        title = link.get_text(strip=True)
                        
                        # Get content from the div
                        content = div.get_text(strip=True)
                        if title in content:
                            content = content.replace(title, '', 1).strip()
                        
                        print(f"\nProcessing result - Title: {title}, URL: {url}")
                        
                        # Skip if it looks like a navigation link or empty title
                        if not title or any(skip in title.lower() for skip in ["search results", "about", "images", "videos", "maps", "news"]):
                            print("Skipping navigation/empty link")
                            continue
                            
                        # Only include links that look like real URLs
                        if url.startswith(('http://', 'https://')):
                            results.append({
                                "title": title,
                                "url": url,
                                "content": content
                            })
                            print(f"Added result with content length: {len(content)}")
                    except Exception as e:
                        print(f"Error parsing div: {e}")
                        continue
                        
                # If no results found, try simpler link-based approach
                if not results:
                    links = soup.find_all('a', href=True)
                    print(f"\nFalling back to link search, found {len(links)} links")
                    
                    for link in links:
                        try:
                            url = link['href']
                            title = link.get_text(strip=True)
                            
                            # Get surrounding text content
                            parent = link.find_parent(['p', 'div', 'section', 'article'])
                            content = parent.get_text(strip=True) if parent else ""
                            if title in content:
                                content = content.replace(title, '', 1).strip()
                            
                            print(f"\nProcessing link - Title: {title}, URL: {url}")
                            
                            # Skip navigation/empty links
                            if not title or any(skip in title.lower() for skip in ["search results", "about", "images", "videos", "maps", "news"]):
                                print("Skipping navigation/empty link")
                                continue
                                
                            # Only include real URLs
                            if url.startswith(('http://', 'https://')):
                                results.append({
                                    "title": title,
                                    "url": url,
                                    "content": content
                                })
                                print(f"Added result with content length: {len(content)}")
                        except Exception as e:
                            print(f"Error parsing link: {e}")
                            continue
                            
            except Exception as e:
                print(f"Error during HTML parsing: {e}")
            
            # If HTML parsing didn't find results, try text-based parsing
            if not results:
                print("\nTrying text-based parsing...")
                sections = re.split(r'\n\s*\n', search_section)  # Split on double newlines
                
                for section in sections:
                    lines = section.strip().split('\n')
                    if not lines:
                        continue
                        
                    current_title = None
                    current_url = None
                    current_content = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        if line.startswith(('http://', 'https://')):
                            current_url = line
                        elif not current_title:
                            current_title = line
                        else:
                            current_content.append(line)
                    
                    if current_title and current_url:
                        content = "\n".join(current_content)
                        results.append({
                            "title": current_title,
                            "url": current_url,
                            "content": content
                        })
                        print(f"Added text result - Title: {current_title}, Content length: {len(content)}")
            
            print("\nExtracted results:", results)
            
            if not results:
                # Try one final attempt to extract any URLs with surrounding text
                print("\nFinal attempt - looking for any URLs with context...")
                url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+' 
                urls = re.findall(url_pattern, search_section)
                
                for url in urls:
                    # Get some surrounding context
                    start_idx = search_section.find(url)
                    if start_idx >= 0:
                        context_start = max(0, start_idx - 200)
                        context_end = min(len(search_section), start_idx + len(url) + 200)
                        context = search_section[context_start:context_end].strip()
                        
                        # Try to find a title in the context
                        lines = context.split('\n')
                        title = next((line.strip() for line in lines if line.strip() and url not in line), url)
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "content": context
                        })
                        print(f"Added URL with context - URL: {url}")
                
            if not results:
                return "No relevant results could be extracted."
            
            # Format output with full content
            output = []
            for idx, item in enumerate(results[:5], 1):
                output.append(f"\nResult {idx}:")
                output.append(f"Title: {item['title']}")
                output.append(f"URL: {item['url']}")
                if item.get('content'):
                    # Clean up content
                    content = item['content']
                    content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                    content = content.strip()
                    output.append(f"Content:\n{content}")  # Include full content
            
            return "\n".join(output)
            
        elif result_type == "article":
            if not content:
                return "No content could be extracted from the article."
            
            # Remove system instructions
            content = re.sub(r"<s>.*?</s>", "", content, flags=re.DOTALL)
            content = re.sub(r"<system>.*?</system>", "", content, flags=re.DOTALL)
            
            # Return full content
            return f"Article Content:\n\n{content}"
            
        return "Unexpected result format"

    async def generate_adjacent_queries(self, query: str, initial_results: str) -> List[str]:
        """Generate related search queries using context from initial search"""
        prompt = f"""Based on these initial search results about '{query}', generate 4 specific follow-up search queries to gather additional relevant information. Focus on gaps in the current results and important aspects not yet covered.

Initial results:
{initial_results}

Return only the queries, one per line, no numbering or extra text."""
        
        try:
            response = self.generate(prompt)
            queries = []
            for line in response.split('\n'):
                line = line.strip()
                line = re.sub(r'^[\d\.-]\s*', '', line)
                if line and len(queries) < 4:  # Get exactly 4 queries
                    queries.append(line)
            
            print("\nGenerated follow-up queries:", queries)
            # If we don't get enough queries, add generic ones to reach 4
            while len(queries) < 4:
                if len(queries) == 0:
                    queries.append(f"{query} latest developments")
                elif len(queries) == 1:
                    queries.append(f"{query} background information")
                elif len(queries) == 2:
                    queries.append(f"{query} analysis")
                else:
                    queries.append(f"{query} details")
            return queries
            
        except Exception as e:
            print(f"Error generating queries: {e}")
            return [
                f"{query} latest developments",
                f"{query} background information",
                f"{query} analysis",
                f"{query} details"
            ]

    async def parallel_search(self, query: str) -> List[Dict[str, Any]]:
        """Execute initial search followed by parallel searches including arxiv, wiki, and scraping"""
        print(f"\n🔍 Starting search process for: '{query}'")
        
        # Initial search
        print("\n📚 Performing initial search...")
        initial_tool_call = {
            "tool": "google_search",
            "parameters": {"query": query}
        }
        initial_result = await self.execute_tool(initial_tool_call)
        
        # Save initial results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        initial_filename = f"{self.results_dir}/search_{timestamp}_0.txt"
        saved_files = []
        
        try:
            with open(initial_filename, 'w', encoding='utf-8') as f:
                f.write(f"Query: {query}\n\n")
                f.write(self.format_search_result(initial_result))
            saved_files.append(initial_filename)
            print(f"  ✅ Saved initial results to {initial_filename}")
            
            # Generate contextual queries based on initial results
            print("\n📚 Generating follow-up queries...")
            adjacent_queries = await self.generate_adjacent_queries(query, self.format_search_result(initial_result))
            
            # Extract potential URLs to scrape from initial results
            urls_to_scrape = self.extract_important_urls(self.format_search_result(initial_result))
            
            # Prepare all parallel tasks
            tasks = []
            
            # Add follow-up search tasks
            for i, q in enumerate(adjacent_queries):
                tasks.append({
                    "type": "google",
                    "task": self.execute_tool({
                        "tool": "google_search",
                        "parameters": {"query": q}
                    }),
                    "query": q,
                    "index": i + 1
                })
            
            # Add arxiv search task using belter-nerder
            tasks.append({
                "type": "arxiv",
                "task": self.async_post(
                    self.base_url,
                    {
                        "model": "belter-nerder:latest",
                        "messages": [{"role": "user", "content": f"Search arxiv for: {query}"}],
                        "stream": False,
                        "context_length": 8192,  # Maximum context length
                        "num_predict": 4096  # Maximum response length
                    }
                ),
                "query": f"arxiv: {query}",
                "index": len(adjacent_queries) + 1
            })
            
            # Add wiki search task using belter-reader
            tasks.append({
                "type": "wiki",
                "task": self.async_post(
                    self.base_url,
                    {
                        "model": "belter-reader:latest",
                        "messages": [{"role": "user", "content": f"Search Wikipedia for: {query}"}],
                        "stream": False,
                        "context_length": 8192,
                        "num_predict": 4096
                    }
                ),
                "query": f"wiki: {query}",
                "index": len(adjacent_queries) + 2
            })
            
            # Add URL scraping tasks using belter-scraper
            for i, url in enumerate(urls_to_scrape[:2]):  # Limit to top 2 URLs
                tasks.append({
                    "type": "scrape",
                    "task": self.async_post(
                        self.base_url,
                        {
                            "model": "belter-scraper:latest",
                            "messages": [{"role": "user", "content": f"Scrape and summarize: {url}"}],
                            "stream": False,
                            "context_length": 8192,
                            "num_predict": 4096
                        }
                    ),
                    "query": f"scrape: {url}",
                    "index": len(adjacent_queries) + 3 + i
                })
            
            print("\n⚡ Executing all parallel searches...")
            results = await asyncio.gather(*[t["task"] for t in tasks], return_exceptions=True)
            
            # Save all results
            for i, (task, result) in enumerate(zip(tasks, results)):
                if isinstance(result, Exception):
                    print(f"  ❌ {task['type'].title()} search {task['index']} failed: {str(result)}")
                    continue
                
                filename = f"{self.results_dir}/search_{timestamp}_{task['index']}.txt"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Query: {task['query']}\n\n")
                        if task['type'] in ['arxiv', 'wiki', 'scrape']:
                            content = result.get("message", {}).get("content", "")
                            f.write(content)
                        else:
                            f.write(self.format_search_result(result))
                    saved_files.append(filename)
                    print(f"  ✅ Saved {task['type']} results for '{task['query']}' to {filename}")
                except Exception as e:
                    print(f"  ❌ Failed to save {task['type']} results for '{task['query']}': {str(e)}")
            
            return saved_files
            
        except Exception as e:
            print(f"  ❌ Error in parallel search: {str(e)}")
            if saved_files:
                return saved_files
            return []
            
    def extract_important_urls(self, text: str) -> List[str]:
        """Extract important URLs from search results for scraping"""
        urls = []
        soup = BeautifulSoup(text, 'html.parser')
        
        # Find all links
        for link in soup.find_all('a', href=True):
            url = link['href']
            # Skip search engines, social media, etc.
            if any(domain in url.lower() for domain in ['google', 'facebook', 'twitter', 'youtube', 'linkedin', 'instagram']):
                continue
            if url.startswith(('http://', 'https://')):
                urls.append(url)
        
        return urls[:2]  # Return top 2 most relevant URLs

    async def synthesize_results(self, files: List[str], original_query: str) -> str:
        """Use Ollama to synthesize search results into a comprehensive report"""
        print(f"\n🤖 Starting synthesis of {len(files)} result files...")
        
        # Collect all search results
        all_content = []
        total_chars = 0
        max_chars = 32000  # Set a reasonable limit for context
        
        print("\n📊 Processing search results:")
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        print(f"  ⚠️ Empty content in {file}")
                        continue
                        
                    # Basic content validation
                    if len(content) < 50:  # Suspiciously short content
                        print(f"  ⚠️ Very short content in {file}: {content}")
                        continue
                        
                    # Process and clean the content
                    content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                    content = re.sub(r'<[^>]+>', '', content)  # Remove HTML tags
                    
                    # Add source marker
                    content = f"[Source: {os.path.basename(file)}]\n{content}"
                    
                    total_chars += len(content)
                    all_content.append(content)
                    print(f"  ✅ Processed {file} ({len(content)} chars)")
            except Exception as e:
                print(f"  ❌ Failed to read {file}: {str(e)}")
        
        if not all_content:
            print("❌ No valid content available for synthesis")
            return "Error: No valid search results were available for synthesis."
        
        print(f"\n📈 Total content size: {total_chars} characters")
        
        # Combine and truncate content if necessary
        combined_content = "\n\n===\n\n".join(all_content)
        if total_chars > max_chars:
            print(f"⚠️ Content exceeds {max_chars} chars, truncating...")
            combined_content = combined_content[:max_chars] + "\n...[truncated]"
        
        print("\n🔍 Validating final content...")
        if not combined_content.strip():
            print("❌ Final content is empty")
            return "Error: Failed to prepare content for synthesis."
            
        # Prepare prompt with explicit instructions
        prompt = f"""Based on the search results below about '{original_query}', provide a comprehensive analysis.
Focus on extracting factual information and providing clear citations.

Required sections:
1. Key Findings
- Main themes and patterns
- Important facts and details
- Notable insights

2. Analysis
- How the sources complement each other
- Any gaps or inconsistencies
- Context and background

3. Summary and Conclusions

Here are the search results to analyze:

{combined_content}

Remember to:
- Cite sources when referencing specific information
- Focus on factual information
- Highlight any contradictions or uncertainties
- Provide context where needed"""

        print("\n📝 Preparing API request...")
        print(f"Prompt length: {len(prompt)} characters")
        
        try:
            print("\n🚀 Making request to API...")
            response = requests.post(
                self.deepseek_url,
                json={
                    "model": "deepseek-r1:8b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a research assistant tasked with analyzing and synthesizing search results. Focus on extracting factual information and providing clear citations."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.2,
                    "stream": True,
                    "context_length": 16384,  # Maximum context length for deepseek
                    "num_predict": 8192  # Maximum response length
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=120,  # Increased timeout for longer responses
                stream=True
            )
            
            print(f"\n📡 Response status: {response.status_code}")
            
            if response.status_code != 200:
                error_text = next(response.iter_lines())[:500]
                print(f"❌ Error response: {error_text}")
                return f"Error: API returned status {response.status_code}"
            
            # Stream the response in real-time
            content = []
            print("\n🤖 Synthesis response:")
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode('utf-8'))
                    if data.get('message', {}).get('content'):
                        chunk = data['message']['content']
                        content.append(chunk)
                        print(chunk, end='', flush=True)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"\n⚠️ Error processing chunk: {e}")
                    continue
            
            if not content:
                print("\n❌ No content extracted from response")
                return "Error: No content could be extracted from response"
            
            result = ''.join(content)
            print("\n\n✅ Successfully synthesized results")
            return result
            
        except requests.exceptions.Timeout:
            print("\n❌ Request timed out")
            return "Error: The request timed out. Please try again."
        except Exception as e:
            print(f"\n❌ Synthesis error: {str(e)}")
            print(f"Error type: {type(e)}")
            return f"Error during synthesis: {str(e)}"

    async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with parallel searches and synthesis"""
        try:
            print("\n🚀 Starting new interaction...")
            print(f"Query: '{user_input}'")
            
            # Step 1: Initial search
            print("\n📚 Performing initial search...")
            initial_tool_call = {
                "tool": "google_search",
                "parameters": {"query": user_input}
            }
            initial_result = await self.execute_tool(initial_tool_call)
            
            # Save initial results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            initial_filename = f"{self.results_dir}/search_{timestamp}_0.txt"
            saved_files = []
            
            with open(initial_filename, 'w', encoding='utf-8') as f:
                f.write(f"Query: {user_input}\n\n")
                f.write(self.format_search_result(initial_result))
            saved_files.append(initial_filename)
            print(f"  ✅ Saved initial results to {initial_filename}")
            
            # Step 2: Generate contextual queries
            print("\n📚 Generating follow-up queries...")
            adjacent_queries = await self.generate_adjacent_queries(user_input, self.format_search_result(initial_result))
            urls_to_scrape = self.extract_important_urls(self.format_search_result(initial_result))
            
            # Step 3: Prepare all parallel tasks
            parallel_tasks = []
            
            # Add follow-up search tasks
            for i, q in enumerate(adjacent_queries):
                parallel_tasks.append({
                    "type": "google",
                    "task": self.execute_tool({
                        "tool": "google_search",
                        "parameters": {"query": q}
                    }),
                    "query": q,
                    "index": i + 1
                })
            
            # Add specialized agent tasks
            parallel_tasks.extend([
                {
                    "type": "arxiv",
                    "task": self.async_post(
                        self.base_url,
                        {
                            "model": "belter-nerder:latest",
                            "messages": [{"role": "user", "content": f"Search arxiv for: {user_input}"}],
                            "stream": False,
                            "context_length": 8192,
                            "num_predict": 4096
                        }
                    ),
                    "query": f"arxiv: {user_input}",
                    "index": len(adjacent_queries) + 1
                },
                {
                    "type": "wiki",
                    "task": self.async_post(
                        self.base_url,
                        {
                            "model": "belter-reader:latest",
                            "messages": [{"role": "user", "content": f"Search Wikipedia for: {user_input}"}],
                            "stream": False,
                            "context_length": 8192,
                            "num_predict": 4096
                        }
                    ),
                    "query": f"wiki: {user_input}",
                    "index": len(adjacent_queries) + 2
                }
            ])
            
            # Add URL scraping tasks
            for i, url in enumerate(urls_to_scrape[:2]):
                parallel_tasks.append({
                    "type": "scrape",
                    "task": self.async_post(
                        self.base_url,
                        {
                            "model": "belter-scraper:latest",
                            "messages": [{"role": "user", "content": f"Scrape and summarize: {url}"}],
                            "stream": False,
                            "context_length": 8192,
                            "num_predict": 4096
                        }
                    ),
                    "query": f"scrape: {url}",
                    "index": len(adjacent_queries) + 3 + i
                })
            
            # Step 4: Execute all parallel tasks and wait for completion
            print("\n⚡ Executing all parallel searches...")
            parallel_results = await asyncio.gather(*[t["task"] for t in parallel_tasks], return_exceptions=True)
            
            # Step 5: Save all parallel results
            print("\n💾 Saving parallel search results...")
            for task, result in zip(parallel_tasks, parallel_results):
                if isinstance(result, Exception):
                    print(f"  ❌ {task['type'].title()} search {task['index']} failed: {str(result)}")
                    continue
                
                filename = f"{self.results_dir}/search_{timestamp}_{task['index']}.txt"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Query: {task['query']}\n\n")
                        if task['type'] in ['arxiv', 'wiki', 'scrape']:
                            content = result.get("message", {}).get("content", "")
                            f.write(content)
                        else:
                            f.write(self.format_search_result(result))
                    saved_files.append(filename)
                    print(f"  ✅ Saved {task['type']} results for '{task['query']}' to {filename}")
                except Exception as e:
                    print(f"  ❌ Failed to save {task['type']} results for '{task['query']}': {str(e)}")
            
            # Step 6: Only proceed to synthesis after all results are saved
            if not saved_files:
                return "No search results were generated."
            
            print(f"\n📊 Retrieved {len(saved_files)} result files")
            print("\n🔄 All searches complete, proceeding to synthesis...")
            
            # Step 7: Final synthesis
            final_report = await self.synthesize_results(saved_files, user_input)
            
            # Clean up
            if self.session:
                await self.session.close()
                self.session = None
            
            print("\n✨ Interaction complete")
            return final_report
            
        except Exception as e:
            print(f"\n❌ Error in run_interaction:")
            print(f"Error type: {type(e)}")
            print(f"Error details: {str(e)}")
            if self.session:
                await self.session.close()
                self.session = None
            return "An error occurred while processing your request."

async def main():
    print("\nInfinite Search Tool")
    print("Commands:")
    print("- Google search: find latest AI news")
    print("- Bing search: search WCAG documentation")
    print("- Baidu search: search Chinese tech news")
    print("- Read URL: read https://example.com/article")
    print("Type 'quit' to exit\n")
    
    agent = OllamaInfiniteUser()
    while True:
        try:
            user_input = input("\nEnter request: ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                break
                
            response = await agent.run_interaction(user_input)
            print("\n" + response)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 