"""
Tool-using setup for Ollama with Document Management integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
from typing import Dict, Any, Optional
from tools.llm_tool_document import Tools
import asyncio
import sys
from pathlib import Path
import os
import re
from collections import defaultdict

class OllamaDocumentUser:
    """Routes document management requests to appropriate handlers with enhanced accessibility"""
    
    def __init__(self, model: str = "drummer-document"):
        """Initialize the document management router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.document_tool = Tools()
        
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
        """Format document management results with enhanced accessibility"""
        if result.get("status") == "success":
            data = result.get("data", {})
            
            if "result" in data and "format" in data:  # OCR results
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
                
            elif "documents" in data:  # Paperless results
                output = [
                    "Paperless Document Search Results:",
                    f"Found {data.get('count', 0)} documents"
                ]
                
                if data.get('query'):
                    query = data['query']
                    filters = []
                    if query.get('type'):
                        filters.append(f"Type: {query['type']}")
                    if query.get('tag'):
                        filters.append(f"Tag: {query['tag']}")
                    if query.get('correspondent'):
                        filters.append(f"Correspondent: {query['correspondent']}")
                    if query.get('year'):
                        filters.append(f"Year: {query['year']}")
                    if query.get('month'):
                        filters.append(f"Month: {query['month']}")
                        
                    if filters:
                        output.append("Filters: " + ", ".join(filters))
                        
                output.append("\nDocuments:")
                for doc in data.get('documents', []):
                    output.extend([
                        f"\n{doc.get('title')}",
                        f"ID: {doc.get('id')}",
                        f"Type: {doc.get('document_type')}",
                        f"Created: {doc.get('created_date')}",
                        f"Correspondent: {doc.get('correspondent')}",
                        "Tags: " + ", ".join(doc.get('tags', [])),
                        "---"
                    ])
                    
                return "\n".join(output)
                
            elif "organized" in data:  # File organization results
                output = [
                    "File Organization Results:",
                    f"Total Organized: {data.get('total_organized', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
                
                if data.get('organized'):
                    output.append("\nOrganized Files:")
                    for file_type, files in data['organized'].items():
                        output.append(f"\n{file_type.title()}:")
                        for file in files:
                            output.append(f"- {file}")
                            
                if data.get('skipped'):
                    output.append("\nSkipped Files:")
                    for skip in data['skipped']:
                        output.append(f"- {skip['file']}: {skip['error']}")
                        
                return "\n".join(output)
                
            elif "transferred" in data:  # File transfer results
                output = [
                    f"File {data.get('operation', 'transfer').title()} Results:",
                    f"Total Transferred: {data.get('total_transferred', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
                
                if data.get('transferred'):
                    output.append("\nTransferred Files:")
                    for file in data['transferred']:
                        output.append(f"- {file}")
                        
                if data.get('skipped'):
                    output.append("\nSkipped Files:")
                    for skip in data['skipped']:
                        output.append(f"- {skip['file']}: {skip['error']}")
                        
                return "\n".join(output)
                
            elif "archived" in data:  # Archive results
                output = [
                    "Archive Creation Results:",
                    f"Archive: {data.get('archive')}",
                    f"Total Archived: {data.get('total_archived', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
                
                if data.get('archived'):
                    output.append("\nArchived Files:")
                    for file in data['archived']:
                        output.append(f"- {file}")
                        
                if data.get('skipped'):
                    output.append("\nSkipped Files:")
                    for skip in data['skipped']:
                        output.append(f"- {skip['file']}: {skip['error']}")
                        
                return "\n".join(output)
                
            elif "deleted" in data:  # Deletion results
                output = [
                    "File Deletion Results:",
                    f"Total Deleted: {data.get('total_deleted', 0)}",
                    f"Total Skipped: {data.get('total_skipped', 0)}"
                ]
                
                if data.get('deleted'):
                    output.append("\nDeleted Files:")
                    for file in data['deleted']:
                        output.append(f"- {file}")
                        
                if data.get('skipped'):
                    output.append("\nSkipped Files:")
                    for skip in data['skipped']:
                        output.append(f"- {skip['file']}: {skip['error']}")
                        
                return "\n".join(output)
                
            return "Successfully processed request."
        else:
            return f"Error: {result.get('message', 'Unknown error occurred')}"
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified document management tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "process_ocr":
                result = await self.document_tool.process_ocr(**params)
            elif tool_name == "get_paperless_documents":
                result = await self.document_tool.get_paperless_documents(**params)
            elif tool_name == "manage_files":
                result = await self.document_tool.manage_files(**params)
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
    """Main function to run the document management tool with enhanced help"""
    processor = OllamaDocumentUser()
    
    print("\nDocument Management Tool")
    print("\nAvailable Commands:")
    print("OCR Processing:")
    print("- 'extract text from FILE'")
    print("- 'process FILE in LANGUAGE'")
    print("- Formats: text, json, markdown")
    print("- Options: language, metadata")
    
    print("\nPaperless Integration:")
    print("- 'find documents TYPE'")
    print("- 'search TAG in YEAR'")
    print("- 'get documents from CORRESPONDENT'")
    print("- Filters: type, tag, correspondent, year, month")
    
    print("\nFile Management:")
    print("- 'organize DIRECTORY'")
    print("- 'move/copy FILES to DESTINATION'")
    print("- 'archive FILES as ARCHIVE'")
    print("- 'delete FILES'")
    print("- Options: recursive, pattern, create_dirs")
    
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