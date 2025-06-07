#!/usr/bin/env python3
"""
Script to start all MoE agent servers concurrently.

This script launches:
  - Caminaå (Coordinator) Server
  - Belters (File Manipulation) Server
  - Drummers (Information Gathering) Server
  - DeepSeek (Background Reasoning) Server

The servers are started as background processes. Press Ctrl+C to stop all servers.
"""

import subprocess
import os
import signal
import sys
import time
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('start_servers')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

def load_server_config():
    """Load server configuration from YAML file."""
    config_path = PROJECT_ROOT / 'config' / 'server_configs' / 'servers.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading server config: {e}")
        sys.exit(1)

# List of tuples: (Server name, script path, default port)
SERVERS = [
    ("Caminaå", "caminaa_server.py", 6000),
    ("Belters", "belters_server.py", 6001),
    ("Drummers", "drummers_server.py", 6002),
    ("DeepSeek", "deepseek_server.py", 6003)
]

processes = []

def start_servers():
    """Start all agent servers as background processes."""
    logger.info("Starting all agent servers...")
    
    # Load server configuration
    config = load_server_config()
    
    # Change to the project root directory
    os.chdir(PROJECT_ROOT)
    
    # Start each server
    for name, script, default_port in SERVERS:
        # Get port from config or use default
        port = config.get(name.lower(), {}).get('port', default_port)
        cmd = f"python servers/{script}"
        
        logger.info(f"Starting {name} Server on port {port}: {cmd}")
        try:
            # Using preexec_fn=os.setsid to ensure a new process group is created
            proc = subprocess.Popen(
                cmd,
                shell=True,
                preexec_fn=os.setsid,
                env={**os.environ, 'PORT': str(port)}
            )
            processes.append((name, proc))
            logger.info(f"{name} Server started with PID {proc.pid}")
        except Exception as e:
            logger.error(f"Error starting {name} Server: {e}")
            stop_servers()
            sys.exit(1)
    
    logger.info("All servers started. Press Ctrl+C to stop them.")
    
    try:
        while True:
            # Check if any process has terminated unexpectedly
            for name, proc in processes[:]:
                if proc.poll() is not None:
                    logger.error(f"{name} Server (PID {proc.pid}) terminated unexpectedly!")
                    stop_servers()
                    sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\nReceived shutdown signal...")
        stop_servers()

def stop_servers():
    """Stop all running servers gracefully."""
    logger.info("Stopping all servers...")
    for name, proc in processes:
        try:
            logger.info(f"Stopping {name} Server (PID {proc.pid})")
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception as e:
            logger.error(f"Error stopping {name} Server: {e}")
    
    # Wait for processes to terminate
    for name, proc in processes:
        try:
            proc.wait(timeout=5)
            logger.info(f"{name} Server stopped")
        except subprocess.TimeoutExpired:
            logger.warning(f"{name} Server (PID {proc.pid}) did not stop gracefully, forcing...")
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    
    logger.info("All servers stopped.")

if __name__ == "__main__":
    start_servers() 