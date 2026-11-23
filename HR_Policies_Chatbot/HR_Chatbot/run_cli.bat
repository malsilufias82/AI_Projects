@echo off
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -q -r requirements.txt
python pdf_chatbot.py
pause
