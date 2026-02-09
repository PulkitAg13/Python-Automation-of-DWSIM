"""
Logging utilities
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

def setup_logger(name: str = "dwsim", log_level: str = "INFO", 
                log_file: str = None) -> logging.Logger:
    """Setup and configure logger"""
    
    # Map string level to logging constant
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        try:
            # Ensure directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(file_format)
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_file}")
        except Exception as e:
            logger.warning(f"Could not setup file logging: {str(e)}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str = "dwsim") -> logging.Logger:
    """Get existing logger or create new one"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Get log level from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/simulation.log')
        
        logger = setup_logger(name, log_level, log_file)
    
    return logger

class LogCapture:
    """Context manager to capture log messages"""
    
    def __init__(self, logger_name: str = "dwsim", level: str = "INFO"):
        self.logger_name = logger_name
        self.level = level
        self.captured_messages = []
        self.original_handlers = []
        
    def __enter__(self):
        logger = logging.getLogger(self.logger_name)
        
        # Save original handlers
        self.original_handlers = logger.handlers.copy()
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Add capturing handler
        capture_handler = logging.Handler()
        capture_handler.setLevel(getattr(logging, self.level.upper()))
        
        def capture(record):
            self.captured_messages.append(record.getMessage())
        
        capture_handler.emit = lambda record: capture(record)
        logger.addHandler(capture_handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = logging.getLogger(self.logger_name)
        
        # Restore original handlers
        logger.handlers.clear()
        for handler in self.original_handlers:
            logger.addHandler(handler)
    
    def get_messages(self) -> list:
        """Get captured log messages"""
        return self.captured_messages
    
    def clear(self):
        """Clear captured messages"""
        self.captured_messages.clear()