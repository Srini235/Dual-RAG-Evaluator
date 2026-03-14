"""
Configuration Management System

Loads and manages settings from .env files and environment variables.
Provides centralized access to application configuration.
"""

import os
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class Settings:
    """Application settings loaded from .env file or environment variables."""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize settings from environment variables or .env file.

        Args:
            env_file: Path to .env file. If None, searches in config/ directory.
        """
        if env_file is None:
            # Search for .env in config/ directory relative to project root
            env_file = Path(__file__).parent.parent.parent / "config" / ".env"

        self.env_file = Path(env_file)
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment from {self.env_file}")
        else:
            logger.warning(f"Environment file not found: {self.env_file}")

    @property
    def APP_NAME(self) -> str:
        """Application name."""
        return os.getenv("APP_NAME", "Dual-RAG-Evaluator")

    @property
    def APP_VERSION(self) -> str:
        """Application version."""
        return os.getenv("APP_VERSION", "1.0.0")

    @property
    def DEBUG(self) -> bool:
        """Enable debug mode."""
        return os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    @property
    def LOG_LEVEL(self) -> str:
        """Logging level."""
        return os.getenv("LOG_LEVEL", "INFO")

    # Database Settings
    @property
    def CHROMADB_PATH(self) -> str:
        """ChromaDB storage path."""
        return os.getenv("CHROMADB_PATH", "./data/embeddings/chromadb")

    @property
    def RESONANCEDB_HOST(self) -> str:
        """ResonanceDB host address."""
        return os.getenv("RESONANCEDB_HOST", "localhost")

    @property
    def RESONANCEDB_PORT(self) -> int:
        """ResonanceDB port."""
        return int(os.getenv("RESONANCEDB_PORT", "8080"))

    @property
    def RESONANCEDB_URL(self) -> str:
        """ResonanceDB connection URL."""
        return f"http://{self.RESONANCEDB_HOST}:{self.RESONANCEDB_PORT}"

    @property
    def USE_MOCK_RESONANCEDB(self) -> bool:
        """Use mock ResonanceDB client (for testing)."""
        return os.getenv("USE_MOCK_RESONANCEDB", "true").lower() in ("true", "1", "yes")

    # Embedding Settings
    @property
    def EMBEDDING_MODEL(self) -> str:
        """Embedding model name."""
        return os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    @property
    def EMBEDDING_DIMENSION(self) -> int:
        """Embedding vector dimension."""
        return int(os.getenv("EMBEDDING_DIMENSION", "384"))

    @property
    def BATCH_SIZE(self) -> int:
        """Batch size for embedding generation."""
        return int(os.getenv("BATCH_SIZE", "32"))

    # RAG Settings
    @property
    def CHUNK_SIZE(self) -> int:
        """Text chunk size for document processing."""
        return int(os.getenv("CHUNK_SIZE", "500"))

    @property
    def CHUNK_OVERLAP(self) -> int:
        """Overlap between consecutive chunks."""
        return int(os.getenv("CHUNK_OVERLAP", "50"))

    @property
    def TOP_K(self) -> int:
        """Number of top results to retrieve."""
        return int(os.getenv("TOP_K", "5"))

    @property
    def SIMILARITY_THRESHOLD(self) -> float:
        """Minimum similarity score threshold."""
        return float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

    @property
    def CONFIDENCE_THRESHOLD(self) -> float:
        """Confidence threshold for results."""
        return float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

    # Negation Detection
    @property
    def NEGATION_ENABLED(self) -> bool:
        """Enable negation detection."""
        return os.getenv("NEGATION_ENABLED", "true").lower() in ("true", "1", "yes")

    @property
    def NEGATION_WORDS_FILE(self) -> str:
        """Path to negation words file."""
        return os.getenv("NEGATION_WORDS_FILE", "config/negation_words.txt")

    # Document Processing
    @property
    def MAX_FILE_SIZE_MB(self) -> int:
        """Maximum file size in MB."""
        return int(os.getenv("MAX_FILE_SIZE_MB", "10"))

    @property
    def SUPPORTED_FORMATS(self) -> list:
        """Supported document formats."""
        formats = os.getenv("SUPPORTED_FORMATS", "pdf,docx,txt,md")
        return formats.split(",")

    @property
    def TEXT_PREVIEW_LENGTH(self) -> int:
        """Length of text preview."""
        return int(os.getenv("TEXT_PREVIEW_LENGTH", "500"))

    # UI Settings
    @property
    def WINDOW_WIDTH(self) -> int:
        """Main window width."""
        return int(os.getenv("WINDOW_WIDTH", "1200"))

    @property
    def WINDOW_HEIGHT(self) -> int:
        """Main window height."""
        return int(os.getenv("WINDOW_HEIGHT", "800"))

    @property
    def THEME(self) -> str:
        """UI theme (light, dark, system)."""
        return os.getenv("THEME", "light")

    @property
    def SHOW_ADVANCED_OPTIONS(self) -> bool:
        """Show advanced configuration options."""
        return os.getenv("SHOW_ADVANCED_OPTIONS", "false").lower() in ("true", "1", "yes")

    # Export Settings
    @property
    def EXPORT_FORMAT_PDF(self) -> bool:
        """Enable PDF export."""
        return os.getenv("EXPORT_FORMAT_PDF", "true").lower() in ("true", "1", "yes")

    @property
    def EXPORT_FORMAT_CSV(self) -> bool:
        """Enable CSV export."""
        return os.getenv("EXPORT_FORMAT_CSV", "true").lower() in ("true", "1", "yes")

    @property
    def EXPORT_FORMAT_JSON(self) -> bool:
        """Enable JSON export."""
        return os.getenv("EXPORT_FORMAT_JSON", "true").lower() in ("true", "1", "yes")

    @property
    def EXPORT_FORMAT_HTML(self) -> bool:
        """Enable HTML export."""
        return os.getenv("EXPORT_FORMAT_HTML", "true").lower() in ("true", "1", "yes")

    @property
    def RESULTS_DIRECTORY(self) -> str:
        """Directory for results and exports."""
        return os.getenv("RESULTS_DIRECTORY", "./results")

    # Advanced Settings
    @property
    def CACHE_ENABLED(self) -> bool:
        """Enable result caching."""
        return os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")

    @property
    def CACHE_DIRECTORY(self) -> str:
        """Cache directory."""
        return os.getenv("CACHE_DIRECTORY", "./data/cache")

    @property
    def CACHE_TTL_HOURS(self) -> int:
        """Cache time-to-live in hours."""
        return int(os.getenv("CACHE_TTL_HOURS", "24"))

    @property
    def BATCH_PROCESSING_ENABLED(self) -> bool:
        """Enable batch document processing."""
        return os.getenv("BATCH_PROCESSING_ENABLED", "true").lower() in ("true", "1", "yes")

    @property
    def QUERY_HISTORY_SIZE(self) -> int:
        """Number of queries to keep in history."""
        return int(os.getenv("QUERY_HISTORY_SIZE", "50"))

    @property
    def METRICS_ENABLED(self) -> bool:
        """Enable performance metrics collection."""
        return os.getenv("METRICS_ENABLED", "true").lower() in ("true", "1", "yes")

    # API Settings (for REST API, if implemented)
    @property
    def API_HOST(self) -> str:
        """API server host."""
        return os.getenv("API_HOST", "127.0.0.1")

    @property
    def API_PORT(self) -> int:
        """API server port."""
        return int(os.getenv("API_PORT", "8000"))

    @property
    def API_WORKERS(self) -> int:
        """Number of API worker processes."""
        return int(os.getenv("API_WORKERS", "4"))

    def to_dict(self) -> dict:
        """Convert all settings to dictionary."""
        return {
            k: getattr(self, k)
            for k in dir(self)
            if not k.startswith("_") and k.isupper() and not callable(getattr(self, k))
        }

    def __repr__(self) -> str:
        """String representation of settings."""
        return f"Settings(debug={self.DEBUG}, app_name={self.APP_NAME})"


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """
    Get global settings instance (lazy initialization).

    Returns:
        Settings: Global settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience function for importing
settings = get_settings()
