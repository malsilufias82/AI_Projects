import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("PDFCHATBOT_API_KEY") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))

# PDF Configuration
PDF_PATH = os.getenv("PDF_PATH", r"C:\Saif\FromVLink\Employee Handbook.pdf")

# ChromaDB Configuration
CHROMA_DB_DIR = "./chroma_db"
COLLECTION_NAME = "hr_policies"

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY or PDFCHATBOT_API_KEY not set. Please set it in .env file")

if not os.path.exists(PDF_PATH):
    raise ValueError(f"PDF file not found at {PDF_PATH}")
