#!/usr/bin/env python3
"""
Backward compatibility wrapper script for the old llamacleaner.py.
This script imports and calls the modularized version.
"""

import sys
from pathlib import Path

def main():
    """Entry point for the wrapper script."""
    # Import the main function from the modularized version
    from llamacleaner.cli import main as modular_main
    
    # Run the modularized version
    modular_main()

if __name__ == "__main__":
    main() 