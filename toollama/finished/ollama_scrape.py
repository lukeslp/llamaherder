#!/usr/bin/env python3
"""Web scraping tool using Ollama and Jina Reader."""

import json
import asyncio
import requests
from typing import Dict, Any
from tools.llm_tool_webscrape import Tools
import re

class OllamaScrapeUser:
    def __init__(self, model="drummer-scrape", base_url="http://localhost:11434/api/chat"):
        """Initialize the scraping user with model and tools."""
        self.model = model
        self.base_url = base_url
        self.scrape_tool = Tools()
        print("\nInitialized web scraping tool")

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
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        try:
            response = requests.post(self.base_url, json=data)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "").strip()
            print("\nRaw LLM Response:", repr(content))
            
            # First clean the content of any escape characters
            content = content.encode().decode('unicode_escape')
            
            # Extract JSON part
            json_start = content.find("{")
            json_end = content.rfind("}")
            if json_start >= 0 and json_end >= 0:
                content = content[json_start:json_end + 1]
            
            # Basic cleaning first
            content = (content.replace("\n", "")
                            .replace("\t", "")
                            .replace("\r", "")
                            .replace("'", '"'))
            
            # Fix common JSON formatting issues
            content = (content.replace('\\"', '"')  # Fix escaped quotes
                            .replace('""', '"')     # Fix double quotes
                            .strip())
            
            # Remove any spaces between JSON structural elements
            content = re.sub(r'\s*:\s*', ':', content)
            content = re.sub(r'\s*,\s*', ',', content)
            content = re.sub(r'\s*{\s*', '{', content)
            content = re.sub(r'\s*}\s*', '}', content)
            
            print("Cleaned Response:", repr(content))
            
            try:
                parsed = json.loads(content)
                
                # Ensure the response follows the exact format
                clean_response = {
                    "tool": "web_scrape",
                    "parameters": {
                        "url": self.normalize_url(parsed.get("parameters", {}).get("url", ""))
                    }
                }
                
                print("Final Response:", json.dumps(clean_response, indent=2))
                return json.dumps(clean_response)
                
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {str(e)}")
                # Attempt to construct a valid response from the URL
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

    async def execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute the specified tool with given parameters"""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            url = params.get('url', '')
            if not url:
                return "Error: No URL provided"
            
            if tool_name == "web_scrape":
                print(f"\nScraping URL: {url}")
                result = await self.scrape_tool.web_scrape(url)
                if "Error scraping web page" in result:
                    suggestions = [
                        f"- Check if {url} is accessible in your browser",
                        "- Make sure the website exists and is public",
                        "- Try adding or removing 'www.' from the URL",
                        "- Check if the website requires authentication",
                        "- Some websites may block automated access"
                    ]
                    return f"\nError scraping {url}\n\nTroubleshooting:\n" + "\n".join(suggestions)
                return result
            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            print(f"\nScraping error: {str(e)}")
            return f"Error scraping webpage: {str(e)}"

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
    """Main function to run the scraping tool."""
    scraper = OllamaScrapeUser()
    
    print("\nWeb Scraping Tool")
    print("Commands:")
    print("- Just enter a URL: lukesteuber.com")
    print("- Scrape webpage: scrape example.com")
    print("- Read content: read actuallyusefulai.com")
    print("- Get webpage: get arxiv.org/abs/2312.00001")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("\nEnter request: ").strip()
            if user_input.lower() == 'quit':
                break
                
            result = await scraper.run_interaction(user_input)
            print(f"\n{result}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 