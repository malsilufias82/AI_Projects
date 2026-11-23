#!/bin/bash

echo "========================================"
echo "HR Policies Chatbot - Setup"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "Step 2: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Step 3: Configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Edit .env file and add your OpenAI API Key!"
    echo "You can get it from https://platform.openai.com/api-keys"
    echo ""
else
    echo ".env file already exists"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the chatbot:"
echo ""
echo "Option 1 - Command Line Interface:"
echo "   python pdf_chatbot.py"
echo ""
echo "Option 2 - Web Interface (Streamlit):"
echo "   streamlit run streamlit_app.py"
echo ""
