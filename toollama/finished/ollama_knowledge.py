"""
Tool-using setup for Ollama with Knowledge Base integration
Enhanced with accessibility features and improved formatting
"""

import json
import requests
from typing import Dict, Any, Optional
from tools.llm_tool_knowledge import Tools
import asyncio
import sys
from pathlib import Path
import os
import re

class OllamaKnowledgeUser:
    """Routes knowledge base requests to appropriate handlers with enhanced accessibility"""
    
    def __init__(self, model: str = "drummer-knowledge"):
        """Initialize the knowledge base router"""
        self.model = model
        self.base_url = "http://localhost:11434/api/chat"
        self.knowledge_tool = Tools()
        
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
        """Format knowledge base results with enhanced accessibility"""
        if result.get("status") == "success":
            data = result.get("data", {})
            
            if "results" in data and "format" in data:  # Wikidata results
                output = [
                    "Wikidata Query Results:",
                    f"Format: {data.get('format')}",
                    f"Results Found: {data.get('count', 0)}"
                ]
                
                if data.get('format') == "raw":
                    output.extend([
                        "\nRaw Results:",
                        "```json",
                        json.dumps(data.get('results'), indent=2),
                        "```"
                    ])
                else:
                    output.append("\nResults:")
                    for i, res in enumerate(data.get('results', []), 1):
                        if isinstance(res, dict):
                            output.append(f"\n{i}. " + " | ".join(f"{k}: {v}" for k, v in res.items()))
                        else:
                            output.append(f"\n{i}. {res}")
                            
                return "\n".join(output)
                
            elif "result" in data and "format" in data:  # Wolfram Alpha results
                output = [
                    "Wolfram Alpha Results:",
                    f"Format: {data.get('format')}",
                    f"Query: {data.get('query')}"
                ]
                
                result = data.get('result', {})
                if data.get('format') == "math":
                    if result.get('input'):
                        output.append(f"\nInput: {result['input']}")
                    if result.get('steps'):
                        output.append("\nSteps:")
                        for i, step in enumerate(result['steps'], 1):
                            output.append(f"{i}. {step}")
                    if result.get('solution'):
                        output.append(f"\nSolution: {result['solution']}")
                elif data.get('format') == "image":
                    output.append("\nImage Results:")
                    for img in result.get('images', []):
                        output.append(f"- {img['title']}: {img['url']}")
                else:  # plain
                    output.append("\nResults:")
                    for pod in result.get('pods', []):
                        output.append(f"\n{pod['title']}:")
                        output.append(pod['text'])
                        
                return "\n".join(output)
                
            elif "results" in data and "mode" in data:  # Perplexity results
                output = [
                    "Perplexity Search Results:",
                    f"Mode: {data.get('mode')}",
                    f"Results Found: {data.get('count', 0)}"
                ]
                
                if data.get('focus'):
                    output.append(f"Focus: {data.get('focus')}")
                    
                output.append("\nResults:")
                for i, res in enumerate(data.get('results', []), 1):
                    output.extend([
                        f"\n{i}. {res.get('title')}",
                        f"   URL: {res.get('url')}",
                        f"   {res.get('snippet')}"
                    ])
                    if "citations" in res:
                        output.append("   Citations:")
                        for cite in res['citations']:
                            output.append(f"   - {cite}")
                            
                return "\n".join(output)
                
            elif "transcript" in data:  # YouTube transcript
                output = [
                    "YouTube Transcript Results:",
                    f"URL: {data.get('url')}"
                ]
                
                if "metadata" in data:
                    meta = data["metadata"]
                    output.extend([
                        f"Title: {meta.get('title')}",
                        f"Author: {meta.get('author')}",
                        f"Views: {meta.get('view_count')}",
                        f"Published: {meta.get('publish_date')}"
                    ])
                    if meta.get('description'):
                        output.extend([
                            "\nDescription:",
                            meta['description']
                        ])
                        
                output.extend([
                    "\nTranscript:",
                    "```",
                    data.get('transcript'),
                    "```"
                ])
                
                return "\n".join(output)
                
            return "Successfully processed request."
        else:
            return f"Error: {result.get('message', 'Unknown error occurred')}"
    
    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified knowledge base tool with enhanced error handling"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "query_wikidata":
                result = self.knowledge_tool.query_wikidata(**params)
            elif tool_name == "query_wolfram":
                result = self.knowledge_tool.query_wolfram(**params)
            elif tool_name == "search_perplexity":
                result = self.knowledge_tool.search_perplexity(**params)
            elif tool_name == "get_youtube_transcript":
                result = await self.knowledge_tool.get_youtube_transcript(**params)
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
    """Main function to run the knowledge base tool with enhanced help"""
    processor = OllamaKnowledgeUser()
    
    print("\nKnowledge Base Tool")
    print("\nAvailable Commands:")
    print("Wikidata Queries:")
    print("- 'find ENTITY'")
    print("- 'search for TOPIC'")
    print("- Formats: simple, detailed, raw")
    
    print("\nWolfram Alpha:")
    print("- 'calculate EXPRESSION'")
    print("- 'solve PROBLEM'")
    print("- Formats: plain, math, image")
    print("- Options: steps, units")
    
    print("\nPerplexity Search:")
    print("- 'search for TOPIC'")
    print("- 'research TOPIC'")
    print("- Modes: search, academic, writing, analysis")
    print("- Options: citations, recent only")
    
    print("\nYouTube Transcripts:")
    print("- 'get transcript from URL'")
    print("- 'transcribe video URL'")
    print("- Options: language, metadata")
    
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