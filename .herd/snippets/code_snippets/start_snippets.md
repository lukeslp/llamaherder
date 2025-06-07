# Code Snippets from toollama/moe/servers/start.py

File: `toollama/moe/servers/start.py`  
Language: Python  
Extracted: 2025-06-07 05:12:13  

## Snippet 1
Lines 1-50

```Python
"""
Script to start all MoE model servers.
"""

import os
import sys
import logging
import asyncio
import argparse
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Server configurations
SERVERS = [
    {
        "name": "Camina",
        "module": "camina",
        "port": 6000,
        "model": "camina-moe"
    },
    {
        "name": "Belter",
        "module": "belter",
        "port": 6001,
        "model": "belter-base"
    },
    {
        "name": "Drummer",
        "module": "drummer",
        "port": 6002,
        "model": "drummer-base"
    },
    {
        "name": "Observer",
        "module": "observer",
        "port": 6003,
        "model": "deepseek-observer"
    }
]
```

## Snippet 2
Lines 51-73

```Python
def start_server(server: dict, debug: bool = False, background: bool = False) -> subprocess.Popen:
    """
    Start a model server.

    Args:
        server: Server configuration
        debug: Enable debug logging
        background: Run in background mode

    Returns:
        Server process
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)

    cmd = [
        sys.executable,
        "-m",
        f"moe.servers.{server['module']}",
        "--port",
        str(server["port"])
    ]
```

## Snippet 3
Lines 79-101

```Python
if background:
        # Redirect output to log files in a logs directory
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        stdout_file = open(log_dir / f"{server['name'].lower()}_out.log", "a")
        stderr_file = open(log_dir / f"{server['name'].lower()}_err.log", "a")

        return subprocess.Popen(
            cmd,
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True  # Detach from parent process
        )
    else:
        return subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
```

## Snippet 4
Lines 130-132

```Python
def cleanup_servers():
    """Clean up any running server processes"""
    pid_file = Path(__file__).parent.parent / "moe_servers.pid"
```

## Snippet 5
Lines 135-139

```Python
for line in f:
                try:
                    name, pid = line.strip().split(":")
                    pid = int(pid)
                    os.kill(pid, 15)  # SIGTERM
```

## Snippet 6
Lines 141-144

```Python
except ProcessLookupError:
                    pass  # Process already gone
                except ValueError:
                    pass  # Malformed line
```

## Snippet 7
Lines 147-154

```Python
async def main_async(debug: bool = False, background: bool = False):
    """Async main function"""
    try:
        # Clean up any existing servers
        cleanup_servers()

        # Start each server
        processes = []
```

## Snippet 8
Lines 155-160

```Python
for server in SERVERS:
            process = start_server(server, debug, background)
            processes.append((server, process))

        logger.info("All servers started")
```

## Snippet 9
Lines 161-169

```Python
if background:
            # Write PID file and exit
            write_pid_file(processes)
            logger.info("Servers running in background. Use 'moe.servers.stop' to stop them.")
            return

        # Monitor server processes
        await monitor_servers(processes, debug)
```

## Snippet 10
Lines 172-175

```Python
for _, process in processes:
            process.terminate()
        sys.exit(0)
```

## Snippet 11
Lines 176-179

```Python
except Exception as e:
        logger.error(f"Error starting servers: {e}")
        sys.exit(1)
```

## Snippet 12
Lines 180-186

```Python
def main():
    """Start all model servers"""
    parser = argparse.ArgumentParser(description="Start MoE model servers")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--background", action="store_true", help="Run servers in background")
    args = parser.parse_args()
```

## Snippet 13
Lines 187-192

```Python
if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    asyncio.run(main_async(args.debug, args.background))
```

