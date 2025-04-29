"""
Logging utilities
"""
import logging
import os
import sys
from datetime import datetime

# Global logger instance
_logger = None

def setup_logger():
    """Set up and configure the application logger"""
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Create logger
    logger = logging.getLogger("python_dlt_viewer")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Try to create file handler in user's home directory
    try:
        log_dir = os.path.expanduser("~/.python_dlt_viewer")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"dlt_viewer_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")
    
    _logger = logger
    return logger

def get_logger():
    """Get the application logger"""
    global _logger
    
    if _logger is None:
        return setup_logger()
    
    return _logger