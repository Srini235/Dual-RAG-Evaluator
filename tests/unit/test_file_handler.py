"""
Unit Tests for File Handling Utilities
"""

import pytest
import tempfile
from pathlib import Path
from src.utils import DocumentHandler


class TestDocumentHandler:
    """Test suite for DocumentHandler class."""

    @pytest.fixture
    def handler(self):
        """Create document handler instance."""
        return DocumentHandler(max_size_mb=10)

    @pytest.fixture
    def temp_file(self):
        """Create temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test document content")
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink()

    def test_handler_initialization(self, handler):
        """Test DocumentHandler initialization."""
        assert handler.max_size_bytes == 10 * 1024 * 1024

    def test_supported_formats(self, handler):
        """Test supported document formats."""
        assert ".pdf" in handler.SUPPORTED_FORMATS
        assert ".txt" in handler.SUPPORTED_FORMATS
        assert ".docx" in handler.SUPPORTED_FORMATS
        assert ".md" in handler.SUPPORTED_FORMATS

    def test_validate_file_not_found(self, handler):
        """Test validation of non-existent file."""
        is_valid, error = handler.validate_file("/non/existent/file.pdf")
        assert not is_valid
        assert "not found" in error.lower()

    def test_validate_file_unsupported_format(self, handler):
        """Test validation of unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix=".xyz") as f:
            is_valid, error = handler.validate_file(f.name)
            assert not is_valid
            assert "unsupported" in error.lower()

    def test_validate_file_valid(self, handler, temp_file):
        """Test validation of valid file."""
        is_valid, error = handler.validate_file(temp_file)
        assert is_valid
        assert error == ""

    def test_load_text_file(self, handler, temp_file):
        """Test loading text file."""
        content, error = handler.load_document(temp_file)
        assert error is None
        assert "Test document" in content

    def test_load_non_existent_file(self, handler):
        """Test loading non-existent file."""
        content, error = handler.load_document("/non/existent/file.txt")
        assert content is None
        assert error is not None

    def test_save_text_file(self, handler):
        """Test saving text file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test_output.txt"
            success, error = handler.save_text(str(filepath), "Test content")
            assert success
            assert error is None
            assert filepath.exists()
            with open(filepath) as f:
                assert f.read() == "Test content"

    def test_get_preview(self, handler, temp_file):
        """Test document preview."""
        preview, error = handler.get_preview(temp_file, preview_length=10)
        assert error is None
        assert len(preview) <= 20  # Some buffer for truncation message
