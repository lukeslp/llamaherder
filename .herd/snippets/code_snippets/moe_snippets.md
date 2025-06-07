# Code Snippets from toollama/moe/moe.py

File: `toollama/moe/moe.py`  
Language: Python  
Extracted: 2025-06-07 05:10:30  

## Snippet 1
Lines 1-28

```Python
#!/usr/bin/env python3
"""
MoE System Management Script
This script provides a command-line interface to manage the MoE system:
- Build models
- Start/stop servers
- Check system status
- Run tests
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('moe-manager')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
```

## Snippet 2
Lines 29-44

```Python
def run_command(cmd, shell=True):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return None
```

## Snippet 3
Lines 45-50

```Python
def build_models():
    """Build all MoE models using Ollama."""
    logger.info("Building MoE models...")
    script_path = PROJECT_ROOT / "scripts" / "build_models.sh"
    return run_command(f"bash {script_path}")
```

## Snippet 4
Lines 51-56

```Python
def start_servers():
    """Start all MoE servers."""
    logger.info("Starting MoE servers...")
    script_path = PROJECT_ROOT / "servers" / "start_servers.py"
    return run_command(f"python {script_path}")
```

## Snippet 5
Lines 57-62

```Python
def stop_servers():
    """Stop all running MoE servers."""
    logger.info("Stopping MoE servers...")
    script_path = PROJECT_ROOT / "servers" / "stop_servers.py"
    return run_command(f"python {script_path}")
```

## Snippet 6
Lines 63-74

```Python
def check_status():
    """Check the status of all MoE components."""
    logger.info("Checking MoE system status...")

    # Check Ollama models
    logger.info("\nChecking available models:")
    run_command("ollama list")

    # Check running servers
    logger.info("\nChecking running servers:")
    ps_cmd = "ps aux | grep 'python.*server.py' | grep -v grep"
    servers = run_command(ps_cmd)
```

## Snippet 7
Lines 75-79

```Python
if servers:
        print(servers)
    else:
        logger.info("No MoE servers currently running.")
```

## Snippet 8
Lines 80-84

```Python
def run_tests():
    """Run all MoE system tests."""
    logger.info("Running MoE system tests...")
    return run_command("pytest tests/")
```

## Snippet 9
Lines 86-93

```Python
"""Main entry point for the MoE management script."""
    parser = argparse.ArgumentParser(description="MoE System Management")
    parser.add_argument('command', choices=['build', 'start', 'stop', 'status', 'test'],
                      help='Command to execute')

    args = parser.parse_args()

    try:
```

## Snippet 10
Lines 104-110

```Python
except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)
```

