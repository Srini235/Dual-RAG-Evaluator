#!/bin/bash

# Dual-RAG-Evaluator Setup Script for Unix/Linux/macOS

set -e

echo "============================================"
echo "Dual-RAG-Evaluator Setup Script"
echo "============================================"
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "ERROR: Python 3.10 or higher is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip, setuptools, and wheel
echo ""
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies (optional)
read -p "Install development tools (pytest, black, mypy)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip install -e ".[dev,docs]"
fi

# Create .env file from template
echo ""
echo "Setting up configuration..."
if [ ! -f "config/.env" ]; then
    cp config/.env.template config/.env
    echo "Created config/.env from template"
    echo "IMPORTANT: Edit config/.env with your settings!"
else
    echo "config/.env already exists"
fi

# Create necessary directories
echo ""
echo "Creating data directories..."
mkdir -p data/documents
mkdir -p data/embeddings
mkdir -p data/cache
mkdir -p results
echo "Data directories created"

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Edit configuration file:"
echo "   nano config/.env"
echo ""
echo "3. Run the application:"
echo "   python -m src.ui.main_window"
echo ""
echo "4. Run tests (optional):"
echo "   pytest tests/ -v"
echo ""
echo "For more information, see README.md"
echo ""
