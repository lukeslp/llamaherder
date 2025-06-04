# Code Snippets from /Volumes/Galactus/_DEV/herd/run_herd.py

File: `/Volumes/Galactus/_DEV/herd/run_herd.py`  
Language: Python  
Extracted: 2025-05-01 13:07:16  

## Snippet 1
Lines 3-12

```Python
Simplified runner script for Herd AI.
This is a temporary script that loads modules directly without package structure,
to allow running the application during development/transition.
"""

import sys
import os
from pathlib import Path
import traceback
```

## Snippet 2
Lines 14-24

```Python
"""Entry point for Herd AI development mode."""
    # Ensure the current directory is in the path
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))

    # Add script directory to Python path
    os.environ['PYTHONPATH'] = str(current_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')

    # Let the user know what we're doing
    print(f"Starting Herd AI in development mode from {current_dir}")
    print("Python path includes:")
```

## Snippet 3
Lines 25-68

```Python
for p in sys.path:
        print(f"  - {p}")

    # Import the CLI modules directly
    try:
        # First try the minimal CLI
        print("Attempting to import minimal_cli...")
        import minimal_cli

        # Run the minimal CLI
        print("Starting Herd AI (development mode)...")
        minimal_cli.main()

    except ImportError as e:
        print(f"Could not import minimal_cli: {e}")
        print("Trying alternative imports...")

        try:
            # Try to import the main CLI modules
            from cli import main as cli_main
            print("Successfully imported regular CLI")
            cli_main()
        except ImportError as e:
            print(f"Could not import cli: {e}")
            print("Trying to import through herd.py...")

            try:
                # Try to use the herd.py entry point
                import herd
                herd.main()
            except ImportError as e:
                print(f"Error importing through herd.py: {e}")
                print("All import attempts failed.")
                print("\nPlease make sure:")
                print("1. You are running from the project root directory")
                print("2. All required dependencies are installed")
                print("3. The project structure is intact")
                sys.exit(1)
    except Exception as e:
        print(f"Error running Herd AI: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        sys.exit(1)
```

