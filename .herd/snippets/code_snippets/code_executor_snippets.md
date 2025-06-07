# Code Snippets from src/herd_ai/utils/code_executor.py

File: `src/herd_ai/utils/code_executor.py`  
Language: Python  
Extracted: 2025-06-07 05:09:48  

## Snippet 1
Lines 7-12

```Python
as a standalone CLI for debugging and output retrieval.

Features:
- Conversational AI assistant with code execution capabilities
- Secure Python and Bash execution (tempfile, restricted env)
- CLI with accessible, colorized output
```

## Snippet 2
Lines 14-18

```Python
- XAI API key support for tool calls

Usage:
  python -m herd_ai.code_executor           # Launch interactive CLI
  herd --exec                               # Launch from herd.py CLI
```

## Snippet 3
Lines 20-34

```Python
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
```

## Snippet 4
Lines 42-45

```Python
if default:
                prompt_str += f"(default: {default}) "
            response = input(prompt_str)
            return response or default
```

## Snippet 5
Lines 48-50

```Python
try:
    from dotenv import load_dotenv
except ImportError:
```

## Snippet 6
Lines 57-68

```Python
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
```

## Snippet 7
Lines 69-84

```Python
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
```

## Snippet 8
Lines 86-91

```Python
if os.path.exists(env_path):
                print(f"{CLIStyle.CYAN}Loading environment from: {env_path}{CLIStyle.RESET}")
                load_dotenv(dotenv_path=env_path)
                env_loaded = True
                break
```

## Snippet 9
Lines 104-106

```Python
if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    os.environ[key] = value[1:-1]
                    print(f"{CLIStyle.CYAN}Stripped quotes from {key}{CLIStyle.RESET}")
```

## Snippet 10
Lines 113-115

```Python
if os.path.exists(swarm_path):
        try:
            with open(swarm_path, 'r', encoding='utf-8') as f:
```

## Snippet 11
Lines 126-129

```Python
def __init__(self):
        self.python_path = sys.executable
        self.temp_dir = tempfile.gettempdir()
```

## Snippet 12
Lines 130-148

```Python
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
```

## Snippet 13
Lines 159-173

```Python
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
```

## Snippet 14
Lines 182-219

```Python
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
```

## Snippet 15
Lines 224-228

```Python
def register_with_registry(registry):
    """Register tools with the provided registry."""
    tools_schema = get_tool_schema()

    # Register each tool
```

## Snippet 16
Lines 229-243

```Python
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
```

## Snippet 17
Lines 244-253

```Python
def setup_client(api_key: Optional[str] = None) -> Dict[str, str]:
    """Set up API client headers based on available API keys

    Supports multiple API providers with the following priority:
    1. XAI_API_KEY
    2. OPENAI_API_KEY
    3. ANTHROPIC_API_KEY
    4. GROQ_API_KEY
    """
    # If api_key is provided directly, use it
```

## Snippet 18
Lines 254-264

```Python
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
```

## Snippet 19
Lines 271-276

```Python
elif os.environ.get("GROQ_API_KEY") and not (os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")):
        XAI_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
        print(f"{CLIStyle.CYAN}Using Groq API endpoint{CLIStyle.RESET}")
    else:
        print(f"{CLIStyle.CYAN}Using X.AI API endpoint{CLIStyle.RESET}")
```

## Snippet 20
Lines 281-292

```Python
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
```

## Snippet 21
Lines 296-303

```Python
if chunk.startswith("data: "):
        data = chunk[6:]
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return None
```

## Snippet 22
Lines 308-314

```Python
function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", "{}")
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError:
            args = {}
```

## Snippet 23
Lines 315-323

```Python
if name == "run_python_code":
            code = args.get("code", "")
            print(f"\n{CLIStyle.CYAN}🟦 Running Python code...{CLIStyle.RESET}")
            result = await tools.run_python_code(code)
            tool_results.append({
                "tool_call_id": tool_call_id,
                "role": "tool",
                "content": result
            })
```

## Snippet 24
Lines 324-338

```Python
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
```

## Snippet 25
Lines 346-349

```Python
if not api_key:
        print(f"{CLIStyle.YELLOW}No API key found in environment variables.{CLIStyle.RESET}")
        print(f"{CLIStyle.YELLOW}Supported keys: XAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY{CLIStyle.RESET}")
        api_key = Prompt.ask("Enter your API key", password=True)
```

## Snippet 26
Lines 354-356

```Python
else:
            print(f"{CLIStyle.RED}No API key provided. Chat functionality will be limited.{CLIStyle.RESET}")
            return False
```

## Snippet 27
Lines 359-368

```Python
async def run_grok_chat(user_input, messages, tools, model, temperature=0.7, max_tokens=800):
    """Run a chat interaction with the selected AI API"""
    # Get API key from environment or use the first available one
    api_key = (
        os.environ.get("XAI_API_KEY") or
        os.environ.get("OPENAI_API_KEY") or
        os.environ.get("ANTHROPIC_API_KEY") or
        os.environ.get("GROQ_API_KEY")
    )
```

## Snippet 28
Lines 372-380

```Python
# Set up the client and get the appropriate headers
    try:
        headers = setup_client(api_key)
        tool_schemas = get_tool_schema()

        # Add user message to conversation
        messages.append({"role": "user", "content": user_input})

        # Prepare API call
```

## Snippet 29
Lines 388-394

```Python
payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
```

## Snippet 30
Lines 399-406

```Python
payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
```

## Snippet 31
Lines 411-418

```Python
payload = {
                "model": model,
                "messages": messages,
                "tools": tool_schemas,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
```

## Snippet 32
Lines 419-439

```Python
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
```

## Snippet 33
Lines 440-448

```Python
if response.status_code != 200:
            error_msg = f"\n{CLIStyle.RED}API Error ({response.status_code}): {response.text}{CLIStyle.RESET}"
            print(error_msg)
            return error_msg, []

        assistant_content = ""
        assistant_tool_calls = []
        current_tool_calls = {}
```

## Snippet 34
Lines 450-452

```Python
if not line:
                continue
            chunk_str = line.decode('utf-8')
```

## Snippet 35
Lines 455-460

```Python
if chunk_str.startswith("data: "):
                try:
                    chunk_data = json.loads(chunk_str[6:])
                except json.JSONDecodeError:
                    continue
                choices = chunk_data.get("choices", [])
```

## Snippet 36
Lines 461-464

```Python
if not choices:
                    continue
                choice = choices[0]
                delta = choice.get("delta", {})
```

## Snippet 37
Lines 473-477

```Python
if index not in current_tool_calls:
                            current_tool_calls[index] = {
                                "id": "",
                                "function": {"name": "", "arguments": ""}
                            }
```

## Snippet 38
Lines 485-491

```Python
assistant_tool_calls = list(current_tool_calls.values())

        # Add assistant message to conversation history
        messages.append({"role": "assistant", "content": assistant_content, "tool_calls": assistant_tool_calls})

        return assistant_content, assistant_tool_calls
```

## Snippet 39
Lines 492-496

```Python
except Exception as e:
        error_msg = f"\n{CLIStyle.RED}Error in API call: {str(e)}{CLIStyle.RESET}"
        print(error_msg)
        return error_msg, []
```

## Snippet 40
Lines 498-506

```Python
"""Test if we can access the configured API endpoint with available credentials"""
    # First, identify which API key we have
    api_key = (
        os.environ.get("XAI_API_KEY") or
        os.environ.get("OPENAI_API_KEY") or
        os.environ.get("ANTHROPIC_API_KEY") or
        os.environ.get("GROQ_API_KEY")
    )
```

## Snippet 41
Lines 507-515

```Python
if not api_key:
        print(f"{CLIStyle.YELLOW}No API key found to test connection.{CLIStyle.RESET}")
        return False

    # Determine which endpoint to use
    endpoint = XAI_API_ENDPOINT
    headers = setup_client(api_key)

    # Create a simple test request (models list is typically lightweight)
```

## Snippet 42
Lines 516-526

```Python
test_url = endpoint.rsplit('/', 1)[0] + "/models" if "/chat/completions" in endpoint else endpoint

    try:
        import requests
        print(f"{CLIStyle.CYAN}Testing API connection to {test_url}...{CLIStyle.RESET}")
        response = requests.get(
            test_url,
            headers=headers,
            timeout=5
        )
```

## Snippet 43
Lines 527-530

```Python
if response.status_code == 200:
            print(f"{CLIStyle.GREEN}API connection successful! ✅{CLIStyle.RESET}")
            return True
        else:
```

## Snippet 44
Lines 543-557

```Python
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
```

## Snippet 45
Lines 562-569

```Python
elif os.environ.get("GROQ_API_KEY") and not (os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")):
        model = os.environ.get("MODEL", "llama3-70b-8192")
    else:
        model = os.environ.get("MODEL", "grok-3-mini-beta")

    temperature = float(os.environ.get("TEMPERATURE", 0.7))
    max_tokens = int(os.environ.get("MAX_TOKENS", 800))
```

## Snippet 46
Lines 570-578

```Python
# Check for API key or prompt user
    has_api_key = check_api_key() and api_working

    # Logo and header
    logo = swarm_logo or "🛠️  CODE EXECUTOR MODULE 🛠️"
    print(f"\n{CLIStyle.GREEN}{logo}{CLIStyle.RESET}")
    print(f"{CLIStyle.MAGENTA}{'='*80}{CLIStyle.RESET}")
    print(f"{CLIStyle.YELLOW}HERD AI CODE EXECUTOR - INTERACTIVE CHAT CLI{CLIStyle.RESET}")
    print(f"{CLIStyle.MAGENTA}{'='*80}{CLIStyle.RESET}")
```

## Snippet 47
Lines 580-584

```Python
f"  {CLIStyle.YELLOW}- Chat with the AI assistant about code or ask it to run code for you\n"
          f"  - For direct execution without AI, prefix Python code with 'run:'\n"
          f"  - For direct Bash commands, prefix with '!', e.g. !ls -la\n"
          f"  - Type 'test all' to run tool tests\n"
          f"  - Type 'verify api' to test the API connection\n"
```

## Snippet 48
Lines 590-594

```Python
"You are a secure code execution assistant module for Herd AI. "
        "When needed, execute Python code or Bash commands using the run_python_code or run_bash_command tools. "
        "Always return the output or error in a clear, accessible format. "
        "Use this tool for: code debugging, output inspection, and safe command execution. "
        "Do not execute unsafe or destructive commands. Think step by step and provide comprehensive, auditable results."
```

## Snippet 49
Lines 599-601

```Python
if has_api_key:
        print(f"{CLIStyle.GREEN}AI Assistant is enabled with {model}. Ask questions or provide code to execute.{CLIStyle.RESET}")
    else:
```

## Snippet 50
Lines 602-606

```Python
if api_key:
            print(f"{CLIStyle.YELLOW}API key found but connection test failed. Running in direct execution mode.{CLIStyle.RESET}")
        else:
            print(f"{CLIStyle.YELLOW}Running in direct execution mode due to missing API key.{CLIStyle.RESET}")
```

## Snippet 51
Lines 618-628

```Python
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
```

## Snippet 52
Lines 632-635

```Python
if has_api_key:
                    print(f"{CLIStyle.GREEN}AI Assistant connection verified. Ready to chat!{CLIStyle.RESET}")
                continue
```

## Snippet 53
Lines 637-644

```Python
if user_input.startswith('run:'):
                # Direct Python execution
                code = user_input[4:].strip()
                print(f"\n{CLIStyle.BLUE}Running Python code:{CLIStyle.RESET}")
                result = await tools.run_python_code(code)
                print(f"\n{CLIStyle.GREEN}Result:{CLIStyle.RESET}\n{result}")
                continue
```

## Snippet 54
Lines 645-652

```Python
if user_input.startswith('!'):
                # Direct Bash execution
                bash_command = user_input[1:].strip()
                print(f"\n{CLIStyle.BLUE}Running Bash command: {bash_command}{CLIStyle.RESET}")
                result = await tools.run_bash_command(bash_command)
                print(f"\n{CLIStyle.GREEN}Result:{CLIStyle.RESET}\n{result}")
                continue
```

## Snippet 55
Lines 654-659

```Python
if has_api_key:
                # Get response from Grok
                assistant_content, assistant_tool_calls = await run_grok_chat(
                    user_input, messages, tools, model, temperature, max_tokens
                )
```

## Snippet 56
Lines 663-665

```Python
for tool_result in tool_results:
                        messages.append(tool_result)
                        content_str = tool_result.get("content", "")
```

## Snippet 57
Lines 675-680

```Python
except KeyboardInterrupt:
        print(f"\n\n{CLIStyle.GREEN}Returning to main menu. 👋{CLIStyle.RESET}")
    except Exception as e:
        print(f"\n\n{CLIStyle.RED}Error: {str(e)}{CLIStyle.RESET}")
        print(f"{CLIStyle.YELLOW}Returning to main menu...{CLIStyle.RESET}")
```

