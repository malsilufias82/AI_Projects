# Quick Start Guide for HR Policies Chatbot

## 🚀 Quick Start (5 minutes)

### Step 1: Setup
**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
bash setup.sh
chmod +x setup.sh
```

Or **Manual Setup:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Step 2: Configure
1. Open `.env` file
2. Add your OpenAI API Key from https://platform.openai.com/api-keys
3. Verify PDF path is correct: `C:\Saif\FromVLink\Employee Handbook.pdf`

### Step 3: Run

**Choose your interface:**

**Option A - CLI (Command Line)**
```bash
python pdf_chatbot.py
```
Then type your questions:
```
You: What is the annual leave policy?
You: How many holidays are in 2026?
You: quit
```

**Option B - Web UI (Streamlit)**
```bash
streamlit run streamlit_app.py
```
Opens at http://localhost:8501

---

## 📋 Sample Questions

Try asking:
- "What is the leave policy?"
- "How many days of leave do I get?"
- "What are the public holidays?"
- "What is the work from home policy?"
- "How do I apply for leave?"
- "What benefits are available?"
- "What is the sick leave policy?"

---

## 🔧 Troubleshooting

### Error: "OPENAI_API_KEY not set"
→ Make sure `.env` file exists and has your API key

### Error: "PDF file not found"
→ Check the PDF path in `.env` is correct

### Slow first run
→ Normal! First run creates the vector database. Next runs are faster.

### No internet connection
→ This chatbot requires internet (calls OpenAI API)

---

## 💡 Tips

1. **First-time takes longer** - Embeddings are created and cached
2. **Rephrase questions** - If answer seems off, try different wording
3. **Check sources** - Review cited pages for context
4. **Use Web UI** - Streamlit app is more user-friendly for interactive use

---

## 📚 File Descriptions

| File | Purpose |
|------|---------|
| `pdf_chatbot.py` | Core chatbot logic and RAG pipeline |
| `streamlit_app.py` | Web interface |
| `config.py` | Configuration settings |
| `.env` | Your secrets (API key, paths) |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |

---

## 🎓 How It Works

```
User Question
     ↓
Vectorize Question
     ↓
Search Vector Database
     ↓
Retrieve Relevant Pages
     ↓
Pass to LLM with Context
     ↓
Generate Answer
     ↓
Show Answer + Sources
```

No code tools needed - pure RAG!

---

## 🆘 Need Help?

1. Check README.md for detailed docs
2. Review config.py for all settings
3. Test with simple questions first
4. Check OpenAI API is working

---

**Ready to chat? Run the setup and start asking questions!** 🤖
