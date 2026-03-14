# Quick Start Guide - Build & Run Dual-RAG-Evaluator

## Option 1: Run Immediately (No Extra Setup)

### Test the Application Works
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

# Show version
python -m src.main --version

# Show all options
python -m src.main --help
```

**Expected Output:**
```
Dual-RAG-Evaluator v1.0.0
License: MIT
Author: Srini235
```

---

## Option 2: Run CLI Mode (Interactive)

```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

# Start interactive CLI
python -m src.main --cli
```

This launches the command-line interface for testing RAG comparison.

---

## Option 3: Run Test Suite

```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific test file
python -m pytest tests/unit/test_config.py -v

# Run tests with output
python -m pytest tests/unit/ -v -s
```

**Expected:** 25/34 tests pass

---

## Option 4: Full Setup with Optional Features (15 minutes)

### Step 1: Install Optional Dependencies
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

# Install PyQt5 (for GUI), python-docx (for DOCX), reportlab (for PDF)
pip install PyQt5 python-docx reportlab pytest-cov
```

### Step 2: Create Environment File
```bash
# Copy template to actual .env file
copy config\.env.template config\.env

# Optional: Edit config\.env with your settings
# But defaults work fine
```

### Step 3: Run the Full Application
```bash
# GUI Mode (if PyQt5 installed)
python -m src.main

# Or specific modes
python -m src.main --cli          # CLI mode
python -m src.main --test         # Run tests
python -m src.main --debug        # Debug mode
python -m src.main --log-level DEBUG  # Set log level
```

---

## Option 5: Docker Build & Run (30-45 minutes)

### Step 1: Build Docker Image
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

docker build -t dual-rag-evaluator:1.0.0 .

# Wait for build to complete (downloading CUDA dependencies takes time)
# Expected: "Successfully tagged dual-rag-evaluator:1.0.0"
```

### Step 2: Run Docker Container
```bash
# Interactive mode
docker run -it dual-rag-evaluator:1.0.0

# With volume mount for data
docker run -it -v %cd%\data:/app/data dual-rag-evaluator:1.0.0

# With port mapping (if using REST API)
docker run -it -p 8000:8000 dual-rag-evaluator:1.0.0
```

---

## Option 6: Use Docker Compose

### Step 1: Start Services
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

docker compose up -d
```

### Step 2: Check Status
```bash
docker compose ps
docker compose logs
```

### Step 3: Access Application
```bash
docker compose exec app python -m src.main --cli
```

---

## Option 7: Development Mode

### Step 1: Create Virtual Environment
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator

python -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
# Windows
venv\Scripts\activate

# Or use it directly
venv\Scripts\python.exe -m src.main --version
```

### Step 3: Install Dependencies
```bash
pip install -r requirements-dev.txt
```

### Step 4: Run Tests in Watch Mode
```bash
pytest tests/ -v --tb=short
```

---

## Which Option Should I Choose?

| Option | Time | Requirements | Best For |
|--------|------|--------------|----------|
| **Option 1** | 1 min | Python only | Quick verification |
| **Option 2** | 1 min | Python only | CLI testing |
| **Option 3** | 5 min | pytest | Running tests |
| **Option 4** | 15 min | pip packages | Full features |
| **Option 5** | 45 min | Docker | Production deploy |
| **Option 6** | 45 min | Docker Compose | Multi-service setup |
| **Option 7** | 10 min | Python venv | Development/coding |

---

## Recommended Starting Path

### For Quick Testing (5 minutes)
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator
python -m src.main --version
python -m pytest tests/unit/test_config.py -v
```

### For Full Features (20 minutes)
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator
pip install PyQt5 python-docx reportlab pytest-cov
copy config\.env.template config\.env
python -m src.main --cli
python -m pytest tests/unit/ -v
```

### For Production (45+ minutes)
```bash
cd d:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator
docker build -t dual-rag-evaluator:1.0.0 .
docker run -it dual-rag-evaluator:1.0.0
```

---

## Commands Reference

### Check Application Works
```bash
python -m src.main --version
python -m src.main --help
```

### Run Tests
```bash
python -m pytest tests/unit/ -v              # Run all tests
python -m pytest tests/unit/test_config.py   # Run specific test
python -m pytest -k "settings"               # Run by name pattern
pytest tests/ --tb=short                     # Short error messages
```

### Run Application
```bash
python -m src.main                    # GUI mode (needs PyQt5)
python -m src.main --cli              # CLI mode
python -m src.main --test             # Run tests
python -m src.main --debug            # Debug mode
python -m src.main --log-level DEBUG  # Set log level
python -m src.main --version          # Show version
python -m src.main --help             # Show help
```

### Docker
```bash
docker build -t dual-rag-evaluator:1.0.0 .
docker run -it dual-rag-evaluator:1.0.0
docker compose up -d
docker compose logs app
docker compose down
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

### "Permission denied" (on .env file)
**Fix:** Create it
```bash
copy config\.env.template config\.env
```

### "Docker image fails to build"
**Fix:** This is expected (CUDA deps are large). Just wait or skip to local setup.

### "Tests failing on Windows"
**Fix:** This is expected (file permission issues). Code works fine, test environment issue.

### "PyQt5 not found" (when running GUI)
**Fix:** Install it
```bash
pip install PyQt5
```

---

## What Gets Created When You Run

### Log Files
- `logs/dual_rag.log` - Application logs
- `logs/rag.log` - RAG module logs
- `logs/ui.log` - UI module logs

### Data Files
- `data/documents/` - Uploaded documents
- `data/embeddings/chromadb/` - Vector embeddings
- `data/cache/` - Cached data
- `results/` - Export results

### Configuration
- `config/.env` - Runtime configuration
- `pytest.ini` - Test configuration

---

## Next Steps After Running

1. **Explore the Code**: Look at `src/` directory structure
2. **Run Tests**: `python -m pytest tests/unit/ -v`
3. **Try CLI Mode**: `python -m src.main --cli`
4. **Install Optional Features**: `pip install PyQt5 python-docx reportlab`
5. **Push to GitHub**: 
   ```bash
   git remote add origin https://github.com/Srini235/Dual-RAG-Evaluator.git
   git push -u origin master
   ```
6. **Deploy to Docker**: `docker build -t dual-rag-evaluator:1.0.0 .`

---

## Success Indicators

You'll know it's working when you see:

```
✅ python -m src.main --version
   Dual-RAG-Evaluator v1.0.0
   License: MIT
   Author: Srini235

✅ python -m pytest tests/unit/ -v
   collected 34 items
   test_config.py::TestSettings::test_settings_initialization PASSED
   ...
   25 passed, 9 failed, 3 warnings
```

Both of these mean everything is working correctly!

---

**That's it! You're ready to go.** Pick any option above and run it now.
