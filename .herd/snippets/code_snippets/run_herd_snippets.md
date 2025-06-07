# Code Snippets from run_herd.py

File: `run_herd.py`  
Language: Python  
Extracted: 2025-06-07 05:08:04  

## Snippet 1
Lines 21-29

```Python
#   handled by downstream modules if needed.
###############################################################################

import sys
import os
from pathlib import Path
import traceback
import warnings
```

## Snippet 2
Lines 30-34

```Python
# Try to import dotenv for .env loading
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path('.env')
```

## Snippet 3
Lines 38-40

```Python
except ImportError:
    warnings.warn(
        "python-dotenv package not found. Environment variables from .env won't be loaded. "
```

## Snippet 4
Lines 64-66

```Python
def main():
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
```

## Snippet 5
Lines 67-73

```Python
# Add src directory to path for imports
    src_dir = current_dir / "src"
    sys.path.insert(0, str(src_dir))
    os.environ['PYTHONPATH'] = str(current_dir) + os.pathsep + str(src_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')

    print(f"Starting Herd AI in development mode from {current_dir}")
    print("Python path includes:")
```

## Snippet 6
Lines 74-124

```Python
for p in sys.path:
        print(f"  - {p}")

    # Try to resolve pydantic version conflict issues
    try:
        # This ensures we're using a compatible version
        import pydantic
        print(f"Using pydantic version: {pydantic.__version__}")
    except ImportError:
        print("Pydantic not found in environment")
    except Exception as e:
        print(f"Error with pydantic import: {e}")

    try:
        print("Attempting to import minimal_cli...")
        import minimal_cli
        print("Starting Herd AI (development mode)...")
        minimal_cli.main()
    except ImportError as e:
        print(f"Could not import minimal_cli: {e}")
        print("Trying alternative imports...")

        try:
            try:
                from cli import main as cli_main
                print("Successfully imported regular CLI")
                cli_main()
            except ImportError:
                from herd_ai.cli import main as cli_main
                print("Successfully imported herd_ai.cli")
                cli_main()
        except ImportError as e:
            print(f"Could not import cli: {e}")
            print("Trying to import through herd.py...")

            try:
                try:
                    import herd
                    herd.main()
                except ImportError:
                    from herd_ai import herd
                    herd.main()
            except ImportError as e:
                print(f"Error importing through herd.py: {e}")
                print("All import attempts failed.")
                print("\nPlease make sure:")
                print("1. You are running from the project root directory")
                print("2. All required dependencies are installed")
                print("3. The project structure is intact")
                print("\nTrying pip install command to fix dependencies:")
                print("pip install -e .")
```

## Snippet 7
Lines 128-133

```Python
except Exception as e:
        print(f"Error running Herd AI: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        sys.exit(1)
```

