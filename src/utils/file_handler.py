"""
File Handling Utilities

Provides document loading, parsing, and validation functionality.
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
import logging

try:
    from PyPDF2 import PdfReader
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from docx import Document
    PYTHON_DOCX_AVAILABLE = True
except ImportError:
    PYTHON_DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)


class DocumentHandler:
    """Handle document file operations: loading, parsing, validation."""

    SUPPORTED_FORMATS = {".pdf", ".txt", ".md", ".docx"}
    DEFAULT_MAX_SIZE_MB = 10

    def __init__(self, max_size_mb: int = DEFAULT_MAX_SIZE_MB):
        """
        Initialize document handler.

        Args:
            max_size_mb: Maximum file size in MB.
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        logger.info(f"DocumentHandler initialized with max size: {max_size_mb}MB")

    def is_supported_format(self, filepath: str) -> bool:
        """
        Check if file format is supported.

        Args:
            filepath: Path to the file.

        Returns:
            True if format is supported, False otherwise.
        """
        path = Path(filepath)
        return path.suffix.lower() in self.SUPPORTED_FORMATS

    def validate_file(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate if file is supported and within size limits.

        Args:
            filepath: Path to the file.

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(filepath)

        # Check if file exists
        if not path.exists():
            return False, f"File not found: {filepath}"

        # Check file extension
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            formats = ", ".join(self.SUPPORTED_FORMATS)
            return False, f"Unsupported format. Supported: {formats}"

        # Check file size
        file_size = path.stat().st_size
        if file_size > self.max_size_bytes:
            return False, f"File too large. Max: {self.max_size_bytes / 1024 / 1024:.1f}MB"

        return True, ""

    def load_document(self, filepath: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Load document from file.

        Args:
            filepath: Path to the document file.

        Returns:
            Tuple of (content, error_message)
        """
        is_valid, error = self.validate_file(filepath)
        if not is_valid:
            return None, error

        path = Path(filepath)
        try:
            if path.suffix.lower() == ".pdf":
                content = self._load_pdf(filepath)
            elif path.suffix.lower() == ".docx":
                content = self._load_docx(filepath)
            elif path.suffix.lower() in {".txt", ".md"}:
                content = self._load_text(filepath)
            else:
                return None, f"Unsupported file type: {path.suffix}"

            if content:
                logger.info(f"Successfully loaded document: {path.name}")
                return content, None
            else:
                return None, "Document is empty"

        except Exception as e:
            error_msg = f"Error loading document: {str(e)}"
            logger.error(error_msg)
            return None, error_msg

    @staticmethod
    def _load_pdf(filepath: str) -> Optional[str]:
        """Load text from PDF file."""
        if not PYPDF2_AVAILABLE:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return None
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return None

    @staticmethod
    def _load_docx(filepath: str) -> Optional[str]:
        """Load text from DOCX file."""
        if not PYTHON_DOCX_AVAILABLE:
            logger.warning("python-docx not installed. Install with: pip install python-docx")
            return None
        try:
            doc = Document(filepath)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"Error reading DOCX: {e}")
            return None

    @staticmethod
    def _load_text(filepath: str) -> Optional[str]:
        """Load text from TXT or Markdown file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            return None

    def get_preview(
        self, filepath: str, preview_length: int = 500
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Get a preview of the document.

        Args:
            filepath: Path to the document.
            preview_length: Length of preview text.

        Returns:
            Tuple of (preview_text, error_message)
        """
        content, error = self.load_document(filepath)
        if error:
            return None, error

        preview = content[: preview_length]
        if len(content) > preview_length:
            preview += f"\n... [truncated, total length: {len(content)} chars]"

        return preview, None

    @staticmethod
    def save_text(filepath: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Save text to a file.

        Args:
            filepath: Path where to save the file.
            content: Text content to save.

        Returns:
            Tuple of (success, error_message)
        """
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Saved document to: {filepath}")
            return True, None
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
