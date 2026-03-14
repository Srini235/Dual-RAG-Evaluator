"""
Unit Tests for Configuration Module
"""

import pytest
import os
from src.config import Settings, get_settings


class TestSettings:
    """Test suite for Settings class."""

    def test_settings_initialization(self):
        """Test settings initialization."""
        settings = Settings()
        assert settings.APP_NAME is not None
        assert settings.APP_VERSION is not None

    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        assert settings.CHUNK_SIZE == 500
        assert settings.CHUNK_OVERLAP == 50
        assert settings.TOP_K == 5
        assert settings.MAX_FILE_SIZE_MB == 10

    def test_boolean_settings(self):
        """Test boolean setting parsing."""
        settings = Settings()
        assert isinstance(settings.DEBUG, bool)
        assert isinstance(settings.NEGATION_ENABLED, bool)
        assert isinstance(settings.CACHE_ENABLED, bool)

    def test_numeric_settings(self):
        """Test numeric setting parsing."""
        settings = Settings()
        assert isinstance(settings.WINDOW_WIDTH, int)
        assert isinstance(settings.WINDOW_HEIGHT, int)
        assert isinstance(settings.BATCH_SIZE, int)

    def test_float_settings(self):
        """Test float setting parsing."""
        settings = Settings()
        assert isinstance(settings.SIMILARITY_THRESHOLD, float)
        assert isinstance(settings.CONFIDENCE_THRESHOLD, float)

    def test_supported_formats(self):
        """Test supported document formats."""
        settings = Settings()
        formats = settings.SUPPORTED_FORMATS
        assert isinstance(formats, list)
        assert ".pdf" in formats or "pdf" in formats

    def test_get_settings_singleton(self):
        """Test settings singleton behavior."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_settings_to_dict(self):
        """Test converting settings to dictionary."""
        settings = Settings()
        settings_dict = settings.to_dict()
        assert isinstance(settings_dict, dict)
        assert "APP_NAME" in settings_dict
        assert len(settings_dict) > 0
