"""
Script to stop all MoE model servers.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def stop_servers():
    """Stop all running server processes"""
    pid_file = Path(__file__).parent.parent / "moe_servers.pid"
    if not pid_file.exists():
        logger.error("No running servers found")
        return
        
    with open(pid_file) as f:
        for line in f:
            try:
                name, pid = line.strip().split(":")
                pid = int(pid)
                os.kill(pid, 15)  # SIGTERM
                logger.info(f"Stopped {name} server (PID: {pid})")
            except ProcessLookupError:
                pass  # Process already gone
            except ValueError:
                pass  # Malformed line
                
    pid_file.unlink()
    logger.info("All servers stopped")

if __name__ == "__main__":
    stop_servers() 