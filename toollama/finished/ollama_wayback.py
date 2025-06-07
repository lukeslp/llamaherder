"""
Tool-using setup for Ollama with Wayback Machine integration
"""

import json
import requests
from typing import Dict, Any, List
from tools.llm_tool_wayback import Tools
import re

class OllamaToolUser:
    def __init__(self, model: str = "drummer-wayback"):
        self.model = model
        self.wayback_tool = Tools()
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
    
    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        # Normalize URL if present
        if "url" in params:
            params["url"] = self.normalize_url(params["url"])
        
        if tool_name == "get_archived_snapshot":
            return self.wayback_tool.get_archived_snapshot(**params)
        elif tool_name == "get_capture_history":
            return self.wayback_tool.get_capture_history(**params)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def format_snapshot_result(self, result: Dict[str, Any]) -> str:
        """Format the snapshot result for display"""
        if result.get("status") == "success":
            if "data" in result:
                if isinstance(result["data"], list):
                    captures = result["data"]
                    if not captures:
                        return f"No snapshots found for {result['original_url']}"
                    return f"Found {len(captures)} snapshots of {result['original_url']}\nLatest capture: {captures[-1].get('timestamp', 'unknown date')}"
                else:
                    data = result["data"]
                    return (f"Found snapshot of {result['original_url']}\n"
                           f"Date: {data.get('timestamp', 'unknown')}\n"
                           f"URL: {data.get('url', 'not available')}")
            return "Successfully retrieved archive information."
        else:
            return f"Error: {result.get('message', 'Unknown error occurred')}"

    def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)
            
            # Parse and execute the tool call
            tool_call = json.loads(response)
            tool_result = self.execute_tool(tool_call)
            
            # Format the result for user
            return self.format_snapshot_result(tool_result)
            
        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
            return "An error occurred while processing your request."

def main():
    print("\nWayback Machine Archive Tool")
    print("Commands:")
    print("- Enter a URL directly: example.com")
    print("- Search with date: show me example.com from 2020")
    print("- Get history: history of example.com")
    print("Type 'quit' to exit\n")
    
    agent = OllamaToolUser()
    while True:
        try:
            user_input = input("\nEnter request: ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                break
                
            response = agent.run_interaction(user_input)
            print("\n" + response)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 