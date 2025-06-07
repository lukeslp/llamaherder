# Code Snippets from toollama/moe/archive/old_tools/web/__main__.py

File: `toollama/moe/archive/old_tools/web/__main__.py`  
Language: Python  
Extracted: 2025-06-07 05:12:20  

## Snippet 1
Lines 1-11

```Python
"""
MoE System Web Interface
Run this module to start the web interface.
"""

import argparse
import logging
from pathlib import Path

from .server import start_server
```

## Snippet 2
Lines 12-23

```Python
def main():
    """Start the MoE System web interface."""
    # Configure argument parser
    parser = argparse.ArgumentParser(description="Start the MoE System web interface")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    # Parse arguments
    args = parser.parse_args()

    # Configure logging
```

## Snippet 3
Lines 24-38

```Python
log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Ensure static directory exists
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    # Start server
    logging.info(f"Starting MoE System web interface on {args.host}:{args.port}")
    start_server(host=args.host, port=args.port)
```

