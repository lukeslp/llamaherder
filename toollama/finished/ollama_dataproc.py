"""
Tool-using setup for Ollama with Data Processing integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
from typing import Dict, Any, Optional
from tools.llm_tool_dataproc import Tools
import asyncio
import sys
from pathlib import Path
import os

class OllamaDataProcUser:
    """Routes data processing requests to appropriate handlers with enhanced accessibility"""
    
    def __init__(self, model: str = "drummer-dataproc"):
        """Initialize the data processing router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.dataproc_tool = Tools()
        
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
                print("\nWarning: Invalid JSON response from model. Attempting to fix...", file=sys.stderr)
                # Attempt to fix common JSON issues
                content = content.replace("'", '"')
                content = re.sub(r'(\w+):', r'"\1":', content)
                json.loads(content)  # Validate again
                return content
                
        except requests.exceptions.RequestException as e:
            print(f"\nNetwork error: {e}", file=sys.stderr)
            raise
        except json.JSONDecodeError as e:
            print(f"\nInvalid JSON: {content}", file=sys.stderr)
            raise
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            raise
    
    def format_output(self, result: Dict[str, Any]) -> str:
        """Format data processing results with enhanced accessibility"""
        if result.get("status") == "success":
            data = result.get("data", {})
            
            if "converted" in data:  # JSON conversion
                output = [
                    "Format Conversion Results:",
                    f"Target Format: {data.get('format')}",
                    f"Style: {data.get('style', 'default')}",
                    "\nConverted Data:",
                    f"```{data.get('format')}\n{data.get('converted')}\n```"
                ]
                return "\n".join(output)
                
            elif "result" in data and "format" in data:  # OCR processing
                output = [
                    "OCR Processing Results:",
                    f"Language: {data.get('language', 'Unknown')}",
                    f"Format: {data.get('format')}",
                    f"Pages Processed: {data.get('pages', 1)}"
                ]
                
                if data.get('format') == "markdown":
                    output.extend([
                        "\nExtracted Text:",
                        data.get('result')
                    ])
                elif data.get('format') == "json":
                    output.extend([
                        "\nExtracted Text (JSON):",
                        f"```json\n{json.dumps(data.get('result'), indent=2)}\n```"
                    ])
                else:  # text
                    output.extend([
                        "\nExtracted Text:",
                        "```",
                        data.get('result'),
                        "```"
                    ])
                    
                return "\n".join(output)
                
            elif "result" in data and "model" in data:  # Audio transcription
                output = [
                    "Audio Transcription Results:",
                    f"Model: {data.get('model')}",
                    f"Format: {data.get('format')}"
                ]
                
                if data.get('options'):
                    opts = data.get('options')
                    if opts.get('language'):
                        output.append(f"Language: {opts.get('language')}")
                    if opts.get('temperature') is not None:
                        output.append(f"Temperature: {opts.get('temperature')}")
                        
                output.extend([
                    "\nTranscription:",
                    "```",
                    data.get('result') if isinstance(data.get('result'), str) 
                    else json.dumps(data.get('result'), indent=2),
                    "```"
                ])
                
                return "\n".join(output)
                
            return "Successfully processed request."
        else:
            return f"Error: {result.get('message', 'Unknown error occurred')}"
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified data processing tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "convert_json":
                result = self.dataproc_tool.convert_json(**params)
            elif tool_name == "process_ocr":
                result = self.dataproc_tool.process_ocr(**params)
            elif tool_name == "transcribe_audio":
                result = self.dataproc_tool.transcribe_audio(**params)
            else:
                return f"Error: Unknown tool {tool_name}"
                
            return self.format_output(result)
                
        except Exception as e:
            print(f"\nTool execution error: {str(e)}", file=sys.stderr)
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
                print(f"\nInvalid JSON response: {response}", file=sys.stderr)
                return "Invalid response format. Please try a more specific request."
            except Exception as e:
                print(f"\nError executing tool: {str(e)}", file=sys.stderr)
                return "An error occurred while processing your request."
                
        except Exception as e:
            print(f"\nError details: {str(e)}", file=sys.stderr)
            return "An error occurred while processing your request."

async def main():
    """Main function to run the data processing tool with enhanced help"""
    processor = OllamaDataProcUser()
    
    print("\nData Processing Tool")
    print("\nAvailable Commands:")
    print("Format Conversion:")
    print("- 'convert DATA to FORMAT'")
    print("- 'convert @file.json to yaml'")
    print("- Formats: json, yaml, xml, csv, toml")
    print("- Styles: pretty, compact, single_line")
    
    print("\nOCR Processing:")
    print("- 'extract text from FILE'")
    print("- 'process FILE in LANGUAGE'")
    print("- Supports images and PDFs")
    print("- Output: text, json, markdown")
    
    print("\nAudio Transcription:")
    print("- 'transcribe FILE'")
    print("- 'transcribe FILE in LANGUAGE'")
    print("- Formats: json, text, srt, vtt")
    print("- Options: language, temperature")
    
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