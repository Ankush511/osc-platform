"""
Centralized logging configuration for the application.
"""
import logging
import sys
from typing import Any
from loguru import logger
from .config import settings


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and redirect to loguru.
    """
    
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    Configure application logging with loguru.
    """
    # Remove default logger
    logger.remove()
    
    # Add console handler with custom format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    if settings.ENVIRONMENT == "production":
        # JSON format for production (easier to parse)
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
            level=settings.LOG_LEVEL.upper(),
            serialize=True,  # Output as JSON
            backtrace=True,
            diagnose=False,  # Don't show variable values in production
        )
    else:
        # Pretty format for development
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.LOG_LEVEL.upper(),
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    
    # Add file handler for errors
    logger.add(
        "logs/error.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        serialize=True,
    )
    
    # Add file handler for all logs
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
        level=settings.LOG_LEVEL.upper(),
        rotation="100 MB",
        retention="7 days",
        compression="zip",
    )
    
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Set log levels for third-party libraries
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False


def get_logger(name: str) -> Any:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Module name
        
    Returns:
        Logger instance
    """
    return logger.bind(module=name)
