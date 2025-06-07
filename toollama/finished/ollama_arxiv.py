"""
Tool-using setup for Ollama with arXiv integration
"""

import json
import requests
from typing import Dict, Any, List
from tools.llm_tool_arxiv import Tools
import re
import asyncio

class OllamaArxivUser:
    def __init__(self, model: str = "drummer-arxiv"):
        self.model = model
        self.arxiv_tool = Tools()
        self.base_url = "http://localhost:11434/api/chat"
        print("\nInitialized arXiv search tool")
        
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
            print("\nRaw LLM Response:", repr(content))
            
            # Extract just the JSON part if there's extra text
            json_start = content.find("{")
            json_end = content.rfind("}")
            if json_start >= 0 and json_end >= 0:
                content = content[json_start:json_end + 1]
            
            # Clean up any potential JSON formatting issues
            if content.count("}") > 2:  # More than 2 closing braces is wrong
                content = content.replace("}}", "}")
            if content.endswith('"}}}'):
                content = content[:-1]
            if not content.endswith('}}'):
                content = content + '}'
                
            print("Cleaned Response:", repr(content))
            
            # Validate JSON structure
            try:
                parsed = json.loads(content)
                if "tool" not in parsed or "parameters" not in parsed:
                    raise ValueError("Missing required fields")
                if parsed["tool"] != "search_papers":
                    raise ValueError("Invalid tool name")
                if "topic" not in parsed["parameters"]:
                    raise ValueError("Missing topic parameter")
                
                # Clean up the topic - remove extra spaces and normalize case
                parsed["parameters"]["topic"] = parsed["parameters"]["topic"].strip()
                content = json.dumps(parsed)
                
                print("Parsed JSON:", json.dumps(parsed, indent=2))
                return content
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON Error: {str(e)}")
                raise
            
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            raise
        except Exception as e:
            print(f"Error parsing response: {e}")
            raise
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            search_topic = params.get('topic', 'unknown topic')
            print(f"\nSearching arXiv for: {search_topic}")
            
            if tool_name == "search_papers":
                result = await self.arxiv_tool.search_papers(**params)
                if "No papers found" in result:
                    suggestions = [
                        f"- Try searching for '{search_topic}' with different terms",
                        "- Add a field like 'computer science', 'physics', etc.",
                        "- Check for typos in names or technical terms",
                        "- Use broader terms if the search is too specific",
                        "- Try searching for related topics or authors"
                    ]
                    return "\nNo papers found on arXiv matching your search.\n\nSuggestions:\n" + "\n".join(suggestions)
                return result
            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            print(f"\nSearch error: {str(e)}")
            return f"Error searching arXiv: {str(e)}"

    async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with tool use"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)
            
            # Parse and execute the tool call
            tool_call = json.loads(response)
            result = await self.execute_tool(tool_call)
            
            # Result is already formatted by the arXiv tool
            return result
            
        except json.JSONDecodeError:
            return "Invalid response format. Please try a more specific request."
        except Exception as e:
            print(f"Error details: {str(e)}")
            return "An error occurred while processing your request."

async def main():
    print("\narXiv Paper Search Tool")
    print("Commands:")
    print("- Search papers: find papers about quantum computing")
    print("- Latest research: latest papers on transformers")
    print("- Specific topic: search papers on speech recognition")
    print("Type 'quit' to exit\n")
    
    agent = OllamaArxivUser()
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