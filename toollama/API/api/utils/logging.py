#!/usr/bin/env python
import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
import traceback


class JSONFormatter(logging.Formatter):
    """Format logs as JSON to facilitate log processing."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra attributes
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in log_entry:
                continue
            
            # Skip some standard attributes that aren't useful
            if key in ("args", "levelno", "msg", "pathname", "filename", "exc_text", 
                       "stack_info", "created", "msecs", "relativeCreated", "exc_info",
                       "thread", "threadName", "processName", "process"):
                continue
            
            log_entry[key] = value
        
        return json.dumps(log_entry)


def setup_logging(
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file: str = "api.log",
    json_format: bool = False
) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level
        log_to_file: Whether to log to a file
        log_file: Path to the log file
        json_format: Whether to format logs as JSON
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    handlers.append(console_handler)
    
    # File handler (optional)
    if log_to_file:
        try:
            # Create directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Error setting up file logging: {e}")
    
    # Create formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Add formatters to handlers and add handlers to root logger
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    # Set log levels for external libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    # Log setup complete
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized with level {logging.getLevelName(level)}")
    if log_to_file:
        logger.info(f"Logging to file: {log_file}")


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        level: Optional level override
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger 