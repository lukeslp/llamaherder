"""
Tool-using setup for Ollama with Web Search integration
"""

import json
import requests
from typing import Dict, Any, List
from rejects.dev_llm_tool_websearch import Tools
import re
import asyncio

class OllamaSearchUser:
    def __init__(self, model: str = "drummer-search:3b"):
        self.model = model
        self.search_tool = Tools()
        # Configure search engine URL - replace with your SearXNG instance
        self.search_tool.valves.SEARXNG_ENGINE_API_BASE_URL = "https://searx.be/search"
        self.search_tool.valves.RETURNED_SCRAPPED_PAGES_NO = 5
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
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        if tool_name == "search_web":
            result = await self.search_tool.search_web(**params)
            return json.loads(result)
        elif tool_name == "get_website":
            if "url" in params:
                params["url"] = self.normalize_url(params["url"])
            result = await self.search_tool.get_website(**params)
            return json.loads(result)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def format_search_result(self, results: List[Dict[str, Any]]) -> str:
        """Format the search results for display"""
        if not results:
            return "No results found."
            
        output = []
        for idx, result in enumerate(results, 1):
            if isinstance(result, dict):
                title = result.get("title", "Untitled")
                url = result.get("url", "No URL")
                excerpt = result.get("excerpt", result.get("snippet", ""))[:200] + "..."
                
                output.append(f"\n{idx}. {title}")
                output.append(f"   URL: {url}")
                if excerpt:
                    output.append(f"   Summary: {excerpt}")
                output.append("")
                
        return "\n".join(output)

    async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)
            
            # Parse and execute the tool call
            tool_call = json.loads(response)
            tool_result = await self.execute_tool(tool_call)
            
            # Format the result for user
            if isinstance(tool_result, list):
                return self.format_search_result(tool_result)
            elif isinstance(tool_result, dict):
                if "error" in tool_result:
                    return f"Error: {tool_result['error']}"
                return self.format_search_result([tool_result])
            else:
                return "Unexpected response format"
            
        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
            return "An error occurred while processing your request."

async def main():
    print("\nWeb Search Tool")
    print("Commands:")
    print("- Search query: what's new with AI?")
    print("- Check website: check example.com")
    print("- Research topic: tell me about quantum computing")
    print("Type 'quit' to exit\n")
    
    agent = OllamaSearchUser()
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