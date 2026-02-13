from loguru import logger
import sys
import os


def setup_logging():
    """Configure Loguru logging"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # File handler with rotation
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logger.add(
        f"{log_dir}/app_{{time:YYYY-MM-DD}}.log",
        rotation="1 day",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        enqueue=True  # Thread-safe
    )
    
    logger.info("Logging configured successfully")
    return logger
