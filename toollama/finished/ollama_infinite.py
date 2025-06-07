"""
Tool-using setup for Ollama with Infinite Search integration
"""

import json
import requests
from typing import Dict, Any, List
from tools.llm_tool_infinite_search import Tools
import re
import asyncio
from bs4 import BeautifulSoup

class OllamaInfiniteUser:
    def __init__(self, model: str = "belter-infinite"):
        self.model = model
        self.search_tool = Tools()
        # Configure search engine URL and settings
        self.search_tool.valves.SEARXNG_URL = "https://searx.be/search"
        self.search_tool.valves.TIMEOUT = 60
        print(f"\nInitialized with search URL: {self.search_tool.valves.SEARXNG_URL}")
        self.base_url = "http://localhost:11434/api/chat"
        
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
            
            # Ensure we have a complete JSON object
            if not content.startswith("{"):
                content = "{"
            if not content.endswith("}"):
                content += "}"
                
            # Validate JSON structure
            json.loads(content)
            return content
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {content}")
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
                print("\nRaw search result:")
                print(result)
                return {"content": result, "type": "search"}
            elif tool_name == "bing_search":
                result = await self.search_tool.bing_search(**params)
                print("\nRaw search result:")
                print(result)
                return {"content": result, "type": "search"}
            elif tool_name == "baidu_search":
                result = await self.search_tool.baidu_search(**params)
                print("\nRaw search result:")
                print(result)
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
        
        if result_type == "search":
            # First, try to find the search results section
            search_section = None
            content_parts = content.split("<system>")
            
            # Look for the part before the first <system> tag
            if content_parts:
                search_section = content_parts[0].strip()
            
            print("\nSearch section:", search_section)
            
            if not search_section:
                return "No search results found."
            
            # Extract URLs and titles
            lines = search_section.split('\n')
            results = []
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('http'):
                    if current_item.get('title'):
                        current_item['url'] = line
                        results.append(current_item.copy())
                        current_item = {}
                else:
                    current_item['title'] = line
            
            # Add the last item if it has both title and URL
            if current_item.get('title') and current_item.get('url'):
                results.append(current_item)
            
            print("\nExtracted results:", results)
            
            if not results:
                return "No relevant results could be extracted."
            
            # Format output
            output = ["Search Results:"]
            for idx, item in enumerate(results[:5], 1):
                output.append(f"\n{idx}. {item['title']}")
                output.append(f"   URL: {item['url']}")
            
            return "\n".join(output)
            
        elif result_type == "article":
            if not content:
                return "No content could be extracted from the article."
            
            # Remove system instructions
            content = re.sub(r"<system>.*?</system>", "", content, flags=re.DOTALL)
            
            # Split into paragraphs and limit length
            paragraphs = [p for p in content.split("\n\n") if p.strip()]
            if not paragraphs:
                return "No readable content found in the article."
                
            summary = "\n\n".join(paragraphs[:3]) + "\n\n[Content truncated...]"
            return f"Article Content:\n\n{summary}"
            
        return "Unexpected result format"

    async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)
            
            # Parse and execute the tool call
            tool_call = json.loads(response)
            tool_result = await self.execute_tool(tool_call)
            
            # Format the result for user
            return self.format_search_result(tool_result)
            
        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
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