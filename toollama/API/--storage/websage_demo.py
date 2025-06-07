#!/usr/bin/env python3
"""
WebSage Demo - Demonstrating the WebSage Ollama model with web search capabilities

This script shows how to use the WebSage model (based on mistral-small) with
the infinite_search.py tool to perform web searches and summarize content.

Requirements:
- Ollama installed with the WebSage model created
- requests library
- The infinite_search.py tool (adapted from the original)
"""

import json
import requests
import asyncio
import sys
from typing import List, Dict, Any, Optional

# Import the Tools class from the infinite_search module
# Adjust the import path as needed for your setup
sys.path.append('./api-tools/tools/tools/tools2')
try:
    from infinite_search import Tools
except ImportError:
    print("Error: Could not import Tools from infinite_search.")
    print("Please ensure the infinite_search.py file is in the correct location.")
    print("Expected path: ./api-tools/tools/tools/tools2/infinite_search.py")
    sys.exit(1)

# Ollama API settings
OLLAMA_API_URL = "http://localhost:11434/api"
MODEL_NAME = "websage"  # The name you used when creating the model

class WebSageDemo:
    def __init__(self):
        self.tools = Tools()
        self.conversation_history = []
        
    async def search_and_read(self, query: str, search_engine: str = "google") -> str:
        """
        Perform a web search and read content from the top results.
        
        Args:
            query: The search query
            search_engine: The search engine to use (google, bing, or baidu)
            
        Returns:
            A string containing the search results and content
        """
        # Select the appropriate search method based on the engine
        if search_engine == "google":
            search_results = await self.tools.google_search(query)
        elif search_engine == "bing":
            search_results = await self.tools.bing_search(query)
        elif search_engine == "baidu":
            search_results = await self.tools.baidu_search(query)
        else:
            return f"Error: Unsupported search engine '{search_engine}'"
        
        # Extract URLs from search results (simplified for demo)
        # In a real implementation, you would parse the search results properly
        urls = self._extract_urls_from_search_results(search_results)
        
        # Read content from the top URLs (limit to 2 for demo purposes)
        content = ""
        for url in urls[:2]:
            try:
                url_content = await self.tools.read_url(url)
                content += f"\n\n--- Content from {url} ---\n{url_content}\n"
            except Exception as e:
                content += f"\n\nError reading {url}: {str(e)}\n"
        
        return f"Search results for '{query}' using {search_engine}:\n{search_results}\n\nExtracted content:{content}"
    
    def _extract_urls_from_search_results(self, search_results: str) -> List[str]:
        """
        Extract URLs from search results (simplified implementation).
        In a real application, you would parse the HTML properly.
        
        Args:
            search_results: The search results HTML
            
        Returns:
            A list of URLs extracted from the search results
        """
        # This is a very simplified extraction - would need proper HTML parsing in production
        urls = []
        lines = search_results.split('\n')
        for line in lines:
            if 'http' in line and 'href=' in line:
                # Very basic extraction - not reliable for production
                start = line.find('href="') + 6
                end = line.find('"', start)
                if start > 6 and end > start:
                    url = line[start:end]
                    if url.startswith('http') and url not in urls:
                        urls.append(url)
        
        return urls
    
    async def chat_with_websage(self, user_message: str) -> str:
        """
        Send a message to the WebSage model and get a response.
        
        Args:
            user_message: The user's message
            
        Returns:
            The model's response
        """
        # Add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare the request to the Ollama API
        url = f"{OLLAMA_API_URL}/chat"
        payload = {
            "model": MODEL_NAME,
            "messages": self.conversation_history,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # Extract the assistant's message
            assistant_message = result.get("message", {}).get("content", "No response")
            
            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama API: {str(e)}"
    
    async def run_demo(self):
        """Run an interactive demo of the WebSage model with web search capabilities."""
        print("\n" + "="*80)
        print("WebSage Demo - Web Search & Summary Expert".center(80))
        print("="*80)
        print("\nThis demo shows how to use the WebSage model with web search capabilities.")
        print("Type 'exit' or 'quit' to end the demo.\n")
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check if the user wants to exit
            if user_input.lower() in ['exit', 'quit']:
                print("\nThank you for using WebSage Demo. Goodbye!")
                break
            
            # Check if this is a search request
            if user_input.lower().startswith(('search ', 'find ', 'look up ')):
                print("\nPerforming web search...")
                
                # Extract the search query
                query = user_input.split(' ', 1)[1]
                
                # Perform the search (default to Google)
                search_results = await self.search_and_read(query)
                
                # Send the search results to WebSage for processing
                print("\nProcessing search results with WebSage...")
                websage_prompt = f"I performed a web search for '{query}' and got these results. Please analyze and summarize the key information:\n\n{search_results}"
                
                # Get WebSage's response
                websage_response = await self.chat_with_websage(websage_prompt)
                
                # Display the response
                print(f"\nWebSage: {websage_response}")
            else:
                # Regular chat with WebSage
                print("\nSending to WebSage...")
                response = await self.chat_with_websage(user_input)
                print(f"\nWebSage: {response}")

if __name__ == "__main__":
    # Check if Ollama is running
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        if response.status_code != 200:
            print("Error: Could not connect to Ollama API.")
            print("Please ensure Ollama is running on http://localhost:11434")
            sys.exit(1)
            
        # Check if the WebSage model exists
        models = response.json().get("models", [])
        model_exists = any(model.get("name") == MODEL_NAME for model in models)
        
        if not model_exists:
            print(f"Error: The '{MODEL_NAME}' model does not exist in Ollama.")
            print("Please create it first using:")
            print(f"  ollama create {MODEL_NAME} -f ./Modelfile")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("Error: Could not connect to Ollama API.")
        print("Please ensure Ollama is running on http://localhost:11434")
        sys.exit(1)
    
    # Run the demo
    demo = WebSageDemo()
    asyncio.run(demo.run_demo()) 