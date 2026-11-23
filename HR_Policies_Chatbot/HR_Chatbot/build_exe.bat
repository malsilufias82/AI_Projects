@echo off
REM Build script for HR Policies Chatbot .exe

echo.
echo ========================================
echo HR Policies Chatbot - EXE Builder
echo ========================================
echo.

REM Check if venv is activated
if "%VIRTUAL_ENV%"=="" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install PyInstaller if not already installed
echo Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install -q pyinstaller
) else (
    echo PyInstaller is already installed
)

echo.
echo Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist HR_Chatbot.spec del HR_Chatbot.spec

echo.
echo Building executable...
echo This may take a few minutes...
echo.

REM Build the executable with simplified options
pyinstaller --onedir --windowed --name HR_Chatbot ^
    --add-data "chroma_db;chroma_db" ^
    --hidden-import=langchain ^
    --hidden-import=langchain_openai ^
    --hidden-import=langchain_classic ^
    --hidden-import=langchain_text_splitters ^
    --hidden-import=faiss ^
    --hidden-import=pypdf ^
    --hidden-import=dotenv ^
    chatbot_gui.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✓ Build successful!
    echo ========================================
    echo.
    echo Executable created at: dist\HR_Chatbot\HR_Chatbot.exe
    echo.
    echo You can now run the chatbot from:
    echo   dist\HR_Chatbot\HR_Chatbot.exe
    echo.
    echo To create a portable version, copy the entire 'dist\HR_Chatbot' folder
    echo to any location on your computer.
    echo.
    pause
) else (
    echo.
    echo ✗ Build failed!
    echo.
    pause
)

