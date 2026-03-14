"""
Unit Tests for Logger Utilities
"""

import pytest
import tempfile
import logging
from pathlib import Path
from src.utils import configure_logging, get_app_logger, get_rag_logger, get_ui_logger


class TestLogging:
    """Test suite for logging utilities."""

    def test_configure_logging(self):
        """Test logging configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = configure_logging(
                name="test_logger",
                level="DEBUG",
                log_dir=temp_dir,
            )

            assert logger is not None
            assert logger.name == "test_logger"
            assert logger.level == logging.DEBUG

            # Verify log file was created
            log_files = list(Path(temp_dir).glob("*.log"))
            assert len(log_files) > 0

    def test_configure_logging_with_custom_file(self):
        """Test configuration with custom log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "custom.log"
            logger = configure_logging(
                name="custom_logger",
                log_file=str(log_file),
            )

            assert logger is not None
            assert log_file.exists()

    def test_logging_levels(self):
        """Test different logging levels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

            for level in levels:
                logger = configure_logging(
                    name=f"logger_{level}",
                    level=level,
                    log_dir=temp_dir,
                )
                assert logger.level == getattr(logging, level)

    def test_logger_writes_to_file(self):
        """Test that logger writes messages to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = configure_logging(
                name="file_test",
                level="INFO",
                log_dir=temp_dir,
            )

            logger.info("Test message")

            log_file = Path(temp_dir) / "file_test.log"
            assert log_file.exists()
            with open(log_file) as f:
                content = f.read()
                assert "Test message" in content

    def test_get_app_logger_singleton(self):
        """Test app logger singleton."""
        logger1 = get_app_logger()
        logger2 = get_app_logger()
        assert logger1 is logger2

    def test_get_rag_logger_singleton(self):
        """Test RAG logger singleton."""
        logger1 = get_rag_logger()
        logger2 = get_rag_logger()
        assert logger1 is logger2

    def test_get_ui_logger_singleton(self):
        """Test UI logger singleton."""
        logger1 = get_ui_logger()
        logger2 = get_ui_logger()
        assert logger1 is logger2

    def test_logger_has_handlers(self):
        """Test that configured logger has handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = configure_logging(
                name="handler_test",
                log_dir=temp_dir,
            )

            # Should have at least file and console handlers
            assert len(logger.handlers) >= 2

    def test_logger_formats_messages(self):
        """Test that logger formats messages correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = configure_logging(
                name="format_test",
                level="INFO",
                log_dir=temp_dir,
            )

            logger.info("Formatted message")

            log_file = Path(temp_dir) / "format_test.log"
            with open(log_file) as f:
                content = f.read()
                # Should contain timestamp, logger name, level, and message
                assert "INFO" in content
                assert "Formatted message" in content
