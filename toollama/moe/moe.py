#!/usr/bin/env python3
"""
MoE System Management Script
This script provides a command-line interface to manage the MoE system:
- Build models
- Start/stop servers
- Check system status
- Run tests
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('moe-manager')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()

def run_command(cmd, shell=True):
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.stderr}")
        return None

def build_models():
    """Build all MoE models using Ollama."""
    logger.info("Building MoE models...")
    script_path = PROJECT_ROOT / "scripts" / "build_models.sh"
    return run_command(f"bash {script_path}")

def start_servers():
    """Start all MoE servers."""
    logger.info("Starting MoE servers...")
    script_path = PROJECT_ROOT / "servers" / "start_servers.py"
    return run_command(f"python {script_path}")

def stop_servers():
    """Stop all running MoE servers."""
    logger.info("Stopping MoE servers...")
    script_path = PROJECT_ROOT / "servers" / "stop_servers.py"
    return run_command(f"python {script_path}")

def check_status():
    """Check the status of all MoE components."""
    logger.info("Checking MoE system status...")
    
    # Check Ollama models
    logger.info("\nChecking available models:")
    run_command("ollama list")
    
    # Check running servers
    logger.info("\nChecking running servers:")
    ps_cmd = "ps aux | grep 'python.*server.py' | grep -v grep"
    servers = run_command(ps_cmd)
    if servers:
        print(servers)
    else:
        logger.info("No MoE servers currently running.")

def run_tests():
    """Run all MoE system tests."""
    logger.info("Running MoE system tests...")
    return run_command("pytest tests/")

def main():
    """Main entry point for the MoE management script."""
    parser = argparse.ArgumentParser(description="MoE System Management")
    parser.add_argument('command', choices=['build', 'start', 'stop', 'status', 'test'],
                      help='Command to execute')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'build':
            build_models()
        elif args.command == 'start':
            start_servers()
        elif args.command == 'stop':
            stop_servers()
        elif args.command == 'status':
            check_status()
        elif args.command == 'test':
            run_tests()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 