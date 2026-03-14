# Contributing to Dual-RAG-Evaluator

First off, thank you for considering contributing to Dual-RAG-Evaluator! It's people like you that help make this project an amazing tool for evaluating RAG systems.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps that reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed**
- **Explain what behavior you expected**
- **Include screenshots or GIFs if possible**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior**
- **Describe the proposed behavior**
- **List some other similar projects if applicable**

### Pull Requests

- Fill in the required template
- Follow the Python/PEP 8 style guide
- Document new code with docstrings
- Add tests for new functionality
- Update relevant documentation
- End all files with a newline

## Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/Dual-RAG-Evaluator.git
   cd Dual-RAG-Evaluator
   ```

2. **Create a new branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Make your changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Follow the existing code style

5. **Test your changes**
   ```bash
   pytest tests/ -v
   black src/  # Format code
   flake8 src/  # Lint code
   mypy src/   # Type checking
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   git push origin feature/your-feature-name
   ```

7. **Submit a Pull Request**
   - Reference related issues
   - Provide detailed description
   - Include before/after screenshots if UI changes
   - Wait for review and address feedback

## Style Guide

### Python Code Style (PEP 8)

- Use 4 spaces for indentation
- Keep lines under 100 characters
- Use meaningful variable names
- Write docstrings for all functions

```python
def process_document(filepath: str, chunk_size: int = 500) -> List[str]:
    """
    Process a document and return text chunks.
    
    Args:
        filepath: Path to the document
        chunk_size: Size of each text chunk
        
    Returns:
        List of text chunks
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If chunk_size is invalid
    """
    pass
```

### Commit Message Style

- Use clear, descriptive titles
- Use imperative mood ("add feature" not "added feature")
- Reference issues: "Fixes #123"
- Keep first line under 50 characters

```
Add negation detection to RAG pipeline (50 chars max)

Implement explicit negation word detection for ChromaDB
and ResonanceDB comparison. Adds phase-based inversion
for better semantic handling of negative queries.

Fixes #123
```

## Testing Guidelines

- Write tests for new functionality
- Maintain minimum 80% code coverage
- Use descriptive test names
- Include both positive and negative test cases

```python
def test_negation_detection():
    """Test that negation words are correctly detected."""
    detector = NegationDetector()
    assert detector.detect("never diabetes") == True
    assert detector.detect("diabetes") == False
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all functions
- Update API documentation
- Include examples for complex features

## Questions?

- Open a GitHub Issue
- Check existing documentation
- Review similar pull requests

---

Thank you for contributing! 🎉
