# Quick Start Guide - Dual-RAG-Evaluator

## 30 Second Setup

### Windows
```bash
setup.bat
```

### Linux/macOS
```bash
bash setup.sh
```

## Launch Application

```bash
python -m src.main
```

## Quick Commands

| Task | Command |
|------|---------|
| **Run GUI** | `python -m src.main` |
| **Run Tests** | `pytest tests/ -v` |
| **Check Code** | `make lint` |
| **Format Code** | `make format` |
| **View Docs** | `make docs-serve` |
| **Build Docker** | `make docker-build` |
| **Run Docker** | `make docker-run` |

## Key Files

| File | Purpose |
|------|---------|
| `config/.env` | Configuration (copy from `.env.template`) |
| `src/main.py` | Application entry point |
| `src/ui/main_window.py` | GUI application |
| `src/core/` | RAG pipeline modules |
| `src/utils/` | File I/O, export, logging |
| `tests/` | 30+ unit tests |

## Configuration

1. Copy template:
   ```bash
   cp config/.env.template config/.env
   ```

2. Edit settings (optional):
   ```bash
   nano config/.env  # Linux/macOS
   notepad config\.env  # Windows
   ```

3. Key settings:
   - `CHUNK_SIZE`: Document chunk size (default: 500)
   - `TOP_K`: Results to retrieve (default: 5)
   - `MAX_FILE_SIZE_MB`: Upload limit (default: 10)
   - `EMBEDDING_MODEL`: Model to use (default: all-MiniLM-L6-v2)

## Troubleshooting

### Import Errors
```bash
pip install --force-reinstall -r requirements.txt
```

### Python Version
```bash
python --version  # Must be 3.10+
```

### Port Already in Use
```bash
# Change API_PORT in config/.env
```

### GUI Not Starting
```bash
python -m src.main --debug  # See detailed errors
```

## Project Structure

```
src/
├── config/          # Settings management
├── core/            # RAG pipeline (doc processor, retriever, evaluator)
├── ui/              # PyQt5 GUI
└── utils/           # File I/O, export, logging

tests/
├── unit/            # 30+ unit tests
└── integration/     # Integration test framework

config/
├── .env.template    # Configuration template
└── negation_words.txt

data/
├── documents/       # Your documents here
├── embeddings/      # ChromaDB storage
└── cache/           # Query cache

docs/
├── guides/          # Analysis documentation
├── architecture/    # Architecture docs (to be created)
└── api/             # API docs (to be created)
```

## Features

✨ **GUI Application**
- Document upload (PDF, DOCX, TXT, Markdown)
- Query input with configuration
- Side-by-side RAG comparison
- Multi-format export (PDF, CSV, JSON, HTML)

🔧 **Configuration**
- 40+ settings via environment variables
- No code changes needed

📊 **Export**
- PDF reports with charts
- CSV for spreadsheets
- JSON for APIs
- HTML for web viewing

🧪 **Testing**
- 30+ unit tests
- Full coverage reporting
- Integration test framework

## Development

### Add a Feature
1. Create file in `src/core/` or `src/ui/`
2. Write unit tests in `tests/unit/`
3. Run tests: `pytest tests/ -v`
4. Format code: `make format`

### Run All Checks
```bash
make check
```

### Generate Documentation
```bash
make docs
```

## Docker

```bash
# Build
docker build -t dual-rag .

# Run
docker run -it -v $(pwd)/data:/app/data dual-rag

# Or with compose
docker-compose up -d
```

## Performance Tips

- **First Run**: Model download takes ~1 minute (one-time)
- **Embeddings**: ChromaDB cached locally for speed
- **Batch**: Use batch mode for 10+ documents
- **Memory**: Requires 4GB+ RAM

## Getting Help

| Need | Location |
|------|----------|
| **How to use** | `README.md` |
| **How to develop** | `DEVELOPER.md` |
| **How to contribute** | `CONTRIBUTING.md` |
| **Security issue** | `SECURITY.md` |
| **Project status** | `CHANGELOG.md` |

## What's Included

✅ Full PyQt5 GUI application  
✅ 4 export formats (PDF, CSV, JSON, HTML)  
✅ 30+ unit tests  
✅ Docker support  
✅ CI/CD pipeline  
✅ 5000+ lines of documentation  
✅ Configuration management  
✅ Professional logging  
✅ Production-ready code  

## Next Steps

1. **Run the app**: `python -m src.main`
2. **Try the tests**: `pytest tests/ -v`
3. **Read the docs**: `README.md`
4. **Configure it**: Edit `config/.env`
5. **Extend it**: Add features in `src/`

---

**Ready to go!** 🚀
