#!/usr/bin/env python3
"""
Entry point for running LlamaCleaner as a module with: python -m llamacleaner
"""

import sys
import os
from pathlib import Path

def run_as_module():
    """Run LlamaCleaner as a module"""
    # Get the package directory
    package_dir = Path(__file__).parent
    
    # Make sure the package is importable as a module
    sys.path.insert(0, str(package_dir.parent))
    
    # Import and run the CLI
    from llamacleaner.cli import main
    main()

if __name__ == "__main__":
    run_as_module() 