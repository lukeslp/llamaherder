#!/usr/bin/env python3
"""
Herd AI - Code Executor Module
-------------------------------------------------------------------------------
Secure, interactive CLI and API for running Python code and Bash commands in a
restricted environment. Designed for use as a tool by agents, orchestrators, or
as a standalone CLI for debugging and output retrieval.

Features:
- Conversational AI assistant with code execution capabilities
- Secure Python and Bash execution (tempfile, restricted env)
- CLI with accessible, colorized output
- Tool schema for LLM/agent integration
- XAI API key support for tool calls

Usage:
  python -m herd_ai.code_executor           # Launch interactive CLI
  herd --exec                               # Launch from herd.py CLI
  (import and use Tools class programmatically)
"""

import os
import sys
import json
import asyncio
import tempfile
import requests
from typing import Dict, Any, Optional

try:
    from rich.prompt import Prompt
    from rich.console import Console
    console = Console()
except ImportError:
    # Simple fallback if rich is not available
    class Prompt:
        @staticmethod
        def ask(prompt, choices=None, default=None):
            prompt_str = f"{prompt} "
            if choices:
                prompt_str += f"[{'/'.join(choices)}] "
            if default:
                prompt_str += f"(default: {default}) "
            response = input(prompt_str)
            return response or default
    console = None

try:
    from dotenv import load_dotenv
except ImportError:
    # Define a simple load_dotenv function if the package is not available
    def load_dotenv(dotenv_path=None):
        """Simple fallback if python-dotenv is not installed"""
        pass

# CLIStyle for accessible output
class CLIStyle:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

def load_env():
    """Load environment variables from .env file and strip quotes"""
    try:
        # Try multiple possible .env file locations
        possible_env_paths = [
            # Current directory
            os.path.join(os.getcwd(), '.env'),
            # Directory of the script
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),
            # Project root (assuming typical structure)
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env'),
            # Home directory
            os.path.join(os.path.expanduser('~'), '.env')
        ]
        
        env_loaded = False
        for env_path in possible_env_paths:
            if os.path.exists(env_path):
                print(f"{CLIStyle.CYAN}Loading environment from: {env_path}{CLIStyle.RESET}")
                load_dotenv(dotenv_path=env_path)
                env_loaded = True
                break
        
        if not env_loaded:
            print(f"{CLIStyle.YELLOW}Warning: No .env file found in any of the expected locations{CLIStyle.RESET}")
            
        # Check for environment variables directly
        env_vars = ["XAI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GROQ_API_KEY"]
        for var in env_vars:
            if os.environ.get(var):
                print(f"{CLIStyle.GREEN}Found {var} in environment{CLIStyle.RESET}")
                
        # Strip quotes from environment variables
        for key, value in os.environ.items():
            if isinstance(value, str) and len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    os.environ[key] = value[1:-1]
                    print(f"{CLIStyle.CYAN}Stripped quotes from {key}{CLIStyle.RESET}")
    except Exception as e:
        print(f"{CLIStyle.RED}Error loading environment: {str(e)}{CLIStyle.RESET}")

def load_swarm_logo() -> str:
    """Load Swarm logo from .swarm file if available"""
    swarm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.swarm')
    if os.path.exists(swarm_path):
        try:
            with open(swarm_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith("SWARM_LOGO"):
                        return line.split("=", 1)[-1].strip().strip('"').strip("'")
        except Exception:
            pass
    return ""

XAI_API_ENDPOINT = "https://api.x.ai/v1/chat/completions"

class Tools:
    def __init__(self):
        self.python_path = sys.executable
        self.temp_dir = tempfile.gettempdir()

    async def run_python_code(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            process = await asyncio.create_subprocess_exec(
                self.python_path,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env={
                    'PATH': os.environ.get('PATH', ''),
                    'PYTHONPATH': '',
                    'PYTHONHOME': '',
                }
            )
            stdout, stderr = await process.communicate()
            os.unlink(temp_path)
            output = stdout.decode() if stdout else ''
            error = stderr.decode() if stderr else ''
            if error:
                return f"Error:\n{error}"
            return output if output else "No output"
        except Exception as e:
            return f"Error running Python code: {str(e)}"

    async def run_bash_command(self, command: str) -> str:
        try:
            if any(unsafe in command.lower() for unsafe in ['sudo', 'rm -rf', '>', '>>', '|', '&', ';']):
                return "Error: Command contains unsafe operations"
            process = await asyncio.create_subprocess_exec(
                'sh',
                '-c',
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir,
                env={
                    'PATH': '/usr/bin:/bin',
                    'HOME': self.temp_dir,
                }
            )
            stdout, stderr = await process.communicate()
            output = stdout.decode() if stdout else ''
            error = stderr.decode() if stderr else ''
            if error:
                return f"Error:\n{error}"
            return output if output else "No output"
        except Exception as e:
            return f"Error running bash command: {str(e)}"

def get_tool_schema() -> dict:
    return [
        {
            "type": "function",
            "function": {
                "name": "run_python_code",
                "description": "Execute Python code in a restricted environment and return the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute."
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run_bash_command",
                "description": "Execute a safe Bash command in a restricted environment and return the output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Bash command to execute."
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    ]

# Define TOOL_SCHEMAS for discovery by external systems
TOOL_SCHEMAS = get_tool_schema()

# Registration function for registry integration
def register_with_registry(registry):
    """Register tools with the provided registry."""
    tools_schema = get_tool_schema()
    
    # Register each tool
    for tool in tools_schema:
        tool_name = tool["function"]["name"]
        tool_description = tool["function"]["description"]
        category = "Execute"
        
        # Register the tool with the registry
        registry.register_tool(
            name=tool_name,
            description=tool_description,
            category=category,
            schema=tool["function"]
        )
    
    return f"Successfully registered executor tools with registry"

def setup_client(api_key: Optional[str] = None) -> Dict[str, str]:
    """Set up API client headers based on available API keys
    
    Supports multiple API providers with the following priority:
    1. XAI_API_KEY
    2. OPENAI_API_KEY
    3. ANTHROPIC_API_KEY
    4. GROQ_API_KEY
    """
    # If api_key is provided directly, use it
    if not api_key:
        # Try each supported API key in order of preference
        api_key = (
            os.environ.get("XAI_API_KEY") or
            os.environ.get("OPENAI_API_KEY") or
            os.environ.get("ANTHROPIC_API_KEY") or
            os.environ.get("GROQ_API_KEY")
        )
    
    # Determine which API endpoint to use based on which key is available
    global XAI_API_ENDPOINT
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("XAI_API_KEY"):
        XAI_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
        print(f"{CLIStyle.CYAN}Using OpenAI API endpoint{CLIStyle.RESET}")
    elif os.environ.get("ANTHROPIC_API_KEY") and not (os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        XAI_API_ENDPOINT = "https://api.anthropic.com/v1/messages"
        print(f"{CLIStyle.CYAN}Using Anthropic API endpoint{CLIStyle.RESET}")
    elif os.environ.get("GROQ_API_KEY") and not (os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        XAI_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
        print(f"{CLIStyle.CYAN}Using Groq API endpoint{CLIStyle.RESET}")
    else:
        print(f"{CLIStyle.CYAN}Using X.AI API endpoint{CLIStyle.RESET}")
    
    if not api_key:
        raise ValueError("API key is required. Set XAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GROQ_API_KEY environment variable or provide --api-key argument.")
    
    # Return the appropriate headers for the API
    if "anthropic.com" in XAI_API_ENDPOINT:
        return {
            "Content-Type": "application/json",
            "X-API-Key": f"{api_key}",
            "anthropic-version": "2023-06-01"
        }
    else:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

def parse_stream_chunk(chunk: str) -> Optional[Dict[str, Any]]:
    if not chunk.strip() or chunk.strip() == "data: [DONE]":
        return None
    if chunk.startswith("data: "):
        data = chunk[6:]
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return None

async def handle_tool_calls(tool_calls: list, tools: Tools) -> list:
    tool_results = []
    for tool_call in tool_calls:
        tool_call_id = tool_call.get("id")
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", "{}")
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            args = {}
        if name == "run_python_code":
            code = args.get("code", "")
            print(f"\n{CLIStyle.CYAN}🟦 Running Python code...{CLIStyle.RESET}")
            result = await tools.run_python_code(code)
            tool_results.append({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": result
            })
        elif name == "run_bash_command":
            command = args.get("command", "")
            print(f"\n{CLIStyle.CYAN}🟩 Running Bash command...{CLIStyle.RESET}")
            result = await tools.run_bash_command(command)
            tool_results.append({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": result
            })
        else:
            tool_results.append({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": f"Error: Tool '{name}' is not supported."
            })
    return tool_results

def check_api_key():
    """Check if API key is available and prompt for it if not"""
    # First try XAI key, then fall back to other providers
    api_key = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        print(f"{CLIStyle.YELLOW}No API key found in environment variables.{CLIStyle.RESET}")
        print(f"{CLIStyle.YELLOW}Supported keys: XAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY{CLIStyle.RESET}")
        api_key = Prompt.ask("Enter your API key", password=True)
        if api_key:
            os.environ["XAI_API_KEY"] = api_key
            print(f"{CLIStyle.GREEN}API key set for this session.{CLIStyle.RESET}")
            return True
        else:
            print(f"{CLIStyle.RED}No API key provided. Chat functionality will be limited.{CLIStyle.RESET}")
            return False
    return True

async def run_grok_chat(user_input, messages, tools, model, temperature=0.7, max_tokens=800):
    """Run a chat interaction with the selected AI API"""
    # Get API key from environment or use the first available one
    api_key = (
        os.environ.get("XAI_API_KEY") or
        os.environ.get("OPENAI_API_KEY") or
        os.environ.get("ANTHROPIC_API_KEY") or
        os.environ.get("GROQ_API_KEY")
    )
    
    if not api_key:
        return "Error: No API key available for chat.", []
    
    # Set up the client and get the appropriate headers    
    try:
        headers = setup_client(api_key)
        tool_schemas = get_tool_schema()
        
        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})
        
        # Prepare API call
        print(f"\n{CLIStyle.CYAN}🤖 Assistant:{CLIStyle.RESET} ", end="", flush=True)
        
        # Select appropriate model name and API format based on which endpoint we're using
        if "anthropic.com" in XAI_API_ENDPOINT:
            # Anthropic model naming format
            if "grok" in model.lower():
                model = "claude-3-opus-20240229"  # Default to Claude 3 Opus if using Grok
            payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        elif "openai.com" in XAI_API_ENDPOINT:
            # OpenAI model naming
            if "grok" in model.lower():
                model = "gpt-4o"  # Default to GPT-4o if using Grok name
            payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
        elif "groq.com" in XAI_API_ENDPOINT:
            # Groq model naming
            if "grok" in model.lower():
                model = "llama3-70b-8192"  # Default to Llama 3 70B if using Grok name
            payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
        else:
            # Default X.AI/Grok compatible format
            payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
        # Use requests in a non-blocking way
        response = await asyncio.to_thread(
            lambda: requests.post(
                XAI_API_ENDPOINT,
                headers=headers,
                json=payload,
                stream=True
            )
        )
        
        if response.status_code != 200:
            error_msg = f"\n{CLIStyle.RED}API Error ({response.status_code}): {response.text}{CLIStyle.RESET}"
            print(error_msg)
            return error_msg, []
            
        assistant_content = ""
        assistant_tool_calls = []
        current_tool_calls = {}
        
        for line in response.iter_lines():
            if not line:
                continue
            chunk_str = line.decode('utf-8')
            if chunk_str.strip() == "data: [DONE]":
                continue
            if chunk_str.startswith("data: "):
                try:
                    chunk_data = json.loads(chunk_str[6:])
                except json.JSONDecodeError:
                    continue
                choices = chunk_data.get("choices", [])
                if not choices:
                    continue
                choice = choices[0]
                delta = choice.get("delta", {})
                if "content" in delta and delta["content"]:
                    content = delta["content"]
                    assistant_content += content
                    print(f"{CLIStyle.WHITE}{content}{CLIStyle.RESET}", end="", flush=True)
                if "tool_calls" in delta:
                    tool_calls_delta = delta["tool_calls"]
                    for tool_call_delta in tool_calls_delta:
                        index = tool_call_delta.get("index", 0)
                        if index not in current_tool_calls:
                            current_tool_calls[index] = {
                                "id": "",
                                "function": {"name": "", "arguments": ""}
                            }
                        if "id" in tool_call_delta:
                            current_tool_calls[index]["id"] = tool_call_delta["id"]
                        if "function" in tool_call_delta and "name" in tool_call_delta["function"]:
                            current_tool_calls[index]["function"]["name"] = tool_call_delta["function"]["name"]
                        if "function" in tool_call_delta and "arguments" in tool_call_delta["function"]:
                            current_tool_calls[index]["function"]["arguments"] += tool_call_delta["function"]["arguments"]
        
        assistant_tool_calls = list(current_tool_calls.values())
        
        # Add assistant message to conversation history
        messages.append({"role": "assistant", "content": assistant_content, "tool_calls": assistant_tool_calls})
        
        return assistant_content, assistant_tool_calls
        
    except Exception as e:
        error_msg = f"\n{CLIStyle.RED}Error in API call: {str(e)}{CLIStyle.RESET}"
        print(error_msg)
        return error_msg, []

def test_api_access():
    """Test if we can access the configured API endpoint with available credentials"""
    # First, identify which API key we have
    api_key = (
        os.environ.get("XAI_API_KEY") or
        os.environ.get("OPENAI_API_KEY") or
        os.environ.get("ANTHROPIC_API_KEY") or
        os.environ.get("GROQ_API_KEY")
    )
    
    if not api_key:
        print(f"{CLIStyle.YELLOW}No API key found to test connection.{CLIStyle.RESET}")
        return False
    
    # Determine which endpoint to use
    endpoint = XAI_API_ENDPOINT
    headers = setup_client(api_key)
    
    # Create a simple test request (models list is typically lightweight)
    test_url = endpoint.rsplit('/', 1)[0] + "/models" if "/chat/completions" in endpoint else endpoint
    
    try:
        import requests
        print(f"{CLIStyle.CYAN}Testing API connection to {test_url}...{CLIStyle.RESET}")
        response = requests.get(
            test_url,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"{CLIStyle.GREEN}API connection successful! ✅{CLIStyle.RESET}")
            return True
        else:
            print(f"{CLIStyle.RED}API connection failed: {response.status_code} - {response.text} ❌{CLIStyle.RESET}")
            return False
    except Exception as e:
        print(f"{CLIStyle.RED}Error testing API connection: {str(e)} ❌{CLIStyle.RESET}")
        return False

async def interactive_cli():
    """Run an interactive chat-based CLI for code execution with AI integration"""
    # Load environment variables first
    print(f"{CLIStyle.CYAN}Loading environment variables...{CLIStyle.RESET}")
    load_env()
    
    # Test if we can access the API with current credentials
    api_working = test_api_access()
    
    swarm_logo = load_swarm_logo()
    tools = Tools()
    
    # Get API credentials and model configuration
    api_key = (
        os.environ.get("XAI_API_KEY") or
        os.environ.get("OPENAI_API_KEY") or
        os.environ.get("ANTHROPIC_API_KEY") or
        os.environ.get("GROQ_API_KEY")
    )
    
    # Determine appropriate default model based on available API key
    if os.environ.get("OPENAI_API_KEY") and not os.environ.get("XAI_API_KEY"):
        model = os.environ.get("MODEL", "gpt-4o")
    elif os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("XAI_API_KEY"):
        model = os.environ.get("MODEL", "claude-3-opus-20240229")
    elif os.environ.get("GROQ_API_KEY") and not (os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        model = os.environ.get("MODEL", "llama3-70b-8192")
    else:
        model = os.environ.get("MODEL", "grok-3-mini-beta")
        
    temperature = float(os.environ.get("TEMPERATURE", 0.7))
    max_tokens = int(os.environ.get("MAX_TOKENS", 800))
    
    # Check for API key or prompt user
    has_api_key = check_api_key() and api_working
    
    # Logo and header
    logo = swarm_logo or "🛠️  CODE EXECUTOR MODULE 🛠️"
    print(f"\n{CLIStyle.GREEN}{logo}{CLIStyle.RESET}")
    print(f"{CLIStyle.MAGENTA}{'='*80}{CLIStyle.RESET}")
    print(f"{CLIStyle.YELLOW}HERD AI CODE EXECUTOR - INTERACTIVE CHAT CLI{CLIStyle.RESET}")
    print(f"{CLIStyle.MAGENTA}{'='*80}{CLIStyle.RESET}")
    print(f"{CLIStyle.CYAN}This module provides an AI-powered chat interface for code execution.\n"
          f"  {CLIStyle.YELLOW}- Chat with the AI assistant about code or ask it to run code for you\n"
          f"  - For direct execution without AI, prefix Python code with 'run:'\n"
          f"  - For direct Bash commands, prefix with '!', e.g. !ls -la\n"
          f"  - Type 'test all' to run tool tests\n"
          f"  - Type 'verify api' to test the API connection\n"
          f"{CLIStyle.CYAN}Type {CLIStyle.YELLOW}'exit', 'quit', or Ctrl+C{CLIStyle.CYAN} to return to main menu.{CLIStyle.RESET}")
    print(f"{CLIStyle.MAGENTA}{'='*80}{CLIStyle.RESET}\n")
    
    # Initialize system prompt and message history
    system_prompt = (
        "You are a secure code execution assistant module for Herd AI. "
        "When needed, execute Python code or Bash commands using the run_python_code or run_bash_command tools. "
        "Always return the output or error in a clear, accessible format. "
        "Use this tool for: code debugging, output inspection, and safe command execution. "
        "Do not execute unsafe or destructive commands. Think step by step and provide comprehensive, auditable results."
    )
    messages = [{"role": "system", "content": system_prompt}]
    
    # Print intro message based on API key availability
    if has_api_key:
        print(f"{CLIStyle.GREEN}AI Assistant is enabled with {model}. Ask questions or provide code to execute.{CLIStyle.RESET}")
    else:
        if api_key:
            print(f"{CLIStyle.YELLOW}API key found but connection test failed. Running in direct execution mode.{CLIStyle.RESET}")
        else:
            print(f"{CLIStyle.YELLOW}Running in direct execution mode due to missing API key.{CLIStyle.RESET}")
    
    try:
        while True:
            # Get user input
            user_input = input(f"\n{CLIStyle.YELLOW}🧑 Query:{CLIStyle.RESET} ")
            
            # Handle exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n{CLIStyle.GREEN}Returning to main menu. 👋{CLIStyle.RESET}")
                break
                
            # Test all features
            if user_input.strip().lower() == "test all":
                print(f"\n{CLIStyle.CYAN}Running all tool tests...{CLIStyle.RESET}")
                print(f"\n{CLIStyle.BLUE}[run_python_code] test:{CLIStyle.RESET}")
                py_result = await tools.run_python_code("print('Hello from Python!')")
                print(py_result)
                print(f"\n{CLIStyle.BLUE}[run_bash_command] test:{CLIStyle.RESET}")
                bash_result = await tools.run_bash_command("echo 'Hello from Bash!'")
                print(bash_result)
                continue
            
            # Test API connection
            if user_input.strip().lower() == "verify api":
                api_working = test_api_access()
                has_api_key = check_api_key() and api_working
                if has_api_key:
                    print(f"{CLIStyle.GREEN}AI Assistant connection verified. Ready to chat!{CLIStyle.RESET}")
                continue
                
            # Direct execution commands
            if user_input.startswith('run:'):
                # Direct Python execution
                code = user_input[4:].strip()
                print(f"\n{CLIStyle.BLUE}Running Python code:{CLIStyle.RESET}")
                result = await tools.run_python_code(code)
                print(f"\n{CLIStyle.GREEN}Result:{CLIStyle.RESET}\n{result}")
                continue
                
            if user_input.startswith('!'):
                # Direct Bash execution
                bash_command = user_input[1:].strip()
                print(f"\n{CLIStyle.BLUE}Running Bash command: {bash_command}{CLIStyle.RESET}")
                result = await tools.run_bash_command(bash_command)
                print(f"\n{CLIStyle.GREEN}Result:{CLIStyle.RESET}\n{result}")
                continue
            
            # Use AI assistant if API key is available
            if has_api_key:
                # Get response from Grok
                assistant_content, assistant_tool_calls = await run_grok_chat(
                    user_input, messages, tools, model, temperature, max_tokens
                )
                
                # Process tool calls if any
                if assistant_tool_calls:
                    tool_results = await handle_tool_calls(assistant_tool_calls, tools)
                    for tool_result in tool_results:
                        messages.append(tool_result)
                        content_str = tool_result.get("content", "")
                        if content_str:
                            print(f"\n{CLIStyle.GREEN}Tool Output:{CLIStyle.RESET}\n{content_str}")
            else:
                # Fallback to direct execution when no API key
                print(f"\n{CLIStyle.YELLOW}AI chat unavailable (no API key or connection failed).\nUse 'run:' or '!' prefixes for direct execution, or type 'verify api' to check API connection.{CLIStyle.RESET}")
                print(f"\n{CLIStyle.BLUE}Running as Python code:{CLIStyle.RESET}")
                result = await tools.run_python_code(user_input)
                print(f"\n{CLIStyle.GREEN}Result:{CLIStyle.RESET}\n{result}")
                
    except KeyboardInterrupt:
        print(f"\n\n{CLIStyle.GREEN}Returning to main menu. 👋{CLIStyle.RESET}")
    except Exception as e:
        print(f"\n\n{CLIStyle.RED}Error: {str(e)}{CLIStyle.RESET}")
        print(f"{CLIStyle.YELLOW}Returning to main menu...{CLIStyle.RESET}")

if __name__ == "__main__":
    asyncio.run(interactive_cli()) 