@echo off
REM Launcher for HR Policies Chatbot Desktop Application

echo.
echo ========================================
echo HR Policies Chatbot - Desktop App
echo ========================================
echo.

REM Activate virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the GUI
echo Starting application...
python chatbot_gui.py

pause
