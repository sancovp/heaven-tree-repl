"""
Simple TreeShell Logger

Uses TREESHELL_DEBUG environment variable:
- TREESHELL_DEBUG="1": Print debug messages to console  
- TREESHELL_DEBUG="0" (default): Only print warnings/errors to console
- Always writes all messages to log file
- Renames log file with _ERROR suffix if any errors are logged
"""

import logging
import os
import atexit
from datetime import datetime
from pathlib import Path

# Check debug flag (same as global exception handler)
debug_enabled = os.getenv("TREESHELL_DEBUG", "0") == "1"

# Create logs directory
log_dir = Path('/tmp/heaven_data/logs')
log_dir.mkdir(parents=True, exist_ok=True)

# Create log file with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = log_dir / f'treeshell_{timestamp}.log'

# Track if any errors were logged
has_errors = False

# Set up logger
logger = logging.getLogger('treeshell')
logger.setLevel(logging.DEBUG)
logger.handlers.clear()

# File handler - always logs everything
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler - respects TREESHELL_DEBUG
if debug_enabled:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

def rename_log_if_errors():
    """Rename log file to include _ERROR suffix if errors were logged."""
    global has_errors
    if has_errors and log_file.exists():
        error_log_file = log_dir / f'treeshell_{timestamp}_ERROR.log'
        log_file.rename(error_log_file)

# Register cleanup function to rename log file on exit
atexit.register(rename_log_if_errors)

def debug(msg):
    """Log debug message."""
    logger.debug(msg)

def info(msg):
    """Log info message."""
    logger.info(msg)

def warning(msg):
    """Log warning message."""
    logger.warning(msg)

def error(msg):
    """Log error message and mark log for error renaming."""
    global has_errors
    has_errors = True
    logger.error(msg)