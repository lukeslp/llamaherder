"""
Tool-using setup for Ollama with Time & Calculation integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
import asyncio
from typing import Dict, Any
from tools.llm_tool_timecalc import Tools

class OllamaTimeCalcUser:
    """Routes time and calculation requests to appropriate handlers with enhanced accessibility"""
    
    def __init__(self, model: str = "drummer-timecalc"):
        """Initialize the time and calculation router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.timecalc_tool = Tools()
        
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
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format time and calculation results with enhanced accessibility"""
        if result.get("status") == "success":
            data = result.get("data", {})
            
            if "original" in data:  # Time conversion
                output = [
                    "Time Conversion Results:",
                    f"Original: {data.get('original')} ({data.get('source_timezone')})",
                    f"Converted: {data.get('converted')} ({data.get('target_timezone')})"
                ]
                return "\n".join(output)
                
            elif "difference" in data:  # Time difference
                output = [
                    "Time Difference Results:",
                    f"Time 1: {data.get('time1')}",
                    f"Time 2: {data.get('time2')}",
                    f"Difference: {data.get('difference')} {data.get('unit')}"
                ]
                return "\n".join(output)
                
            elif "expression" in data:  # Math evaluation
                output = [
                    "Math Evaluation Results:",
                    f"Expression: {data.get('expression')}"
                ]
                if data.get("variables"):
                    output.append("Variables:")
                    for var, value in data.get("variables", {}).items():
                        output.append(f"  {var} = {value}")
                output.append(f"Result: {data.get('result')}")
                return "\n".join(output)
                
            elif "current_time" in data:  # Current time
                return f"Current Time: {data.get('current_time')} ({data.get('timezone')})"
                
            elif "timezones" in data:  # Timezone list
                zones = data.get("timezones", [])
                if len(zones) > 20:
                    zones = zones[:20]
                    return f"Available Timezones (showing first 20 of {len(data.get('timezones', []))}):\n" + "\n".join(zones)
                return "Available Timezones:\n" + "\n".join(zones)
                
            return "Successfully processed request."
        else:
            return f"Error: {result.get('message', 'Unknown error occurred')}"
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified time or calculation tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "convert_time":
                result = self.timecalc_tool.convert_time(**params)
            elif tool_name == "calculate_time_difference":
                result = self.timecalc_tool.calculate_time_difference(**params)
            elif tool_name == "evaluate_math":
                result = self.timecalc_tool.evaluate_math(**params)
            elif tool_name == "get_current_time":
                result = self.timecalc_tool.get_current_time(**params)
            elif tool_name == "list_timezones":
                result = self.timecalc_tool.list_timezones(**params)
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
    """Main function to run the time and calculation tool with enhanced help"""
    processor = OllamaTimeCalcUser()
    
    print("\nTime & Calculation Tool")
    print("\nAvailable Commands:")
    print("Time Operations:")
    print("- 'convert TIME to TIMEZONE'")
    print("- 'time difference between TIME1 and TIME2'")
    print("- 'current time in TIMEZONE'")
    print("- 'list timezones [FILTER]'")
    
    print("\nMath Operations:")
    print("- 'calculate EXPRESSION'")
    print("- 'evaluate EXPRESSION with VAR1=VALUE1, VAR2=VALUE2'")
    print("- Supports: +, -, *, /, ^, sin, cos, tan, log, sqrt, pi, e")
    
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