#!/usr/bin/env python3
###############################################################################
# Herd AI - Development Runner Script
# -----------------------------------------------------------------------------
# This script serves as a convenience entry point for running Herd AI in
# development mode. It attempts to load the CLI or main application modules
# directly from the local project structure, allowing for rapid iteration
# without requiring full package installation.
#
# Usage:
#   python run_herd.py
#
# Arguments:
#   None (invoked as a script)
#
# Argument Format:
#   No command-line arguments are required or processed by this script.
#
# Credentials:
#   No credentials are required to run this script. All authentication is
#   handled by downstream modules if needed.
###############################################################################

import sys
import os
from pathlib import Path
import traceback
import warnings

# Try to import dotenv for .env loading
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment variables from {env_path.absolute()}")
except ImportError:
    warnings.warn(
        "python-dotenv package not found. Environment variables from .env won't be loaded. "
        "Install with 'pip install python-dotenv' for .env file support.",
        ImportWarning,
        stacklevel=2
    )

###############################################################################
# main
# -----------------------------------------------------------------------------
# Entry point for Herd AI development mode. Modifies sys.path and PYTHONPATH
# to ensure local modules are importable, then attempts to import and run
# the CLI or main application modules in the following order:
#   1. minimal_cli
#   2. cli (as main)
#   3. herd (as main)
#
# If all import attempts fail, prints diagnostic information and exits.
#
# Arguments:
#   None
#
# Returns:
#   None
###############################################################################
def main():
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    # Add src directory to path for imports
    src_dir = current_dir / "src"
    sys.path.insert(0, str(src_dir))
    os.environ['PYTHONPATH'] = str(current_dir) + os.pathsep + str(src_dir) + os.pathsep + os.environ.get('PYTHONPATH', '')

    print(f"Starting Herd AI in development mode from {current_dir}")
    print("Python path includes:")
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
                print("\nOr if that fails, try:")
                print("pip install --no-deps -e .")
                sys.exit(1)
    except Exception as e:
        print(f"Error running Herd AI: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()
        sys.exit(1)

###############################################################################
# Script Entry Point
# -----------------------------------------------------------------------------
# Invokes the main() function when the script is run directly.
###############################################################################
if __name__ == "__main__":
    main()