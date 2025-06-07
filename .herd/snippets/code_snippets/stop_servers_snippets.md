# Code Snippets from toollama/moe/servers/stop_servers.py

File: `toollama/moe/servers/stop_servers.py`  
Language: Python  
Extracted: 2025-06-07 05:11:53  

## Snippet 1
Lines 1-20

```Python
#!/usr/bin/env python3
"""
Script to stop all running MoE agent servers gracefully.
This script finds and terminates all running server processes.
"""

import os
import signal
import subprocess
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('stop_servers')
```

## Snippet 2
Lines 21-28

```Python
def find_server_processes():
    """Find all running MoE server processes."""
    try:
        # Use ps to find Python processes running our server scripts
        cmd = "ps aux | grep 'python.*server.py' | grep -v grep"
        output = subprocess.check_output(cmd, shell=True).decode()

        processes = []
```

## Snippet 3
Lines 40-43

```Python
def stop_servers():
    """Stop all running server processes gracefully."""
    processes = find_server_processes()
```

## Snippet 4
Lines 44-47

```Python
if not processes:
        logger.info("No running MoE servers found.")
        return
```

## Snippet 5
Lines 50-54

```Python
for pid, cmd in processes:
        try:
            logger.info(f"Stopping server (PID {pid}): {cmd}")
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
```

## Snippet 6
Lines 59-62

```Python
# Give processes time to shut down gracefully
    import time
    time.sleep(2)
```

## Snippet 7
Lines 65-73

```Python
for pid, cmd in remaining:
        try:
            logger.warning(f"Force killing server (PID {pid}): {cmd}")
            os.kill(pid, signal.SIGKILL)
        except Exception as e:
            logger.error(f"Error force killing process {pid}: {e}")

    logger.info("All servers stopped.")
```

