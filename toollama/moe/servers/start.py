"""
Script to start all MoE model servers.
"""

import os
import sys
import logging
import asyncio
import argparse
import subprocess
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

# Server configurations
SERVERS = [
    {
        "name": "Camina",
        "module": "camina",
        "port": 6000,
        "model": "camina-moe"
    },
    {
        "name": "Belter",
        "module": "belter",
        "port": 6001,
        "model": "belter-base"
    },
    {
        "name": "Drummer",
        "module": "drummer",
        "port": 6002,
        "model": "drummer-base"
    },
    {
        "name": "Observer",
        "module": "observer",
        "port": 6003,
        "model": "deepseek-observer"
    }
]

def start_server(server: dict, debug: bool = False, background: bool = False) -> subprocess.Popen:
    """
    Start a model server.
    
    Args:
        server: Server configuration
        debug: Enable debug logging
        background: Run in background mode
        
    Returns:
        Server process
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)
    
    cmd = [
        sys.executable,
        "-m",
        f"moe.servers.{server['module']}",
        "--port",
        str(server["port"])
    ]
    
    if debug:
        cmd.append("--debug")
        
    logger.info(f"Starting {server['name']} server on port {server['port']}")
    
    if background:
        # Redirect output to log files in a logs directory
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        stdout_file = open(log_dir / f"{server['name'].lower()}_out.log", "a")
        stderr_file = open(log_dir / f"{server['name'].lower()}_err.log", "a")
        
        return subprocess.Popen(
            cmd,
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True  # Detach from parent process
        )
    else:
        return subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

async def monitor_servers(processes: list, debug: bool = False):
    """Monitor server processes and restart them if they crash"""
    while True:
        for i, (server, process) in enumerate(processes):
            if process.poll() is not None:
                # Server crashed
                logger.error(
                    f"{server['name']} server crashed with code {process.returncode}"
                )
                if not isinstance(process.stdout, (subprocess.PIPE, int)):
                    process.stdout.close()
                if not isinstance(process.stderr, (subprocess.PIPE, int)):
                    process.stderr.close()
                
                # Restart server
                logger.info(f"Restarting {server['name']} server...")
                new_process = start_server(server, debug)
                processes[i] = (server, new_process)
                
        await asyncio.sleep(1)

def write_pid_file(processes: list):
    """Write server PIDs to file for later cleanup"""
    pid_file = Path(__file__).parent.parent / "moe_servers.pid"
    with open(pid_file, "w") as f:
        for server, process in processes:
            f.write(f"{server['name']}:{process.pid}\n")

def cleanup_servers():
    """Clean up any running server processes"""
    pid_file = Path(__file__).parent.parent / "moe_servers.pid"
    if pid_file.exists():
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

async def main_async(debug: bool = False, background: bool = False):
    """Async main function"""
    try:
        # Clean up any existing servers
        cleanup_servers()
        
        # Start each server
        processes = []
        for server in SERVERS:
            process = start_server(server, debug, background)
            processes.append((server, process))
            
        logger.info("All servers started")
        
        if background:
            # Write PID file and exit
            write_pid_file(processes)
            logger.info("Servers running in background. Use 'moe.servers.stop' to stop them.")
            return
            
        # Monitor server processes
        await monitor_servers(processes, debug)
            
    except KeyboardInterrupt:
        logger.info("Shutting down servers...")
        for _, process in processes:
            process.terminate()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Error starting servers: {e}")
        sys.exit(1)

def main():
    """Start all model servers"""
    parser = argparse.ArgumentParser(description="Start MoE model servers")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--background", action="store_true", help="Run servers in background")
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    asyncio.run(main_async(args.debug, args.background))

if __name__ == "__main__":
    main() 