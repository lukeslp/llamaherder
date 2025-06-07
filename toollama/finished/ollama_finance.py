"""
Tool-using setup for Ollama with Finance integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
import asyncio
from typing import Dict, Any
from tools.llm_tool_finance import Tools

class OllamaFinanceUser:
    """Routes finance requests to appropriate handlers with enhanced accessibility"""
    
    def __init__(self, model: str = "drummer-finance"):
        """Initialize the finance router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.finance_tool = Tools()
        
    def generate(self, prompt: str) -> str:
        """Generate a response from Ollama with enhanced error handling"""
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        try:
            response = requests.post(self.base_url, json=data, timeout=30)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            
            # Ensure we have a complete JSON object
            if not content.startswith("{"):
                content = "{"
            if not content.endswith("}"):
                content += "}"
                
            # Validate JSON structure
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError:
                print("\nWarning: Invalid JSON response from model. Attempting to fix...")
                # Attempt to fix common JSON issues
                content = content.replace("'", '"')
                content = content.replace("None", "null")
                json.loads(content)  # Validate again
                return content
                
        except requests.exceptions.RequestException as e:
            print(f"\nNetwork error: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"\nInvalid JSON: {content}")
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            raise
    
    def format_output(self, result: str) -> str:
        """Format finance results with enhanced accessibility"""
        return result
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified finance tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "analyze_asset":
                result = await self.finance_tool.analyze_asset(**params)
            else:
                return f"Error: Unknown tool {tool_name}"
                
            return self.format_output(result)
                
        except Exception as e:
            print(f"\nTool execution error: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"
    
    async def run_interaction(self, user_input: str) -> str:
        """Run a complete interaction with enhanced error handling"""
        try:
            # Get tool selection from LLM
            response = self.generate(user_input)
            
            # Parse and execute the tool call
            try:
                tool_call = json.loads(response)
                return await self.execute_tool(tool_call)
            except json.JSONDecodeError:
                print(f"\nInvalid JSON response: {response}")
                return "Invalid response format. Please try a more specific request."
            except Exception as e:
                print(f"\nError executing tool: {str(e)}")
                return "An error occurred while processing your request."
                
        except Exception as e:
            print(f"\nError details: {str(e)}")
            return "An error occurred while processing your request."

async def main():
    """Main function to run the finance tool with enhanced help"""
    processor = OllamaFinanceUser()
    
    print("\nFinance Analysis Tool")
    print("\nAvailable Commands:")
    print("Stock Analysis:")
    print("- 'analyze TICKER'")
    print("- 'analyze stock TICKER'")
    print("- Example: analyze AAPL")
    
    print("\nCrypto Analysis:")
    print("- 'analyze crypto SYMBOL'")
    print("- Example: analyze BTC-USD")
    
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            request = input("\nEnter request: ").strip()
            if request.lower() == 'quit':
                print("Exiting...")
                break
                
            result = await processor.run_interaction(request)
            print("\n" + result)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred while processing your request.")
            print(f"Error details: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 