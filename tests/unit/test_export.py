"""
Unit Tests for Export Utilities
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.utils import ResultExporter


class TestResultExporter:
    """Test suite for ResultExporter class."""

    @pytest.fixture
    def exporter(self):
        """Create exporter instance with temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield ResultExporter(output_directory=temp_dir)

    @pytest.fixture
    def sample_results(self):
        """Create sample results for testing."""
        return {
            "query": "test query",
            "chromadb": {"score": 0.85, "time": 0.5},
            "resonancedb": {"score": 0.92, "time": 0.6},
        }

    def test_exporter_initialization(self, exporter):
        """Test exporter initialization."""
        assert exporter.output_dir.exists()

    def test_export_json(self, exporter, sample_results):
        """Test JSON export."""
        success, filepath = exporter.export_json(sample_results, "test_results.json")
        assert success
        assert filepath is not None
        assert Path(filepath).exists()

        # Verify JSON content
        with open(filepath) as f:
            loaded = json.load(f)
            assert loaded["query"] == "test query"

    def test_export_json_auto_filename(self, exporter, sample_results):
        """Test JSON export with auto-generated filename."""
        success, filepath = exporter.export_json(sample_results)
        assert success
        assert filepath is not None
        assert "results_" in Path(filepath).name
        assert filepath.endswith(".json")

    def test_export_csv(self, exporter):
        """Test CSV export."""
        results = [
            {"metric": "score", "chromadb": 0.85, "resonancedb": 0.92},
            {"metric": "time", "chromadb": 0.5, "resonancedb": 0.6},
        ]
        success, filepath = exporter.export_csv(results, "test_results.csv")
        assert success
        assert filepath is not None
        assert Path(filepath).exists()

    def test_export_csv_empty(self, exporter):
        """Test CSV export with empty results."""
        success, filepath = exporter.export_csv([], "test_results.csv")
        assert not success

    def test_export_html(self, exporter, sample_results):
        """Test HTML export."""
        success, filepath = exporter.export_html(sample_results, "test_results.html")
        assert success
        assert filepath is not None
        assert Path(filepath).exists()

        # Verify HTML content
        with open(filepath) as f:
            content = f.read()
            assert "<!DOCTYPE html>" in content
            assert "Dual-RAG" in content

    def test_export_pdf(self, exporter, sample_results):
        """Test PDF export."""
        success, filepath = exporter.export_pdf(sample_results, "test_results.pdf")
        assert success
        assert filepath is not None
        assert Path(filepath).exists()
        assert filepath.endswith(".pdf")

    def test_export_formats_auto_filenames(self, exporter, sample_results):
        """Test all export formats with auto-generated filenames."""
        formats = [
            ("json", exporter.export_json),
            ("html", exporter.export_html),
            ("pdf", exporter.export_pdf),
        ]

        for format_name, export_func in formats:
            success, filepath = export_func(sample_results)
            assert success
            assert filepath.endswith(f".{format_name}")
            assert "results_" in Path(filepath).name
