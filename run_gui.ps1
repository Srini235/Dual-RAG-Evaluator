# Dual-RAG-Evaluator GUI Launcher for PowerShell
# Sets up environment to use system Python's working torch installation

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Dual-RAG-Evaluator - GUI Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for torch and transformers
$env:PYTHONPATH = "C:\Program Files\Python310\Lib\site-packages"
$env:TORCH_DEVICE = "cpu"
$env:CUDA_VISIBLE_DEVICES = ""
$env:TRANSFORMERS_OFFLINE = "0"

Write-Host "Environment configured:" -ForegroundColor Green
Write-Host "- venv: .\.venv"  
Write-Host "- System torch from: C:\Program Files\Python310"
Write-Host "- Mode: CPU"
Write-Host ""

# Launch the GUI
Write-Host "Launching GUI..." -ForegroundColor Yellow
& "D:\07_SelfStudy\docker_app\workspace\.venv\Scripts\python.exe" "D:\07_SelfStudy\docker_app\workspace\Dual-RAG-Evaluator\src\main.py"
