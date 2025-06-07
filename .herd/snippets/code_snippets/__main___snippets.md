# Code Snippets from src/herd_ai/__main__.py

File: `src/herd_ai/__main__.py`  
Language: Python  
Extracted: 2025-06-07 05:09:32  

## Snippet 1
Lines 3-10

```Python
Entry point for running Herd AI as a module with: python -m herd_ai
"""

import sys
import os
from pathlib import Path
import warnings
```

## Snippet 2
Lines 19-30

```Python
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
```

