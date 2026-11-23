# Build script for HR Policies Chatbot .exe (PowerShell version)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HR Policies Chatbot - EXE Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv is activated
if ($env:VIRTUAL_ENV -eq "") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Install PyInstaller if not already installed
Write-Host "Checking for PyInstaller..." -ForegroundColor Yellow
$pyinstaller = pip show pyinstaller 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install -q pyinstaller
} else {
    Write-Host "PyInstaller is already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Cleaning old build files..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "HR_Chatbot.spec") { Remove-Item "HR_Chatbot.spec" -Force }

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

# Build the executable with simplified options
$pyinstallerArgs = @(
    "--onedir",
    "--windowed",
    "--name", "HR_Chatbot",
    "--add-data", "chroma_db;chroma_db",
    "--hidden-import=langchain",
    "--hidden-import=langchain_openai",
    "--hidden-import=langchain_classic",
    "--hidden-import=langchain_text_splitters",
    "--hidden-import=faiss",
    "--hidden-import=pypdf",
    "--hidden-import=dotenv",
    "chatbot_gui.py"
)

& pyinstaller $pyinstallerArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Build successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable created at: dist\HR_Chatbot\HR_Chatbot.exe" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the chatbot from:" -ForegroundColor Cyan
    Write-Host "  dist\HR_Chatbot\HR_Chatbot.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "To create a portable version, copy the entire 'dist\HR_Chatbot' folder" -ForegroundColor Cyan
    Write-Host "to any location on your computer." -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Press Enter to continue"

