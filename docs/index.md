# Dual-RAG-Evaluator Documentation

Welcome to the Dual-RAG-Evaluator documentation!

## Overview

Dual-RAG-Evaluator is a comprehensive tool for comparing ChromaDB and ResonanceDB vector databases in Retrieval-Augmented Generation (RAG) applications, with special emphasis on semantic negation handling.

## Quick Links

- [Getting Started Guide](getting-started.md)
- [Architecture Documentation](architecture/index.md)
- [API Reference](api/index.md)
- [User Guide](user-guide.md)
- [Developer Guide](../DEVELOPER.md)

## Key Features

- **Side-by-side RAG Comparison**: Compare results from ChromaDB and ResonanceDB
- **Negation Detection**: Explicit handling of negation queries and semantic inversion
- **Multi-format Export**: PDF, CSV, JSON, HTML result export
- **Professional GUI**: PyQt5-based user interface
- **Extensible Architecture**: Easy to add new RAG components

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/Srini235/Dual-RAG-Evaluator.git
cd Dual-RAG-Evaluator

# Run setup script
# Windows
setup.bat

# Linux/macOS
bash setup.sh

# Activate environment
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### First Run

```bash
# Configure environment
cp config/.env.template config/.env
nano config/.env  # Edit settings

# Launch GUI
python -m src.main

# Or run tests
pytest tests/ -v
```

## Documentation Structure

### For Users

- [User Guide](user-guide.md) - How to use the application
- [Configuration Guide](configuration.md) - Setting up your environment
- [Export Guide](export-guide.md) - Exporting results

### For Developers

- [Developer Guide](../DEVELOPER.md) - Development setup and workflow
- [Architecture Guide](architecture/README.md) - System architecture
- [API Documentation](api/index.md) - Module reference
- [Testing Guide](testing.md) - Writing and running tests

### Reference

- [Changelog](../CHANGELOG.md) - Version history
- [Contributing](../CONTRIBUTING.md) - How to contribute
- [Security Policy](../SECURITY.md) - Vulnerability reporting

## Project Structure

```
Dual-RAG-Evaluator/
├── src/              # Application source code
│   ├── core/         # RAG pipeline components
│   ├── ui/           # GUI components
│   ├── utils/        # Utility modules
│   ├── config/       # Configuration management
│   └── main.py       # Application entry point
├── tests/            # Test suite
├── docs/             # Documentation
├── config/           # Configuration files
└── data/             # Data storage (documents, embeddings)
```

## Python API

### Core Modules

```python
from src.core import (
    DocumentProcessor,      # Load and chunk documents
    BaselineRetriever,      # ChromaDB vector search
    ResonanceClient,        # ResonanceDB client
    WaveMapper,             # Wave calculations
    DualRAGEvaluator,       # Comparison metrics
)

from src.utils import (
    DocumentHandler,        # File I/O
    ResultExporter,         # Export results
    get_app_logger,         # Application logging
)

from src.config import get_settings  # Configuration
```

### Example Usage

```python
from src.core import DocumentProcessor, BaselineRetriever

# Initialize components
processor = DocumentProcessor()
retriever = BaselineRetriever()

# Load document
chunks = processor.process_document("document.pdf")

# Search
results = retriever.search("query", top_k=5)
```

## Running the Application

### GUI Mode (Default)

```bash
python -m src.main
```

### CLI Mode (Coming Soon)

```bash
python -m src.main --cli
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# With coverage
pytest tests/ --cov=src
```

### Run with Docker

```bash
# Build image
docker build -t dual-rag-evaluator:latest .

# Run container
docker run -it -v $(pwd)/data:/app/data dual-rag-evaluator:latest
```

## System Requirements

- **Python**: 3.10 or higher
- **OS**: Windows, Linux, or macOS
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB for models and data

## Dependencies

### Core
- sentence-transformers (embeddings)
- chromadb (vector database)
- torch (ML framework)
- langchain (RAG orchestration)

### GUI
- PyQt5 (user interface)

### Export
- reportlab (PDF generation)
- pandas (data processing)

See `requirements.txt` for complete list.

## Performance

- **Document Processing**: ~100 documents/minute
- **Query Retrieval**: ~0.5s per query
- **Export**: <1s for PDF, <0.5s for CSV/JSON/HTML

## Contributing

We welcome contributions! See [CONTRIBUTING](../CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](../LICENSE) file

## Support

- **Documentation**: See this site
- **Issues**: [GitHub Issues](https://github.com/Srini235/Dual-RAG-Evaluator/issues)
- **Security**: See [SECURITY.md](../SECURITY.md)

## Citation

If you use Dual-RAG-Evaluator in your research:

```bibtex
@software{dual_rag_evaluator_2024,
  title={Dual-RAG-Evaluator: Comparing Vector Databases for RAG},
  author={Srini235},
  year={2024},
  url={https://github.com/Srini235/Dual-RAG-Evaluator}
}
```

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Status**: Production Ready

```{toctree}
:hidden:

getting-started
architecture/index
api/index
user-guide
configuration
export-guide
testing
```
