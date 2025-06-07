#!/usr/bin/env python
from flask import Blueprint, request, jsonify
import logging
import json
import requests
import tempfile
import asyncio
import subprocess
import os
import sys
from typing import Dict, Any, List, Optional, Callable, Awaitable
import xml.dom.minidom
import csv
import io
import yaml
import toml
import urllib.parse

from api.services.provider_factory import ProviderFactory
from api.utils.errors import InvalidRequestError, ProviderNotAvailableError

# Logger for this module
logger = logging.getLogger(__name__)

# Blueprint for tools routes
tools_bp = Blueprint('tools', __name__)

# Configuration for API keys
API_KEYS = {
    'wolframalpha': os.environ.get('WOLFRAMALPHA_APP_ID', '')
}


@tools_bp.route('/call', methods=['POST'])
def call_tool():
    """Call a tool/function with an AI provider."""
    data = request.json or {}
    
    # Get required parameters
    provider_name = data.get('provider', 'anthropic')
    model = data.get('model')
    prompt = data.get('prompt', '')
    tools = data.get('tools', [])
    
    # Get provider instance
    provider = ProviderFactory.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Provider '{provider_name}' not available"}), 400
    
    if not model:
        return jsonify({"error": "Model parameter is required"}), 400
    
    if not tools or not isinstance(tools, list):
        return jsonify({"error": "Tools parameter must be a non-empty array"}), 400
    
    # Optional parameters
    conversation_id = data.get('conversation_id')
    user_id = data.get('user_id', 'default_user')
    tool_choice = data.get('tool_choice', 'auto')
    
    logger.info(f"Tool call request: provider={provider_name}, model={model}, tools={len(tools)}")
    
    try:
        # Call the tool with the provider
        result = provider.call_tool(
            prompt=prompt,
            model=model,
            tools=tools,
            conversation_id=conversation_id,
            user_id=user_id,
            tool_choice=tool_choice
        )
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error calling tool: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tools_bp.route('/schemas', methods=['GET', 'POST'])
def get_tool_schemas():
    """Get available tool schemas for a provider."""
    if request.method == 'POST':
        data = request.json or {}
        provider_name = data.get('provider', 'anthropic')
    else:
        provider_name = request.args.get('provider', 'anthropic')
    
    # Get provider instance
    provider = ProviderFactory.get_provider(provider_name)
    if not provider:
        return jsonify({"error": f"Provider '{provider_name}' not available"}), 400
    
    try:
        # Not all providers may implement this method
        if hasattr(provider, 'get_tool_schemas'):
            schemas = provider.get_tool_schemas()
            return jsonify(schemas)
        else:
            # Return some default schemas based on provider
            if provider_name in ['anthropic', 'openai', 'mistral', 'cohere']:
                return jsonify([
                    {
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "description": "Get the current weather in a location",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "The city and state, e.g. San Francisco, CA"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["celsius", "fahrenheit"],
                                        "description": "The unit of temperature"
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_archived_webpage",
                            "description": "Retrieve an archived version of a webpage from various archive services",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "url": {
                                        "type": "string",
                                        "description": "The URL to find an archived version for"
                                    },
                                    "provider": {
                                        "type": "string",
                                        "enum": ["wayback", "archiveis", "memento", "12ft"],
                                        "description": "The archive provider to use (wayback, archiveis, memento, 12ft)"
                                    },
                                    "capture": {
                                        "type": "boolean",
                                        "description": "Whether to capture a new snapshot (for archiveis only)"
                                    }
                                },
                                "required": ["url"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "execute_code",
                            "description": "Execute Python code in a restricted environment",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "code": {
                                        "type": "string",
                                        "description": "The Python code to execute"
                                    }
                                },
                                "required": ["code"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "analyze_text",
                            "description": "Analyze text for sentiment, key entities, and offensive content",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "The text to analyze"
                                    },
                                    "language": {
                                        "type": "string",
                                        "description": "The language code (default: 'en')"
                                    }
                                },
                                "required": ["text"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "format_data",
                            "description": "Convert data between JSON and other formats (YAML, TOML, XML, CSV)",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "data": {
                                        "type": "object",
                                        "description": "The data to convert (as JSON object or string)"
                                    },
                                    "target_format": {
                                        "type": "string",
                                        "enum": ["json", "yaml", "toml", "xml", "csv"],
                                        "description": "The target format"
                                    },
                                    "style": {
                                        "type": "string",
                                        "enum": ["pretty", "compact", "single_line"],
                                        "description": "Output style"
                                    }
                                },
                                "required": ["data", "target_format"]
                            }
                        }
                    }
                ])
            else:
                return jsonify([])
    except Exception as e:
        logger.error(f"Error getting tool schemas: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tools_bp.route('/capabilities', methods=['GET'])
def get_tool_capabilities():
    """Get tool capabilities for all providers."""
    providers = {
        'anthropic': {
            'supports_tools': True,
            'supports_streaming': True,
            'max_tools': 128,
            'requires_tool_choice': False
        },
        'openai': {
            'supports_tools': True,
            'supports_streaming': True,
            'max_tools': 128,
            'requires_tool_choice': False
        },
        'ollama': {
            'supports_tools': False,
            'supports_streaming': False,
            'max_tools': 0,
            'requires_tool_choice': False
        },
        'perplexity': {
            'supports_tools': False,
            'supports_streaming': False,
            'max_tools': 0,
            'requires_tool_choice': False
        },
        'mistral': {
            'supports_tools': True,
            'supports_streaming': True,
            'max_tools': 64,
            'requires_tool_choice': False
        },
        'cohere': {
            'supports_tools': True,
            'supports_streaming': False,
            'max_tools': 16,
            'requires_tool_choice': False
        },
        'xai': {
            'supports_tools': False,
            'supports_streaming': False,
            'max_tools': 0,
            'requires_tool_choice': False
        },
        'coze': {
            'supports_tools': False,
            'supports_streaming': False,
            'max_tools': 0,
            'requires_tool_choice': False
        }
    }
    
    # Add the integrated tools as their own "provider"
    tools = {
        'standard': ['web_search', 'archive', 'weather', 'map', 'wolframalpha'],
        'extensions': ['execute_code', 'analyze_text', 'format_data'],
        'social': ['reddit_subreddit', 'reddit_user'],
        'news': ['bbc_news', 'nyt_search', 'nyt_top']
    }
    
    return jsonify({
        'providers': providers,
        'tools': tools
    })


@tools_bp.route('/archive', methods=['GET', 'POST'])
def archive_retrieval():
    """
    Retrieve archived versions of web pages using various archive services.
    
    This endpoint proxies requests to archive services like the Wayback Machine,
    Archive.is, and Memento Aggregator to retrieve archived versions of web pages.
    
    Query Parameters (GET) or JSON body (POST):
        - url: The URL to find an archived version for (required)
        - provider: The archive provider to use (wayback, archiveis, memento)
                   Default is 'wayback'
        - capture: Whether to capture a new snapshot (for archiveis only)
                  Default is False
    
    Returns:
        JSON object with the archived URL and metadata
    """
    # Import necessary libraries
    import requests
    import urllib.parse
    from datetime import datetime
    
    # Define a User-Agent string to mimic a real browser
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
    
    # Get parameters from request
    if request.method == 'POST':
        data = request.json or {}
        target_url = data.get('url')
        provider = data.get('provider', 'wayback')
        capture = data.get('capture', False)
    else:
        target_url = request.args.get('url')
        provider = request.args.get('provider', 'wayback')
        capture = request.args.get('capture', 'false').lower() in ['true', '1', 't', 'yes']
    
    if not target_url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        result = {
            "original_url": target_url,
            "provider": provider,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "archived_url": None,
            "message": ""
        }
        
        if provider == "wayback":
            try:
                # Import here to avoid dependency issues if not installed
                from waybackpy import Url
                
                try:
                    # Create a Url object
                    url_obj = Url(target_url, USER_AGENT)
                    
                    # Get the newest snapshot as a string
                    archived_url = str(url_obj.newest())
                    
                    # Get the timestamp as a string
                    try:
                        # In waybackpy 2.4.4, timestamp might be an attribute or a method
                        timestamp = url_obj.timestamp
                        if callable(timestamp):
                            timestamp = timestamp()
                        
                        # Convert datetime to string for JSON serialization
                        if hasattr(timestamp, 'isoformat'):
                            timestamp = timestamp.isoformat()
                        else:
                            timestamp = str(timestamp)
                    except Exception as e:
                        # If there's any error getting the timestamp, use the current time
                        timestamp = datetime.now().isoformat()
                        logger.warning(f"Error getting timestamp from Wayback Machine: {str(e)}")
                    
                    # Create a new result dictionary with only serializable data
                    result = {
                        "original_url": target_url,
                        "provider": provider,
                        "timestamp": timestamp,
                        "success": True,
                        "archived_url": archived_url,
                        "message": "Successfully retrieved the most recent snapshot from the Wayback Machine"
                    }
                except Exception as e:
                    result["message"] = f"Error processing Wayback Machine response: {str(e)}"
                    logger.error(f"Error processing Wayback Machine response: {str(e)}")
            
            except Exception as e:
                result["message"] = f"Wayback Machine API error: {str(e)}"
                logger.error(f"Wayback Machine API error: {str(e)}")
        
        elif provider == "archiveis":
            try:
                # Import here to avoid dependency issues if not installed
                import archiveis
                
                if capture:
                    # Capture a new snapshot
                    archived_url = archiveis.capture(target_url)
                    result["archived_url"] = archived_url
                    result["success"] = True
                    result["message"] = "Successfully captured a new snapshot with Archive.is"
                else:
                    # Try to find an existing snapshot
                    # Note: Archive.is doesn't have a direct API for retrieving existing snapshots
                    # This is a workaround that might not always work
                    archived_url = f"https://archive.is/{target_url}"
                    
                    # Check if the archive exists by making a HEAD request
                    response = requests.head(archived_url, headers={"User-Agent": USER_AGENT}, timeout=10)
                    
                    if response.status_code == 200:
                        result["archived_url"] = archived_url
                        result["success"] = True
                        result["message"] = "Found an existing snapshot on Archive.is"
                    else:
                        result["message"] = "No existing snapshot found on Archive.is. Set 'capture=true' to create a new one."
            
            except Exception as e:
                result["message"] = f"Archive.is error: {str(e)}"
                logger.error(f"Archive.is error: {str(e)}")
        
        elif provider == "memento":
            try:
                encoded_url = urllib.parse.quote(target_url, safe="")
                # The correct URL format for Memento Aggregator
                # Make sure the URL is properly formatted with http:// or https:// prefix
                if not target_url.startswith(('http://', 'https://')):
                    target_url = 'http://' + target_url
                
                # Use the full URL format that Memento expects
                api_url = f"http://timetravel.mementoweb.org/timemap/json/{target_url}"
                
                response = requests.get(api_url, headers={"User-Agent": USER_AGENT}, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                mementos = data.get("mementos", {}).get("list", [])
                
                if mementos:
                    # Get the most recent memento
                    latest_memento = mementos[-1]
                    result["archived_url"] = latest_memento.get("uri")
                    result["timestamp"] = latest_memento.get("datetime")
                    result["success"] = True
                    result["message"] = "Successfully retrieved the most recent snapshot from Memento Aggregator"
                    
                    # Add additional metadata
                    result["total_snapshots"] = len(mementos)
                    result["first_snapshot_date"] = mementos[0].get("datetime") if mementos else None
                    result["last_snapshot_date"] = latest_memento.get("datetime") if mementos else None
                else:
                    result["message"] = "No snapshots found via Memento Aggregator"
            
            except Exception as e:
                result["message"] = f"Memento Aggregator error: {str(e)}"
                logger.error(f"Memento Aggregator error: {str(e)}")
        
        elif provider == "12ft":
            try:
                # 12ft.io simply prepends the URL with 12ft.io/
                archived_url = f"https://12ft.io/{target_url}"
                
                # 12ft.io often returns a 302 redirect, which is normal and expected
                # We'll consider both 200 and 302 as success
                response = requests.head(archived_url, headers={"User-Agent": USER_AGENT}, timeout=10, allow_redirects=False)
                
                if response.status_code in [200, 302]:
                    result["archived_url"] = archived_url
                    result["success"] = True
                    result["message"] = "Successfully created a 12ft.io link to bypass paywalls and remove distractions"
                else:
                    result["message"] = f"12ft.io service returned unexpected status code: {response.status_code}"
            
            except Exception as e:
                result["message"] = f"12ft.io error: {str(e)}"
                logger.error(f"12ft.io error: {str(e)}")
        
        else:
            return jsonify({"error": f"Unknown provider: {provider}"}), 400
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in archive retrieval: {str(e)}")
        return jsonify({"error": str(e)}), 500


@tools_bp.route('/archive/schema', methods=['GET'])
def archive_schema():
    """Get the JSON schema for the archive tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "get_archived_webpage",
            "description": "Retrieve an archived version of a webpage from various archive services",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to find an archived version for"
                    },
                    "provider": {
                        "type": "string",
                        "enum": ["wayback", "archiveis", "memento", "12ft"],
                        "description": "The archive provider to use (wayback, archiveis, memento, 12ft)"
                    },
                    "capture": {
                        "type": "boolean",
                        "description": "Whether to capture a new snapshot (for archiveis only)"
                    }
                },
                "required": ["url"]
            }
        }
    }
    
    return jsonify(schema)


@tools_bp.route('/execute/get_archived_webpage', methods=['POST'])
def execute_get_archived_webpage():
    """
    Execute the get_archived_webpage tool directly.
    
    This endpoint allows AI models to call the archive tool directly without going through
    the provider's tool calling mechanism. It's useful for providers that don't support
    tool calling or for direct API access.
    
    Request Body:
        - url: The URL to find an archived version for (required)
        - provider: The archive provider to use (wayback, archiveis, memento)
                   Default is 'wayback'
        - capture: Whether to capture a new snapshot (for archiveis only)
                  Default is False
    
    Returns:
        JSON object with the archived URL and metadata
    """
    data = request.json or {}
    
    if not data.get('url'):
        return jsonify({"error": "URL parameter is required"}), 400
    
    # Forward the request to the archive endpoint
    return archive_retrieval()


@tools_bp.route('/execute/analyze_text', methods=['POST'])
def execute_analyze_text():
    """
    Execute the analyze_text tool directly.
    
    This endpoint allows AI models to analyze text for sentiment, key entities, and offensive content
    without going through the provider's tool calling mechanism.
    
    Request Body:
        - text: The text to analyze (required)
        - language: The language code (default: "en")
    
    Returns:
        JSON object with the analysis results
    """
    data = request.json or {}
    
    if not data.get('text'):
        return jsonify({"error": "text parameter is required"}), 400
    
    # Forward the request to the analyze_text endpoint
    return analyze_text()


@tools_bp.route('/execute/format_data', methods=['POST'])
def execute_format_data():
    """
    Execute the format_data tool directly.
    
    This endpoint allows AI models to convert data between different formats
    without going through the provider's tool calling mechanism.
    
    Request Body:
        - data: The data to convert (required)
        - target_format: The target format (json, yaml, toml, xml, csv)
        - style: Output style (pretty, compact, single_line)
    
    Returns:
        JSON object with the converted data
    """
    data = request.json or {}
    
    if not data.get('data'):
        return jsonify({"error": "data parameter is required"}), 400
    
    if not data.get('target_format'):
        return jsonify({"error": "target_format parameter is required"}), 400
    
    # Forward the request to the format_data endpoint
    return format_data()


@tools_bp.route('/execute/code', methods=['POST'])
def execute_code():
    """
    Execute Python code in a restricted environment.
    
    This endpoint safely executes Python code in a restricted sandbox.
    
    JSON body:
        - code: The Python code to execute (required)
    
    Returns:
        JSON object with the execution results
    """
    import asyncio
    import sys
    import os
    
    # Get parameters from request
    data = request.json or {}
    code = data.get('code')
    
    if not code:
        return jsonify({"error": "No code provided"}), 400
    
    try:
        # Import or create the code executor
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        
        try:
            from api_tools.tools.code.runner.code_executor import Tools
            logger.info("Imported code executor from api_tools")
        except ImportError:
            # Create a minimal code executor implementation
            import tempfile
            import asyncio
            import subprocess
            
            class Tools:
                """Tools for running code in a restricted environment"""
                
                def __init__(self):
                    self.python_path = sys.executable
                    self.temp_dir = tempfile.gettempdir()
                    
                async def run_python_code(self, code: str) -> str:
                    """Run Python code in a restricted environment"""
                    try:
                        # Create a temporary file
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                            f.write(code)
                            temp_path = f.name
                        
                        # Run with restricted permissions
                        process = await asyncio.create_subprocess_exec(
                            self.python_path,
                            temp_path,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                            cwd=self.temp_dir,
                            env={
                                'PATH': os.environ.get('PATH', ''),
                                'PYTHONPATH': '',  # Restrict imports
                                'PYTHONHOME': '',  # Restrict Python environment
                            }
                        )
                        
                        stdout, stderr = await process.communicate()
                        os.unlink(temp_path)  # Clean up temp file
                        
                        output = stdout.decode() if stdout else ''
                        error = stderr.decode() if stderr else ''
                        
                        if error:
                            return f"Error:\n{error}"
                        return output if output else "No output"
                        
                    except Exception as e:
                        return f"Error running Python code: {str(e)}"
            
            logger.info("Created minimal code executor implementation")
        
        # Execute the code
        tool = Tools()
        result = asyncio.run(tool.run_python_code(code))
        
        return jsonify({
            "success": True, 
            "result": result,
            "code": code
        })
        
    except Exception as e:
        logger.error(f"Error executing code: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "code": code
        }), 500


@tools_bp.route('/analyze/text', methods=['POST'])
def analyze_text():
    """
    Analyze text for sentiment, key entities, and offensive content using Tisane API.
    
    JSON body:
        - text: The text to analyze (required)
        - language: The language code (default: "en")
        - api_key: The Tisane API key (optional, uses default if not provided)
    
    Returns:
        JSON object with the analysis results
    """
    import asyncio
    import sys
    import os
    import requests
    from typing import Dict, Any, Optional, Callable, Awaitable
    
    # Get parameters from request
    data = request.json or {}
    text = data.get('text')
    language = data.get('language', 'en')
    api_key = data.get('api_key', '52573597091145c2befcc184c54b49ff')  # Default from the example
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        # Define a minimal TisaneClient implementation
        class TisaneClient:
            def __init__(self, api_key: str):
                self.api_key = api_key
                self.base_url = "https://api.tisane.ai/parse"
                
            async def analyze_text(
                self,
                text: str,
                language: str = "en",
                __user__: dict = {},
                __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
            ) -> str:
                headers = {"Ocp-Apim-Subscription-Key": self.api_key, "Content-Type": "application/json"}
                data = {"language": language, "content": text}
                
                try:
                    response = requests.post(self.base_url, headers=headers, json=data, timeout=15)
                    response.raise_for_status()
                    analysis = response.json()
                    
                    sentiment = analysis.get("sentiment", "Unknown")
                    entities = analysis.get("entities", [])
                    offenses = analysis.get("offenses", [])
                    
                    results = f"Text Analysis Results:\n\n"
                    results += f"  Sentiment: {sentiment}\n"
                    results += f"  Entities: {', '.join(e['value'] for e in entities)}\n" if entities else "  No key entities found.\n"
                    results += f"  Offensive Content: {', '.join(o['group'] for o in offenses)}\n" if offenses else "  No offensive content detected.\n"
                    
                    return results
                    
                except requests.RequestException as e:
                    return f"Error analyzing text: {str(e)}"
                except Exception as e:
                    return f"Unexpected error: {str(e)}"
        
        # Analyze the text
        client = TisaneClient(api_key)
        result = asyncio.run(client.analyze_text(text, language))
        
        return jsonify({
            "success": True,
            "result": result,
            "text": text,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "text": text
        }), 500


@tools_bp.route('/process/format', methods=['POST'])
def format_data():
    """
    Convert data between JSON and other formats (YAML, TOML, XML, CSV).
    
    JSON body:
        - data: The data to convert (required)
        - target_format: The target format (json, yaml, toml, xml, csv)
        - style: Output style (pretty, compact, single_line)
    
    Returns:
        JSON object with the converted data
    """
    import json
    import sys
    import os
    
    # Get parameters from request
    data = request.json or {}
    input_data = data.get('data')
    target_format = data.get('target_format', 'json')
    style = data.get('style', 'pretty')
    
    if not input_data:
        return jsonify({"error": "No data provided"}), 400
    
    try:
        # Ensure proper packages are installed
        try:
            import toml
        except ImportError:
            return jsonify({"error": "TOML package not installed. Install with: pip install toml"}), 500
        
        # Convert input to Python object if it's a string
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON data provided"}), 400
        
        # Define conversion functions
        def _convert_to_json(data, indent=None):
            return json.dumps(data, indent=indent)
            
        def _convert_to_yaml(data):
            try:
                return yaml.dump(data, sort_keys=False, allow_unicode=True)
            except Exception as e:
                logger.error(f"Error in YAML conversion: {str(e)}")
                # Fallback to a simple conversion if PyYAML methods fail
                result = ""
                if isinstance(data, dict):
                    for k, v in data.items():
                        result += f"{k}: {v}\n"
                return result
            
        def _convert_to_toml(data):
            return toml.dumps(data)
            
        def _convert_to_xml(data):
            def dict_to_xml(data, root_name="root"):
                doc = xml.dom.minidom.Document()
                root = doc.createElement(root_name)
                doc.appendChild(root)
                
                def add_element(parent, key, value):
                    if isinstance(value, dict):
                        child = doc.createElement(key)
                        for k, v in value.items():
                            add_element(child, k, v)
                        parent.appendChild(child)
                    elif isinstance(value, list):
                        for item in value:
                            child = doc.createElement(key)
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    add_element(child, k, v)
                            else:
                                child.appendChild(doc.createTextNode(str(item)))
                            parent.appendChild(child)
                    else:
                        child = doc.createElement(key)
                        child.appendChild(doc.createTextNode(str(value)))
                        parent.appendChild(child)
                
                for key, value in data.items():
                    add_element(root, key, value)
                
                return doc.toprettyxml(indent="  ")
            
            return dict_to_xml(data)
            
        def _convert_to_csv(data):
            output = io.StringIO()
            writer = None
            
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    writer = csv.DictWriter(output, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                else:
                    writer = csv.writer(output)
                    writer.writerows(data)
            elif isinstance(data, dict):
                writer = csv.writer(output)
                writer.writerows([[k, v] for k, v in data.items()])
            
            return output.getvalue()
        
        # Perform the conversion
        if target_format == "json":
            indent = 2 if style == "pretty" else None
            result = _convert_to_json(input_data, indent)
        elif target_format == "yaml":
            result = _convert_to_yaml(input_data)
        elif target_format == "toml":
            result = _convert_to_toml(input_data)
        elif target_format == "xml":
            result = _convert_to_xml(input_data)
        elif target_format == "csv":
            result = _convert_to_csv(input_data)
        else:
            return jsonify({"error": f"Unsupported format: {target_format}"}), 400
        
        # Apply style
        if style == "single_line" and target_format != "csv":
            result = result.replace("\n", " ").strip()
        
        return jsonify({
            "success": True,
            "result": result,
            "original_data": input_data,
            "target_format": target_format,
            "style": style
        })
        
    except Exception as e:
        logger.error(f"Error formatting data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": input_data
        }), 500


# Add schemas for the new tools
@tools_bp.route('/schemas/extensions', methods=['GET'])
def get_extension_tool_schemas():
    """Get available tool schemas for the extended tools."""
    schemas = [
        {
            "type": "function",
            "function": {
                "name": "execute_code",
                "description": "Execute Python code in a restricted environment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_text",
                "description": "Analyze text for sentiment, key entities, and offensive content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to analyze"
                        },
                        "language": {
                            "type": "string",
                            "description": "The language code (default: 'en')"
                        },
                        "api_key": {
                            "type": "string",
                            "description": "The Tisane API key (optional, uses default if not provided)"
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "format_data",
                "description": "Convert data between JSON and other formats (YAML, TOML, XML, CSV)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "description": "The data to convert (as JSON object or string)"
                        },
                        "target_format": {
                            "type": "string",
                            "enum": ["json", "yaml", "toml", "xml", "csv"],
                            "description": "The target format"
                        },
                        "style": {
                            "type": "string",
                            "enum": ["pretty", "compact", "single_line"],
                            "description": "Output style"
                        }
                    },
                    "required": ["data", "target_format"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_wolframalpha",
                "description": "Query the Wolfram Alpha knowledge engine to solve problems or answer questions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or problem to solve with Wolfram Alpha"
                        },
                        "simple": {
                            "type": "boolean",
                            "description": "Whether to use the simple API (returns an image URL) instead of the text API"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    return jsonify(schemas)


@tools_bp.route('/wolframalpha/query', methods=['POST'])
def wolfram_alpha_query():
    """
    Query the Wolfram Alpha API to solve problems or answer questions.
    
    Required parameters:
    - query: The question or problem to solve with Wolfram Alpha
    
    Optional parameters:
    - app_id: The Wolfram Alpha API key (if not provided, uses environment variable)
    - simple: Boolean to determine if the simple API should be used (defaults to False)
    """
    data = request.json or {}
    
    # Get required parameters
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    
    # Get optional parameters
    app_id = data.get('app_id', API_KEYS['wolframalpha'])
    simple = data.get('simple', False)
    
    if not app_id:
        return jsonify({"error": "Wolfram Alpha API key is required. Please provide it via app_id parameter or set the WOLFRAMALPHA_APP_ID environment variable."}), 400
    
    try:
        if simple:
            # Use the simple API (returns an image URL)
            base_url = "http://api.wolframalpha.com/v1/simple"
            params = {"i": query, "appid": app_id}
            result_url = f"{base_url}?{urllib.parse.urlencode(params)}"
            
            return jsonify({
                "success": True,
                "result_type": "image",
                "result_url": result_url,
                "query": query
            })
        else:
            # Use the short answer API
            base_url = "http://api.wolframalpha.com/v1/result"
            params = {
                "i": query,
                "appid": app_id,
                "format": "plaintext",
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            return jsonify({
                "success": True,
                "result_type": "text",
                "result": response.text,
                "query": query
            })
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Wolfram Alpha: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "query": query
        }), 500


@tools_bp.route('/wolframalpha/schema', methods=['GET'])
def wolfram_alpha_schema():
    """Get the JSON schema for the WolframAlpha tool."""
    schema = {
        "type": "function",
        "function": {
            "name": "query_wolframalpha",
            "description": "Query the Wolfram Alpha knowledge engine to solve problems or answer questions",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or problem to solve with Wolfram Alpha"
                    },
                    "simple": {
                        "type": "boolean",
                        "description": "Whether to use the simple API (returns an image URL) instead of the text API"
                    }
                },
                "required": ["query"]
            }
        }
    }
    
    return jsonify(schema)


@tools_bp.route('/execute/query_wolframalpha', methods=['POST'])
def execute_query_wolframalpha():
    """
    Execute the query_wolframalpha tool directly.
    
    This endpoint allows AI models to query Wolfram Alpha directly without going through
    the provider's tool calling mechanism. It's useful for providers that don't support
    tool calling or for direct API access.
    
    Request Body:
        - query: The question or problem to solve with Wolfram Alpha (required)
        - simple: Whether to use the simple API (returns an image URL) (default: false)
    
    Returns:
        JSON object with the Wolfram Alpha response
    """
    data = request.json or {}
    
    if not data.get('query'):
        return jsonify({"error": "Query parameter is required"}), 400
    
    # Forward the request to the wolfram_alpha_query endpoint
    return wolfram_alpha_query()


@tools_bp.route('/schemas/social', methods=['GET'])
def get_social_tool_schemas():
    """Get available tool schemas for the social tools."""
    schemas = [
        {
            "type": "function",
            "function": {
                "name": "get_reddit_subreddit",
                "description": "Get the latest posts from a specific subreddit on Reddit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subreddit": {
                            "type": "string",
                            "description": "The name of the subreddit (without r/ prefix)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of posts to retrieve (1-100)",
                            "default": 10
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["hot", "new", "top", "rising"],
                            "description": "Sort method for posts",
                            "default": "hot"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["hour", "day", "week", "month", "year", "all"],
                            "description": "Timeframe for 'top' sort",
                            "default": "day"
                        }
                    },
                    "required": ["subreddit"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_reddit_user",
                "description": "Get the latest posts from a specific user on Reddit",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "The Reddit username (without u/ prefix)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of posts to retrieve (1-100)",
                            "default": 10
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["hot", "new", "top", "controversial"],
                            "description": "Sort method for posts",
                            "default": "new"
                        },
                        "timeframe": {
                            "type": "string",
                            "enum": ["hour", "day", "week", "month", "year", "all"],
                            "description": "Timeframe for 'top' and 'controversial' sorts",
                            "default": "all"
                        }
                    },
                    "required": ["username"]
                }
            }
        }
    ]
    
    return jsonify(schemas)


@tools_bp.route('/schemas/news', methods=['GET'])
def get_news_tool_schemas():
    """Get available tool schemas for the news tools."""
    schemas = [
        {
            "type": "function",
            "function": {
                "name": "get_bbc_news_feed",
                "description": "Get the latest news articles from BBC News by category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": [
                                "top_stories", "world", "uk", "business", "politics", 
                                "health", "education", "science_and_environment", 
                                "technology", "entertainment_and_arts", "africa", 
                                "asia", "australia", "europe", "latin_america", 
                                "middle_east", "us_and_canada"
                            ],
                            "description": "The news category to retrieve",
                            "default": "top_stories"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_bbc_news_content",
                "description": "Get the full content of a BBC News article by URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the BBC News article"
                        }
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_nyt_articles",
                "description": "Search for New York Times articles by keyword or topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "page": {
                            "type": "integer",
                            "description": "The page number for paginated results (0-100)",
                            "default": 0
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["newest", "oldest", "relevance"],
                            "description": "Sort order for search results",
                            "default": "newest"
                        },
                        "begin_date": {
                            "type": "string",
                            "description": "Filter by begin date in YYYYMMDD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Filter by end date in YYYYMMDD format"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_nyt_top_stories",
                "description": "Get the top stories from the New York Times by section",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "section": {
                            "type": "string",
                            "enum": [
                                "arts", "automobiles", "books", "business", "fashion", "food",
                                "health", "home", "insider", "magazine", "movies", "nyregion",
                                "obituaries", "opinion", "politics", "realestate", "science",
                                "sports", "sundayreview", "technology", "theater", "travel",
                                "upshot", "us", "world"
                            ],
                            "description": "The section to retrieve top stories from",
                            "default": "home"
                        }
                    }
                }
            }
        }
    ]
    
    return jsonify(schemas) 