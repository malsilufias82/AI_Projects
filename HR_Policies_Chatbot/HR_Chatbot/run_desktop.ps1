# Launcher for HR Policies Chatbot Desktop Application (PowerShell version)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HR Policies Chatbot - Desktop App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if not already
if ($env:VIRTUAL_ENV -eq "") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Run the GUI
Write-Host "Starting application..." -ForegroundColor Yellow
Write-Host ""

python chatbot_gui.py
