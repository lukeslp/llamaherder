# Code Snippets from /Volumes/Galactus/_DEV/herd/run_herd.py

File: `/Volumes/Galactus/_DEV/herd/run_herd.py`  
Language: Python  
Extracted: 2025-05-01 17:28:15  

## Snippet 1
Lines 21-30

```Python
#   handled by downstream modules if needed.
###############################################################################

import sys
import os
from pathlib import Path
import traceback

###############################################################################
# main
```

## Snippet 2
Lines 47-53

```Python
def main():
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    os.environ['PYTHONPATH'] = str(current_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')

    print(f"Starting Herd AI in development mode from {current_dir}")
    print("Python path includes:")
```

## Snippet 3
Lines 54-90

```Python
for p in sys.path:
        print(f"  - {p}")

    try:
        print("Attempting to import minimal_cli...")
        import minimal_cli
        print("Starting Herd AI (development mode)...")
        minimal_cli.main()
    except ImportError as e:
        print(f"Could not import minimal_cli: {e}")
        print("Trying alternative imports...")

        try:
            from cli import main as cli_main
            print("Successfully imported regular CLI")
            cli_main()
        except ImportError as e:
            print(f"Could not import cli: {e}")
            print("Trying to import through herd.py...")

            try:
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

