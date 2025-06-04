# Code Snippets from /Volumes/Galactus/_DEV/herd/__main__.py

File: `/Volumes/Galactus/_DEV/herd/__main__.py`  
Language: Python  
Extracted: 2025-05-01 13:07:20  

## Snippet 1
Lines 3-9

```Python
Entry point for running LlamaCleaner as a module with: python -m llamacleaner
"""

import sys
import os
from pathlib import Path
```

## Snippet 2
Lines 10-21

```Python
def run_as_module():
    """Run LlamaCleaner as a module"""
    # Get the package directory
    package_dir = Path(__file__).parent

    # Make sure the package is importable as a module
    sys.path.insert(0, str(package_dir.parent))

    # Import and run the CLI
    from llamacleaner.cli import main
    main()
```

