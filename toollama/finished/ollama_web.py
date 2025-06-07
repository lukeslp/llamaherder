#!/usr/bin/env python3
"""Web search and scraping tool using Ollama with multiple backends."""

import json
import asyncio
import requests
from typing import Dict, Any, Optional, List
from tools.llm_tool_webscrape import Tools as ScrapeTools
from tools.llm_tool_infinite_search import Tools as SearchTools
from tools.llm_tool_knowledge import Tools as KnowledgeTools
import re
import os

class OllamaWebUser:
    def __init__(self, model="belter-web", base_url="http://localhost:11434/api/chat"):
        """Initialize the web tools with model and various backends."""
        self.model = model
        self.base_url = base_url
        self.scrape_tool = ScrapeTools()
        self.search_tool = SearchTools()
        self.knowledge_tool = KnowledgeTools()
        print("\nInitialized web tools")

    def normalize_url(self, url: str) -> str:
        """Ensure URL has proper protocol"""
        if not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url

    def generate(self, prompt: str) -> str:
        """Generate a response from Ollama"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": """You are a web search and scraping assistant. 
                Available tools:
                1. web_scrape: Scrape content from a URL
                   Parameters: {"url": "example.com"}
                2. google_search: Search using Google
                   Parameters: {"query": "search terms"}
                3. bing_search: Search using Bing
                   Parameters: {"query": "search terms"}
                4. perplexity_search: Search using Perplexity AI
                   Parameters: {"query": "search terms", "mode": "search|academic|writing|analysis"}
                
                Respond with a JSON object containing:
                {
                    "tool": "tool_name",
                    "parameters": {
                        // tool specific parameters
                    }
                }"""},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            print("\nRaw LLM Response:", repr(content))
            
            # Clean and parse JSON response
            content = self._clean_json_response(content)
            
            try:
                parsed = json.loads(content)
                
                # Normalize the response based on tool type
                clean_response = {
                    "tool": parsed.get("tool", ""),
                    "parameters": {}
                }
                
                if parsed.get("tool") == "web_scrape":
                    clean_response["parameters"]["url"] = self.normalize_url(
                        parsed.get("parameters", {}).get("url", "")
                    )
                elif parsed.get("tool") in ["google_search", "bing_search", "perplexity_search"]:
                    clean_response["parameters"] = parsed.get("parameters", {})
                    if "mode" not in clean_response["parameters"] and parsed.get("tool") == "perplexity_search":
                        clean_response["parameters"]["mode"] = "search"
                
                print("Final Response:", json.dumps(clean_response, indent=2))
                return json.dumps(clean_response)
                
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {str(e)}")
                # Handle direct URL inputs
                if isinstance(prompt, str) and (prompt.startswith("http") or "." in prompt):
                    return json.dumps({
                        "tool": "web_scrape",
                        "parameters": {
                            "url": self.normalize_url(prompt)
                        }
                    })
                raise
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except Exception as e:
            print(f"Error parsing response: {e}")
            raise

    def _clean_json_response(self, content: str) -> str:
        """Clean and format JSON response from LLM"""
        content = content.encode().decode('unicode_escape')
        
        # Extract JSON part
        json_start = content.find("{")
        json_end = content.rfind("}")
        if json_start >= 0 and json_end >= 0:
            content = content[json_start:json_end + 1]
        
        # Basic cleaning
        content = (content.replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("'", '"'))
        
        # Fix JSON formatting issues
        content = (content.replace('\\"', '"')
                        .replace('""', '"')
                        .strip())
        
        # Remove spaces between JSON elements
        content = re.sub(r'\s*:\s*', ':', content)
        content = re.sub(r'\s*,\s*', ',', content)
        content = re.sub(r'\s*{\s*', '{', content)
        content = re.sub(r'\s*}\s*', '}', content)
        
        return content

    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "web_scrape":
                url = params.get('url', '')
                if not url:
                    return "Error: No URL provided"
                print(f"\nScraping URL: {url}")
                return await self.scrape_tool.web_scrape(url)
                
            elif tool_name == "google_search":
                query = params.get('query', '')
                if not query:
                    return "Error: No search query provided"
                print(f"\nPerforming Google search: {query}")
                return await self.search_tool.google_search(query)
                
            elif tool_name == "bing_search":
                query = params.get('query', '')
                if not query:
                    return "Error: No search query provided"
                print(f"\nPerforming Bing search: {query}")
                return await self.search_tool.bing_search(query)
                
            elif tool_name == "perplexity_search":
                query = params.get('query', '')
                mode = params.get('mode', 'search')
                if not query:
                    return "Error: No search query provided"
                print(f"\nPerforming Perplexity search: {query} (mode: {mode})")
                return self.knowledge_tool.search_perplexity(query, mode)
            
            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"

    async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)
            
            # Parse and execute the tool call
            tool_call = json.loads(response)
            result = await self.execute_tool(tool_call)
            
            return result
            
        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
            return "An error occurred while processing your request."

async def main():
    """Main function to run the web tools."""
    web_tools = OllamaWebUser()
    
    print("\nWeb Search and Scraping Tool")
    print("Commands:")
    print("- Direct URL: example.com")
    print("- Scrape: scrape example.com")
    print("- Google Search: search python programming")
    print("- Bing Search: bing machine learning")
    print("- Perplexity: perplexity quantum computing")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("\nEnter request: ").strip()
            if user_input.lower() == 'quit':
                break
                
            result = await web_tools.run_interaction(user_input)
            print(f"\n{result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())