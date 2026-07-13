import logging
import sys
from datetime import datetime

# Configure structured logging
def setup_logger(name, level=logging.INFO):
    """Setup a logger with structured formatting"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create file handler
        file_handler = logging.FileHandler(f'logs/video_gen_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setLevel(level)
        
        # Create formatter with structured format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

# Global logger instance
logger = setup_logger('video_gen')