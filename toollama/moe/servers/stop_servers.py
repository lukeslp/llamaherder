#!/usr/bin/env python3
"""
Script to stop all running MoE agent servers gracefully.
This script finds and terminates all running server processes.
"""

import os
import signal
import subprocess
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('stop_servers')

def find_server_processes():
    """Find all running MoE server processes."""
    try:
        # Use ps to find Python processes running our server scripts
        cmd = "ps aux | grep 'python.*server.py' | grep -v grep"
        output = subprocess.check_output(cmd, shell=True).decode()
        
        processes = []
        for line in output.splitlines():
            parts = line.split()
            pid = int(parts[1])
            cmd = ' '.join(parts[10:])  # Full command
            if any(x in cmd for x in ['caminaa_server.py', 'belters_server.py', 
                                    'drummers_server.py', 'deepseek_server.py']):
                processes.append((pid, cmd))
        return processes
    except subprocess.CalledProcessError:
        return []  # No processes found

def stop_servers():
    """Stop all running server processes gracefully."""
    processes = find_server_processes()
    
    if not processes:
        logger.info("No running MoE servers found.")
        return
    
    logger.info(f"Found {len(processes)} running server(s).")
    
    for pid, cmd in processes:
        try:
            logger.info(f"Stopping server (PID {pid}): {cmd}")
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            logger.warning(f"Process {pid} not found (already terminated?)")
        except Exception as e:
            logger.error(f"Error stopping process {pid}: {e}")
    
    # Give processes time to shut down gracefully
    import time
    time.sleep(2)
    
    # Check for any remaining processes and force kill if necessary
    remaining = find_server_processes()
    for pid, cmd in remaining:
        try:
            logger.warning(f"Force killing server (PID {pid}): {cmd}")
            os.kill(pid, signal.SIGKILL)
        except Exception as e:
            logger.error(f"Error force killing process {pid}: {e}")
    
    logger.info("All servers stopped.")

if __name__ == "__main__":
    stop_servers() 