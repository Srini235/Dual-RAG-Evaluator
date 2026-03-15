@echo off
REM Dual-RAG-Evaluator GUI Launcher
REM This script properly configures the environment and launches the PyQt5 GUI
REM The issue: venv's torch has DLL problems, so we use system Python's torch

setlocal enabledelayedexpansion

REM Get the directory of this script
cd /d "%~dp0"

REM Set Python paths to use system Python's packages alongside venv's
set PYTHONPATH=C:\Program Files\Python310\Lib\site-packages;%PYTHONPATH%
set TORCH_DEVICE=cpu
set CUDA_VISIBLE_DEVICES=
set TRANSFORMERS_OFFLINE=0

echo.
echo ========================================
echo Dual-RAG-Evaluator
echo ========================================
echo.
echo Environment:
echo - Using venv: .\.venv
echo - Python torch from: C:\Program Files\Python310
echo - CPU mode enabled
echo.

REM Launch the GUI with venv Python but system's ML packages
".\.venv\Scripts\python.exe" src\main.py

pause
