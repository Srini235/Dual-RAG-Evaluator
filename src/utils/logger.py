"""
Logging Utilities

Provides centralized logging configuration for the application.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def configure_logging(
    name: str = "dual_rag",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "./logs",
) -> logging.Logger:
    """
    Configure and return a logger for the application.

    Args:
        name: Logger name.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Log file path. If None, uses {log_dir}/{name}.log
        log_dir: Directory for log files.

    Returns:
        Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Set log file
    if log_file is None:
        log_file = log_path / f"{name}.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(message)s",
    )

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


# Application loggers
_app_logger = None
_rag_logger = None
_ui_logger = None


def get_app_logger(level: str = "INFO") -> logging.Logger:
    """Get or create application logger."""
    global _app_logger
    if _app_logger is None:
        _app_logger = configure_logging("dual_rag", level=level)
    return _app_logger


def get_rag_logger(level: str = "INFO") -> logging.Logger:
    """Get or create RAG pipeline logger."""
    global _rag_logger
    if _rag_logger is None:
        _rag_logger = configure_logging("dual_rag.core", level=level)
    return _rag_logger


def get_ui_logger(level: str = "INFO") -> logging.Logger:
    """Get or create UI logger."""
    global _ui_logger
    if _ui_logger is None:
        _ui_logger = configure_logging("dual_rag.ui", level=level)
    return _ui_logger


# Convenience aliases
app_logger = get_app_logger()
rag_logger = get_rag_logger()
ui_logger = get_ui_logger()
