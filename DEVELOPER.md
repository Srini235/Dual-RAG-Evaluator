# Developer Guide - Dual-RAG-Evaluator

## Quick Start

### 1. Environment Setup

**Windows:**
```bash
setup.bat
venv\Scripts\activate
pip install -r requirements-dev.txt
```

**Linux/macOS:**
```bash
bash setup.sh
source venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Running the Application

**GUI Application:**
```bash
python -m src.main
```

**CLI Interface (when ready):**
```bash
python -m src.main --cli
```

**Run Tests:**
```bash
pytest tests/ -v
pytest tests/unit/ -v  # Only unit tests
pytest tests/integration/ -v  # Only integration tests
```

### 3. Code Quality

**Format code:**
```bash
make format
# or
black src/ tests/
isort src/ tests/
```

**Lint code:**
```bash
make lint
# or
flake8 src/ tests/ --max-line-length=100
```

**Type checking:**
```bash
make type-check
# or
mypy src/ --ignore-missing-imports
```

**Run all checks:**
```bash
make check
```

## Project Organization

```
src/
├── __init__.py              # Package initialization
├── main.py                  # Application entry point
├── config/                  # Configuration management
│   ├── __init__.py
│   └── settings.py          # Settings class
├── core/                    # Core RAG pipeline
│   ├── __init__.py
│   ├── doc_processor.py     # Document loading & chunking
│   ├── baseline_retriever.py # ChromaDB wrapper
│   ├── resonance_client.py  # ResonanceDB client
│   ├── wave_mapper.py       # Wave calculations
│   └── evaluator.py         # Comparison & metrics
├── ui/                      # User interface
│   ├── __init__.py
│   └── main_window.py       # GUI main window
└── utils/                   # Utility modules
    ├── __init__.py
    ├── file_handler.py      # Document I/O
    ├── export.py            # Result export (PDF/CSV/JSON/HTML)
    └── logger.py            # Logging configuration

config/
├── .env.template            # Configuration template
└── negation_words.txt       # Negation word list

tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── unit/                    # Unit tests
│   ├── test_config.py
│   ├── test_file_handler.py
│   ├── test_export.py
│   └── test_logger.py
└── integration/             # Integration tests

docs/
├── architecture/            # Architecture diagrams (to be created)
├── api/                     # API documentation (Doxygen)
└── guides/                  # Analysis documentation

data/
├── documents/               # User-uploaded documents
├── embeddings/              # ChromaDB storage
└── cache/                   # Query results cache

results/                     # Exported results go here
```

## Adding New Features

### 1. Core RAG Module

If adding to the RAG pipeline:

1. Create module in `src/core/`
2. Add imports to `src/core/__init__.py`
3. Write unit tests in `tests/unit/`
4. Update `README.md` with feature description

### 2. UI Component

If adding to the GUI:

1. Create class in `src/ui/main_window.py` or separate file
2. Add to imports in `src/ui/__init__.py`
3. Test manually by running GUI
4. Document the UI element

### 3. Utility Function

If adding utilities:

1. Create in `src/utils/` (new file or existing)
2. Add import to `src/utils/__init__.py`
3. Write unit tests in `tests/unit/`
4. Update docstring with examples

## Configuration

Edit `config/.env`:

```bash
# Copy template
cp config/.env.template config/.env

# Edit with your settings
nano config/.env  # Linux/macOS
notepad config\.env  # Windows
```

Key settings:
- `EMBEDDING_MODEL`: Which model to use for embeddings
- `CHUNK_SIZE`: Document chunk size (default 500)
- `TOP_K`: Number of results to retrieve (default 5)
- `MAX_FILE_SIZE_MB`: Max upload size (default 10MB)
- `EXPORT_FORMAT_*`: Enable/disable export formats

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_config.py -v
```

### Run Test with Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

Coverage report will be in `htmlcov/index.html`

### Test Markers

```bash
# Unit tests only
pytest -m unit tests/

# Integration tests only
pytest -m integration tests/

# Slow tests
pytest -m slow tests/
```

## Build & Distribution

### Build Distribution

```bash
make build
# Creates dist/dual-rag-evaluator-*.tar.gz and .whl
```

### Install Locally (Development)

```bash
pip install -e .
```

### Install Locally (User)

```bash
pip install dist/dual_rag_evaluator-1.0.0-py3-none-any.whl
```

## Docker

### Build Docker Image

```bash
make docker-build
# or
docker build -t dual-rag-evaluator:latest .
```

### Run in Docker

```bash
make docker-run
# or
docker run -it -v $(pwd)/data:/app/data dual-rag-evaluator:latest
```

### Docker Compose

```bash
docker-compose up -d  # Start services
docker-compose down   # Stop services
```

## Documentation

### Generate Sphinx Documentation

```bash
make docs
```

Documentation will be in `docs/_build/html/`

### View Documentation

```bash
make docs-serve
# Open http://localhost:8000
```

### Doxygen Documentation (Future)

```bash
doxygen Doxyfile
# Open docs/_build/doxygen/html/index.html
```

## Code Style Guidelines

### Python (PEP 8)

- **Line length**: 100 characters
- **Indentation**: 4 spaces
- **Comments**: Use meaningful comments, explain "why" not "what"

### Docstrings

Use Google style docstrings:

```python
def process_document(filepath: str, chunk_size: int = 500) -> List[str]:
    """
    Process a document and return text chunks.
    
    Args:
        filepath: Path to the document
        chunk_size: Size of each chunk
        
    Returns:
        List of text chunks
        
    Raises:
        FileNotFoundError: If document doesn't exist
        ValueError: If chunk_size is invalid
    """
    pass
```

### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Any

def calculate_similarity(
    vec1: List[float],
    vec2: List[float],
) -> float:
    """Calculate cosine similarity between two vectors."""
    pass
```

## Debugging

### Enable Debug Mode

```bash
# In code
from src.config import get_settings
settings = get_settings()
# settings.DEBUG will be True or False

# Or set environment variable
export DEBUG=true
python -m src.main --debug
```

### Logging

Loggers are available in each module:

```python
from src.utils import get_app_logger

logger = get_app_logger()
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

Logs go to:
- Console (INFO level default)
- `logs/dual_rag.log` (all levels)

## Performance Profiling

```bash
# Line-by-line profiling
kernprof -l -v script.py

# Memory profiling
mprof run script.py
mprof plot mprofile_*.dat
```

## Pre-commit Hooks

Setup automatic code checking before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install hook into git
pre-commit install

# Run manually
pre-commit run --all-files
```

## Common Tasks

### Add a New Dependency

1. Edit `requirements.txt` or `requirements-dev.txt`
2. Run `pip install -r requirements.txt`
3. Update setup.py install_requires
4. Commit changes

### Update Dependencies

```bash
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### Create a New Test

1. Create file in `tests/unit/` or `tests/integration/`
2. Follow naming: `test_*.py`
3. Use pytest fixtures from `conftest.py`
4. Run: `pytest tests/ -v`

### Generate Changelog

See `CHANGELOG.md` - update manually when releasing versions.

## Troubleshooting

### Import Errors

Ensure Python path includes project root:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Missing Dependencies

Reinstall all dependencies:
```bash
pip install --force-reinstall -r requirements.txt
```

### GUI Not Starting

```bash
# Check dependencies
python -c "from PyQt5.QtWidgets import QApplication"

# Run with debug
python -m src.main --debug
```

### Test Failures

```bash
# Run verbose
pytest tests/ -v

# Show print output
pytest tests/ -vs

# Show full traceback
pytest tests/ --tb=long
```

## Contributing

See `CONTRIBUTING.md` for guidelines on submitting changes.

## Security

See `SECURITY.md` for vulnerability reporting procedures.

## Support

- **Documentation**: See `/docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: (contact info in SECURITY.md)

---

**Happy developing!** 🚀
