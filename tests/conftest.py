"""
Pytest Configuration and Fixtures

Provides common fixtures and configuration for test suite.
"""

import pytest
import tempfile
from pathlib import Path


@pytest.fixture
def temp_directory():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_text_file(temp_directory):
    """Create a sample text file for testing."""
    filepath = temp_directory / "sample.txt"
    filepath.write_text("This is a sample text document for testing.\n" * 10)
    return filepath


@pytest.fixture
def sample_markdown_file(temp_directory):
    """Create a sample markdown file for testing."""
    filepath = temp_directory / "sample.md"
    content = """# Sample Markdown Document

## Introduction
This is a sample markdown document for testing purposes.

## Section 1
Some content here.

## Section 2
More content here.
"""
    filepath.write_text(content)
    return filepath


@pytest.fixture
def sample_results():
    """Provide sample RAG results for testing."""
    return {
        "query": "diabetes treatment",
        "chromadb": {
            "results": [
                {"text": "Treatment A", "score": 0.85},
                {"text": "Treatment B", "score": 0.78},
            ],
            "execution_time": 0.45,
        },
        "resonancedb": {
            "results": [
                {"text": "Treatment A", "score": 0.89},
                {"text": "Treatment B", "score": 0.82},
            ],
            "execution_time": 0.52,
        },
        "metadata": {
            "negation_detected": False,
            "timestamp": "2024-01-15 10:30:00",
        },
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
