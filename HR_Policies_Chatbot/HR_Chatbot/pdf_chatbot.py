import os
import sys
from langchain_classic.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_classic.chains import LLMChain
from langchain_classic.prompts import PromptTemplate
from langchain_classic.vectorstores import FAISS
from config import (
    PDF_PATH,
    OPENAI_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    CHROMA_DB_DIR,
    COLLECTION_NAME,
)


class PDFChatbot:
    def __init__(self):
        """Initialize the PDF Chatbot with RAG pipeline."""
        self.pdf_path = PDF_PATH
        self.chroma_db_dir = CHROMA_DB_DIR
        self.collection_name = COLLECTION_NAME
        self.embeddings = None
        self.vector_store = None
        self.retriever = None  # For manual document retrieval
        self.qa_chain = None
        self.llm = None
        self.conversation_history = []  # Store chat history for context

    def load_pdf(self):
        """Load and process PDF document."""
        print(f"Loading PDF from: {self.pdf_path}")
        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from PDF")
        return documents

    def split_documents(self, documents):
        """Split documents into manageable chunks."""
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} text chunks")
        return chunks

    def create_vector_store(self, chunks):
        """Create vector store from document chunks using FAISS."""
        print("Creating vector store with OpenAI embeddings...")
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=self.embeddings,
        )
        
        # Save to disk
        self.vector_store.save_local(self.chroma_db_dir)
        print("Vector store created and saved")

    def setup_qa_chain(self):
        """Setup the QA chain with retrieval."""
        print("Setting up QA chain...")
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
        )

        # Create retriever for manual document retrieval
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

        # Custom prompt for HR context with extreme specificity and logical deduction
        prompt_template = """You are a precise HR assistant. Your job is to answer questions about HR policies based on the handbook.

CRITICAL: FOLLOW-UP QUESTION DETECTION
=========================================
If the previous conversation is available (look below), check if the current question is a DIRECT FOLLOW-UP:
- Previous: "What is bereavement leave?"  Current: "Can probation get it?" → YES, direct follow-up
- Previous: "Is mediclaim for all employees?" Current: "Does this include probation?" → YES, direct follow-up
- Previous: "What is X?" Current: "What about Y?" → NO, new topic

IF THIS IS A DIRECT FOLLOW-UP:
- Use the previous answer as the PRIMARY source of truth
- Apply logical deductions from the previous answer
- DO NOT search for new unrelated policies
- Reference what was already stated

ABSOLUTE RULES FOR ALL ANSWERS:
1. Use ONLY the text provided in the context - nothing else
2. Quote exact wording when stating policies
3. Make LOGICAL DEDUCTIONS from explicit policy statements:
   - If policy says "Upon confirmation of employment", then probation employees are NOT eligible
   - If policy says "all employees" or "everyone", then it includes probation employees
   - If a policy explicitly restricts to certain employee types, follow that restriction
4. For FOLLOW-UP questions: Always reference the previous answer and apply logic to it
5. Do NOT combine unrelated information from different sections
6. Do NOT answer about unrelated policies if this is a direct follow-up
7. If you are uncertain or if the context is ambiguous, say: "The handbook is unclear on this point"
8. If information is not in the context, say: "This information is not available in the handbook"

FOLLOW-UP EXAMPLE:
- Previous Q&A: "Is mediclaim for all?" → "Yes, for all employees"
- Current Q: "Does this include probation?"
- CORRECT: "Yes, since mediclaim is available to 'all employees', probation employees are included."
- WRONG: "Harassment policy applies to all employees of all categories..."

Previous conversation (if any):
{history}

Context from Handbook:
{context}

Current Question: {question}

Answer based on the handbook. If this is a follow-up question, reference the previous answer. Make logical deductions from explicit statements:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question", "history"],
        )

        # Create LLMChain for flexible variable handling
        self.qa_chain = LLMChain(llm=self.llm, prompt=PROMPT)
        print("QA chain setup complete")

    def initialize(self):
        """Initialize the chatbot by loading PDF and setting up RAG."""
        try:
            documents = self.load_pdf()
            chunks = self.split_documents(documents)
            self.create_vector_store(chunks)
            self.setup_qa_chain()
            print("\n✓ Chatbot initialized successfully!\n")
            return True
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            return False

    def _is_probation_eligibility_question(self, question):
        lower = question.lower()
        if "probation" not in lower and "probationary" not in lower and "confirmation" not in lower:
            return False
        return any(term in lower for term in ["eligible", "include", "covered", "can", "does", "is", "are", "what about"])

    def _deduce_answer_from_history(self, question):
        if not self.conversation_history:
            return None

        if not self._is_probation_eligibility_question(question):
            return None

        # Check the most recent answers for explicit eligibility signals
        for _, answer in reversed(self.conversation_history):
            lower_answer = answer.lower()
            if "only after confirmation" in lower_answer:
                return "NO"
            if "after confirmation" in lower_answer and "probation" in lower_answer:
                return "NO"
            if "upon confirmation" in lower_answer:
                return "NO"
            if "not eligible" in lower_answer and "probation" in lower_answer:
                return "NO"
            if "included" in lower_answer and "probation" in lower_answer:
                return "YES"
            if "all employees" in lower_answer or "everyone" in lower_answer:
                return "YES"
        return None

    def answer_question(self, question):
        """Answer a question using the RAG pipeline with conversation history."""
        if not self.qa_chain or not self.retriever:
            print("Chatbot not initialized. Please call initialize() first.")
            return None

        try:
            # Manually retrieve relevant documents
            source_docs = self.retriever.invoke(question)
            
            # Format context from retrieved documents
            context = "\n".join([doc.page_content for doc in source_docs])
            
            # Format conversation history for context
            history_text = ""
            if self.conversation_history:
                history_text = "Previous conversation (use this to answer follow-up questions):\n"
                for i, (q, a) in enumerate(self.conversation_history[-3:], 1):  # Last 3 exchanges
                    # Truncate long answers to avoid confusing the LLM
                    truncated_a = a[:300] + "..." if len(a) > 300 else a
                    history_text += f"{i}. Q: {q}\n   A: {truncated_a}\n\n"
            
            # Attempt deterministic follow-up deduction for probation/confirmation eligibility questions
            deduced_answer = self._deduce_answer_from_history(question)
            if deduced_answer:
                answer = deduced_answer
            else:
                # Call the LLMChain with all required variables
                result = self.qa_chain.invoke({
                    "context": context,
                    "question": question,
                    "history": history_text
                })
                answer = result.get("text", "No answer found")

            # Store in conversation history
            self.conversation_history.append((question, answer))

            response = {
                "answer": answer,
                "sources": [
                    {
                        "page": doc.metadata.get("page", "Unknown"),
                        "content_preview": doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content,
                    }
                    for doc in source_docs
                ],
            }
            return response
        except Exception as e:
            print(f"Error answering question: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def load_existing_vector_store(self):
        """Load existing vector store if available using FAISS."""
        if os.path.exists(self.chroma_db_dir):
            print("Loading existing vector store...")
            self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            self.vector_store = FAISS.load_local(
                self.chroma_db_dir,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.setup_qa_chain()
            print("Vector store loaded successfully!")
            return True
        return False


if __name__ == "__main__":
    chatbot = PDFChatbot()

    # Try to load existing vector store, if not, initialize from PDF
    if not chatbot.load_existing_vector_store():
        if not chatbot.initialize():
            sys.exit(1)

    # Interactive Q&A loop
    print("=" * 60)
    print("HR POLICIES CHATBOT")
    print("=" * 60)
    print("Ask questions about HR policies, leaves, holidays, etc.")
    print("Type 'quit' or 'exit' to end the conversation.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in ["quit", "exit"]:
            print("Thank you for using HR Chatbot. Goodbye!")
            break

        if not question:
            print("Please enter a question.\n")
            continue

        response = chatbot.answer_question(question)

        if response:
            print("\nChatbot:", response["answer"])
            if response["sources"]:
                # Get unique page numbers
                page_numbers = set(source['page'] for source in response["sources"])
                page_list = ", ".join(str(p) for p in sorted(page_numbers))
                print(f"\nSource: Page {page_list}")
            print()
