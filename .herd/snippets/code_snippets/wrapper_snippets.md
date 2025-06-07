# Code Snippets from src/herd_ai/wrapper.py

File: `src/herd_ai/wrapper.py`  
Language: Python  
Extracted: 2025-06-07 05:09:40  

## Snippet 1
Lines 3-9

```Python
Backward compatibility wrapper script for the old llamacleaner.py.
This script imports and calls the modularized version.
"""

import sys
from pathlib import Path
```

## Snippet 2
Lines 12-17

```Python
# Import the main function from the modularized version
    from llamacleaner.cli import main as modular_main

    # Run the modularized version
    modular_main()
```

