@echo off
echo ========================================
echo HR Policies Chatbot - Setup
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)

echo.
echo Step 1: Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo.
echo Step 2: Installing dependencies...
python -m pip install --upgrade pip
python -m pip install --only-binary=:all: -r requirements.txt
if errorlevel 1 (
    echo Warning: Binary installation had issues, trying with build tools...
    python -m pip install -r requirements.txt
)

echo.
echo Step 3: Configuration...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Edit .env file and add your OpenAI API Key!
    echo You can get it from https://platform.openai.com/api-keys
    echo.
    pause
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the chatbot:
echo.
echo Option 1 - Command Line Interface:
echo   python pdf_chatbot.py
echo.
echo Option 2 - Web Interface (Streamlit):
echo   streamlit run streamlit_app.py
echo.
pause
