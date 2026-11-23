import streamlit as st
from pdf_chatbot import PDFChatbot
import os

# Page configuration
st.set_page_config(
    page_title="HR Policies Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with improved styling
st.markdown(
    """
    <style>
    .chatbot-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .question-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    .answer-box {
        background-color: #e8f5e9;
        padding: 12px 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #4caf50;
        color: #1b5e20;
    }
    .source-box {
        background-color: #f5f5f5;
        padding: 10px;
        border-left: 4px solid #2196F3;
        margin: 5px 0;
        border-radius: 4px;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and Header
st.title("🤖 HR Policies Chatbot")
st.markdown(
    "Get instant answers to your questions about HR policies, leaves, holidays, and more!"
)

# Initialize session state
if "chatbot" not in st.session_state:
    with st.spinner("Initializing chatbot..."):
        st.session_state.chatbot = PDFChatbot()
        # Try to load existing vector store, if not, initialize from PDF
        if not st.session_state.chatbot.load_existing_vector_store():
            if not st.session_state.chatbot.initialize():
                st.error("Failed to initialize chatbot. Please check your configuration.")
                st.stop()
    st.success("✓ Chatbot ready!")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
st.markdown("### Conversation")
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="question-box"><b>You:</b> {message["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="answer-box"><b>Chatbot:</b> {message["content"]}</div>',
                unsafe_allow_html=True,
            )
            if "sources" in message and message["sources"]:
                # Get unique page numbers
                page_numbers = set(source["page"] for source in message["sources"])
                page_list = ", ".join(str(p) for p in sorted(page_numbers))
                st.markdown(
                    f'<div class="source-box"><b>Source:</b> Page {page_list}</div>',
                    unsafe_allow_html=True,
                )

# Input area
st.markdown("---")

def process_question():
    """Callback to process the question and handle chatbot response."""
    user_input = st.session_state.user_input_field
    if user_input.strip():
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get response from chatbot
        with st.spinner("Thinking..."):
            response = st.session_state.chatbot.answer_question(user_input)

        if response:
            # Add chatbot response to history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response["answer"],
                    "sources": response["sources"],
                }
            )
        
        # Clear the input field after processing
        st.session_state.user_input_field = ""

col1, col2 = st.columns([0.85, 0.15])

with col1:
    st.text_input(
        "Ask a question about HR policies:",
        placeholder="e.g., What is the bereavement leave policy?",
        label_visibility="collapsed",
        key="user_input_field",
        on_change=process_question,
    )

with col2:
    st.button("Send ➤", use_container_width=True, type="primary", on_click=process_question)

# Sidebar with information and controls
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown(
        """
    This chatbot is powered by AI and uses the Employee Handbook PDF to answer your questions.
    
    **Features:**
    - 🔍 Semantic search through HR documents
    - 📚 Source citations for transparency
    - 💬 Natural conversation interface
    - ✨ Specific and focused answers
    
    **Topics covered:**
    - HR Policies
    - Leave Management
    - Holidays
    - Employee Guidelines
    - And more!
    """
    )

    st.markdown("---")
    
    # Chat controls
    st.subheader("🎮 Chat Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Bot", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    st.markdown("---")
    st.markdown("**Powered by LangChain & OpenAI**")
    st.markdown("Employee Handbook PDF: HR Policies Chatbot")

