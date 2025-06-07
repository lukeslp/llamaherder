# Code Snippets from toollama/moe/servers/start_servers.py

File: `toollama/moe/servers/start_servers.py`  
Language: Python  
Extracted: 2025-06-07 05:11:52  

## Snippet 1
Lines 1-33

```Python
#!/usr/bin/env python3
"""
Script to start all MoE agent servers concurrently.

This script launches:
  - Caminaå (Coordinator) Server
  - Belters (File Manipulation) Server
  - Drummers (Information Gathering) Server
  - DeepSeek (Background Reasoning) Server

The servers are started as background processes. Press Ctrl+C to stop all servers.
"""

import subprocess
import os
import signal
import sys
import time
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('start_servers')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
```

## Snippet 2
Lines 34-53

```Python
def load_server_config():
    """Load server configuration from YAML file."""
    config_path = PROJECT_ROOT / 'config' / 'server_configs' / 'servers.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading server config: {e}")
        sys.exit(1)

# List of tuples: (Server name, script path, default port)
SERVERS = [
    ("Caminaå", "caminaa_server.py", 6000),
    ("Belters", "belters_server.py", 6001),
    ("Drummers", "drummers_server.py", 6002),
    ("DeepSeek", "deepseek_server.py", 6003)
]

processes = []
```

## Snippet 3
Lines 54-64

```Python
def start_servers():
    """Start all agent servers as background processes."""
    logger.info("Starting all agent servers...")

    # Load server configuration
    config = load_server_config()

    # Change to the project root directory
    os.chdir(PROJECT_ROOT)

    # Start each server
```

## Snippet 4
Lines 65-69

```Python
for name, script, default_port in SERVERS:
        # Get port from config or use default
        port = config.get(name.lower(), {}).get('port', default_port)
        cmd = f"python servers/{script}"
```

## Snippet 5
Lines 70-79

```Python
logger.info(f"Starting {name} Server on port {port}: {cmd}")
        try:
            # Using preexec_fn=os.setsid to ensure a new process group is created
            proc = subprocess.Popen(
                cmd,
                shell=True,
                preexec_fn=os.setsid,
                env={**os.environ, 'PORT': str(port)}
            )
            processes.append((name, proc))
```

## Snippet 6
Lines 97-100

```Python
except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal...")
        stop_servers()
```

## Snippet 7
Lines 101-103

```Python
def stop_servers():
    """Stop all running servers gracefully."""
    logger.info("Stopping all servers...")
```

## Snippet 8
Lines 112-114

```Python
for name, proc in processes:
        try:
            proc.wait(timeout=5)
```

