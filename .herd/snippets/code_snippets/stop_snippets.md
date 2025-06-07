# Code Snippets from toollama/moe/servers/stop.py

File: `toollama/moe/servers/stop.py`  
Language: Python  
Extracted: 2025-06-07 05:12:05  

## Snippet 1
Lines 1-19

```Python
"""
Script to stop all MoE model servers.
"""

import os
import sys
import logging
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
```

## Snippet 2
Lines 20-22

```Python
def stop_servers():
    """Stop all running server processes"""
    pid_file = Path(__file__).parent.parent / "moe_servers.pid"
```

## Snippet 3
Lines 23-27

```Python
if not pid_file.exists():
        logger.error("No running servers found")
        return

    with open(pid_file) as f:
```

## Snippet 4
Lines 28-32

```Python
for line in f:
            try:
                name, pid = line.strip().split(":")
                pid = int(pid)
                os.kill(pid, 15)  # SIGTERM
```

## Snippet 5
Lines 34-38

```Python
except ProcessLookupError:
                pass  # Process already gone
            except ValueError:
                pass  # Malformed line
```

