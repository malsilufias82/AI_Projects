# HR Policies PDF Chatbot

A powerful AI-powered chatbot that answers HR-related questions by retrieving information from the Employee Handbook PDF using Retrieval-Augmented Generation (RAG).

## Features

✨ **No Code Tools Required** - The chatbot doesn't use external tools/functions, it purely uses RAG
🤖 **AI-Powered Q&A** - Natural language understanding for HR queries
📄 **PDF-Based Knowledge** - Learns from Employee Handbook PDF
🔍 **Semantic Search** - Finds relevant information intelligently
📝 **Source Citations** - Shows which pages information came from
💬 **Multiple Interfaces** - CLI and Web-based (Streamlit) options

## Technologies Used

- **LangChain** - Framework for building RAG applications
- **ChromaDB** - Vector database for semantic search
- **OpenAI** - LLM and embeddings API
- **Streamlit** - Web interface for easy interaction
- **PyPDF** - PDF document loading

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API Key
- Employee Handbook PDF file

### Setup Steps

1. **Clone or create the project directory:**
   ```bash
   cd c:\Saif\MyDevelopment
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your OpenAI API Key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     PDF_PATH=C:\Saif\FromVLink\Employee Handbook.pdf
     ```

## Usage

### Option 1: Command Line Interface (CLI)

Run the interactive CLI chatbot:

```bash
python pdf_chatbot.py
```

Then type your questions about HR policies, leaves, holidays, etc.

Example interactions:
```
You: What is the leave policy?
Chatbot: [Detailed answer about leave policy with sources]

You: How many holidays are there in 2026?
Chatbot: [Information about holidays from the handbook]

You: quit
```

### Option 2: Web Interface (Streamlit)

Run the web-based interface:

```bash
streamlit run streamlit_app.py
```

The app will open in your default browser at `http://localhost:8501`

Features:
- Clean, intuitive chat interface
- Chat history maintained during session
- Source citations with expandable details
- Real-time responses
- Mobile-friendly design

## How It Works

1. **PDF Loading** - Reads the Employee Handbook PDF
2. **Text Chunking** - Splits document into meaningful chunks
3. **Embeddings** - Converts text to vector embeddings using OpenAI
4. **Vector Store** - Stores embeddings in ChromaDB for fast retrieval
5. **Question Processing** - When you ask a question:
   - Converts your question to embeddings
   - Searches for most relevant document chunks
   - Passes context to LLM with your question
   - LLM generates answer based on context
   - Returns answer with source references

## Project Structure

```
c:\Saif\MyDevelopment\
├── requirements.txt          # Python dependencies
├── config.py                # Configuration settings
├── pdf_chatbot.py           # Core chatbot logic
├── streamlit_app.py         # Web interface
├── .env.example             # Environment variables template
├── .env                     # Your actual environment variables (create this)
├── chroma_db/               # Vector store (auto-created)
└── README.md                # This file
```

## Configuration

Edit `config.py` or `.env` to customize:

- **OPENAI_API_KEY** - Your OpenAI API key
- **MODEL_NAME** - LLM model (default: gpt-3.5-turbo)
- **TEMPERATURE** - Response creativity (0-1, default: 0.7)
- **PDF_PATH** - Path to your PDF file
- **CHROMA_DB_DIR** - Vector store location

## Getting an OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key and add it to your `.env` file

## Troubleshooting

### "OPENAI_API_KEY not set"
- Make sure you created a `.env` file
- Check that your API key is correct and not expired

### "PDF file not found"
- Verify the PDF path in `.env` is correct
- Check that the file exists at that location

### Slow response times
- First run creates vector store - this is normal
- Subsequent runs will be faster as it uses cached embeddings

### Low quality answers
- Try rephrasing your question
- Check that relevant information exists in the PDF
- Adjust temperature in config for different response styles

## Advanced Usage

### Reset Vector Store

Delete the `chroma_db` folder to force re-creation of the vector store:

```bash
rmdir /s chroma_db
```

Then run the chatbot again - it will rebuild from the PDF.

### Add More PDFs

To include additional PDFs (e.g., Holidays 2026.pdf), modify the PDF loading section in `pdf_chatbot.py`:

```python
def load_pdf(self):
    documents = []
    for pdf_file in [self.pdf_path, "path/to/other.pdf"]:
        loader = PyPDFLoader(pdf_file)
        documents.extend(loader.load())
    return documents
```

## Limitations

- Requires internet connection (calls OpenAI API)
- API costs apply based on token usage
- Answers are only as good as the PDF content
- No persistent memory between sessions (unless using database)

## Future Enhancements

- [ ] Multi-PDF support
- [ ] Chat history persistence
- [ ] Local LLM option (Ollama/LLaMA)
- [ ] Custom fine-tuning
- [ ] Document upload UI
- [ ] Analytics and usage tracking

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify your `.env` configuration
3. Test with a simple question first
4. Check OpenAI API status

## License

This project uses OpenAI's API. Please review OpenAI's terms of service.

---

**Ready to get started?** Run `python pdf_chatbot.py` for the CLI or `streamlit run streamlit_app.py` for the web interface!
