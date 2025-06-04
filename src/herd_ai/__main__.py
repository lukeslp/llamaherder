#!/usr/bin/env python3
"""
Entry point for running Herd AI as a module with: python -m herd_ai
"""

import sys
import os
from pathlib import Path
import warnings

def run_as_module():
    """Run Herd AI as a module"""
    # Get the command name for detection (herd vs llamacleaner)
    command = Path(sys.argv[0]).stem if len(sys.argv) > 0 else ""
    
    # Check for legacy mode
    is_legacy_mode = command == "llamacleaner"
    
    if is_legacy_mode:
        warnings.warn(
            "The 'llamacleaner' command is deprecated and will be removed in a future version. "
            "Please use 'herd' instead.", 
            DeprecationWarning, 
            stacklevel=2
        )
    
    # Import and run the CLI
    from herd_ai.cli import main
    main()

if __name__ == "__main__":
    run_as_module() 