# How It Works: RAG Pipeline

1️⃣ PDF Loading: Employee Handbook loaded and parsed

2️⃣ Text Chunking: Document split into 1000-char chunks

3️⃣ Embeddings: Text converted to vector embeddings (OpenAI)

4️⃣ Vector Store: Embeddings stored in FAISS database

5️⃣ Retrieval: When user asks, top 5 relevant chunks retrieved

6️⃣ Generation: LLM generates answer using retrieved context

# System Architecture

**Frontend:**

&nbsp;&nbsp;&nbsp;• CLI Interface
   
&nbsp;&nbsp;&nbsp;• Streamlit Web App
   
&nbsp;&nbsp;&nbsp;• Tkinter Desktop GUI


**Backend:**

&nbsp;&nbsp;&nbsp;• LangChain Framework
   
&nbsp;&nbsp;&nbsp;• OpenAI LLM (GPT-3.5)
   
&nbsp;&nbsp;&nbsp;• FAISS Vector Store


**Data Pipeline:**

&nbsp;&nbsp;&nbsp;• PyPDF: Load handbook
   
&nbsp;&nbsp;&nbsp;• RecursiveTextSplitter
   
&nbsp;&nbsp;&nbsp;• OpenAI Embeddings
   
&nbsp;&nbsp;&nbsp;• FAISS Index


**Key Features:**

&nbsp;&nbsp;&nbsp;• Conversation history
   
&nbsp;&nbsp;&nbsp;• Source citations
   
&nbsp;&nbsp;&nbsp;• Follow-up handling


# Technology Stack
**LLM & Embeddings:**

&nbsp;&nbsp;&nbsp;• OpenAI GPT-3.5-turbo

&nbsp;&nbsp;&nbsp;• OpenAI Embeddings API


**Python Libraries:**

&nbsp;&nbsp;&nbsp;• LangChain (orchestration)

&nbsp;&nbsp;&nbsp;• PyPDF (document loading)


**Frontend Frameworks:**

&nbsp;&nbsp;&nbsp;• Streamlit (web UI)

&nbsp;&nbsp;&nbsp;• Tkinter (desktop GUI)


**Development Tools:**

&nbsp;&nbsp;&nbsp;• Python 3.8+
   
&nbsp;&nbsp;&nbsp;• PyInstaller (exe build)
   
&nbsp;&nbsp;&nbsp;• Virtual environment


**Deployment:**

&nbsp;&nbsp;&nbsp;• Windows executables

&nbsp;&nbsp;&nbsp;• No external dependencies


# Setup & Installation
**Prerequisites: Python 3.8+, OpenAI API Key**

1️⃣ Clone/setup project directory

2️⃣ Create virtual environment: python -m venv venv

3️⃣ Activate: venv\Scripts\activate

4️⃣ Install dependencies: pip install -r requirements.txt

5️⃣ Configure .env file with OpenAI API key and PDF path

6️⃣ Run your preferred interface (CLI, Web, or Desktop)


# Troubleshooting & Maintenance
**❌ Issue: Incorrect answers?**

&nbsp;&nbsp;&nbsp;✓ Rebuild vector store: Remove chroma_db folder


**❌ Issue: API key errors?**

&nbsp;&nbsp;&nbsp;✓ Check .env file configuration

&nbsp;&nbsp;&nbsp;✓ Verify OpenAI API key is valid


**❌ Issue: PDF not loading?**

&nbsp;&nbsp;&nbsp;✓ Ensure PDF path in config.py is correct

&nbsp;&nbsp;&nbsp;✓ Check file exists and readable


**❌ Issue: Slow responses?**

&nbsp;&nbsp;&nbsp;✓ Check internet connection (API calls)

&nbsp;&nbsp;&nbsp;✓ Reduce retrieval context (k parameter)


# Summary & Next Steps
**✅ Summary:**

&nbsp;&nbsp;&nbsp;• AI-powered RAG chatbot for HR policies

&nbsp;&nbsp;&nbsp;• Multiple interfaces (CLI, Web, Desktop)

&nbsp;&nbsp;&nbsp;• Accurate, source-backed answers


**📋 Next Steps:**

1️⃣ Configure OpenAI API key

2️⃣ Test with employee handbook

3️⃣ Deploy to target environment

4️⃣ Gather user feedback

5️⃣ Iterate and improve