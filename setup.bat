@echo off
REM Dual-RAG-Evaluator Setup Script for Windows

setlocal enabledelayedexpansion

echo ============================================
echo Dual-RAG-Evaluator Setup Script
echo ============================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    exit /b 1
)

python --version
echo.

REM Verify Python 3.10+
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.10 or higher is required
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip, setuptools, and wheel
echo.
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Install development dependencies (optional)
setlocal
echo.
set /p DEV_INSTALL="Install development tools (pytest, black, mypy)? (y/n) "
if /i "!DEV_INSTALL!"=="y" (
    echo Installing development dependencies...
    pip install -e ".[dev,docs]"
)
endlocal

REM Create .env file from template
echo.
echo Setting up configuration...
if not exist "config\.env" (
    copy config\.env.template config\.env
    echo Created config\.env from template
    echo IMPORTANT: Edit config\.env with your settings!
) else (
    echo config\.env already exists
)

REM Create necessary directories
echo.
echo Creating data directories...
if not exist "data\documents" mkdir data\documents
if not exist "data\embeddings" mkdir data\embeddings
if not exist "data\cache" mkdir data\cache
if not exist "results" mkdir results
echo Data directories created

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Edit configuration file:
echo    notepad config\.env
echo.
echo 3. Run the application:
echo    python -m src.ui.main_window
echo.
echo 4. Run tests ^(optional^):
echo    pytest tests\ -v
echo.
echo For more information, see README.md
echo.
pause
