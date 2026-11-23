#!/usr/bin/env python3
"""
Generate a comprehensive PowerPoint presentation for the HR Chatbot project
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from datetime import datetime

def create_presentation():
    """Create a comprehensive HR Chatbot presentation"""
    
    # Create presentation
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)
    
    # Define color scheme
    PRIMARY_COLOR = RGBColor(102, 126, 234)  # Purple/Blue
    SECONDARY_COLOR = RGBColor(118, 75, 162)  # Dark Purple
    ACCENT_COLOR = RGBColor(76, 175, 80)  # Green
    DARK_TEXT = RGBColor(33, 33, 33)  # Dark Gray
    LIGHT_BG = RGBColor(245, 245, 245)  # Light Gray
    
    def add_title_slide(title, subtitle=""):
        """Add a title slide"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = PRIMARY_COLOR
        
        # Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(9), Inches(2))
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(54)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_para.alignment = PP_ALIGN.CENTER
        
        # Subtitle
        if subtitle:
            subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(9), Inches(1.5))
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.word_wrap = True
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.text = subtitle
            subtitle_para.font.size = Pt(28)
            subtitle_para.font.color.rgb = RGBColor(200, 200, 255)
            subtitle_para.alignment = PP_ALIGN.CENTER
    
    def add_content_slide(title, content_items, use_bullets=True):
        """Add a content slide with title and bullet points"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)
        
        # Title bar
        title_shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(1))
        title_shape.fill.solid()
        title_shape.fill.fore_color.rgb = PRIMARY_COLOR
        title_shape.line.color.rgb = PRIMARY_COLOR
        
        # Title text
        title_frame = title_shape.text_frame
        title_frame.clear()
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(40)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_frame.margin_bottom = Inches(0.1)
        title_frame.margin_left = Inches(0.3)
        
        # Content
        content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(5.5))
        text_frame = content_box.text_frame
        text_frame.word_wrap = True
        
        for i, item in enumerate(content_items):
            if i > 0:
                text_frame.add_paragraph()
            
            p = text_frame.paragraphs[i]
            
            if use_bullets and isinstance(item, dict):
                p.text = item.get('text', '')
                p.level = item.get('level', 0)
                p.font.size = Pt(18) if item.get('level', 0) == 0 else Pt(16)
            elif use_bullets and isinstance(item, str):
                p.text = item
                p.font.size = Pt(18)
            else:
                p.text = item
                p.font.size = Pt(18)
            
            p.font.color.rgb = DARK_TEXT
            if use_bullets:
                p.level = 0
            p.space_before = Pt(6)
            p.space_after = Pt(6)
    
    def add_two_column_slide(title, left_items, right_items):
        """Add a slide with two columns"""
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        
        # Background
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(255, 255, 255)
        
        # Title bar
        title_shape = slide.shapes.add_shape(1, Inches(0), Inches(0), Inches(10), Inches(1))
        title_shape.fill.solid()
        title_shape.fill.fore_color.rgb = PRIMARY_COLOR
        title_shape.line.color.rgb = PRIMARY_COLOR
        
        title_frame = title_shape.text_frame
        title_frame.clear()
        title_para = title_frame.paragraphs[0]
        title_para.text = title
        title_para.font.size = Pt(40)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 255, 255)
        title_frame.margin_left = Inches(0.3)
        
        # Left column
        left_box = slide.shapes.add_textbox(Inches(0.4), Inches(1.3), Inches(4.5), Inches(5.8))
        left_frame = left_box.text_frame
        left_frame.word_wrap = True
        
        for i, item in enumerate(left_items):
            if i > 0:
                left_frame.add_paragraph()
            p = left_frame.paragraphs[i]
            p.text = item
            p.font.size = Pt(16)
            p.font.color.rgb = DARK_TEXT
            p.space_before = Pt(4)
            p.space_after = Pt(4)
        
        # Right column
        right_box = slide.shapes.add_textbox(Inches(5.1), Inches(1.3), Inches(4.5), Inches(5.8))
        right_frame = right_box.text_frame
        right_frame.word_wrap = True
        
        for i, item in enumerate(right_items):
            if i > 0:
                right_frame.add_paragraph()
            p = right_frame.paragraphs[i]
            p.text = item
            p.font.size = Pt(16)
            p.font.color.rgb = DARK_TEXT
            p.space_before = Pt(4)
            p.space_after = Pt(4)
    
    # SLIDE 1: Title Slide
    add_title_slide(
        "HR Policies Chatbot",
        "AI-Powered RAG Solution for Employee Handbook Q&A"
    )
    
    # SLIDE 2: Project Overview
    add_content_slide(
        "Project Overview",
        [
            "✨ Intelligent HR Assistant using Retrieval-Augmented Generation (RAG)",
            "📄 Answers HR policy questions from Employee Handbook PDF",
            "🤖 Powered by OpenAI GPT and LangChain framework",
            "🔍 Semantic search for accurate information retrieval",
            "💼 Multiple interfaces: CLI, Web (Streamlit), Desktop (Tkinter)",
            "✅ Source citations showing exact handbook pages",
        ]
    )
    
    # SLIDE 3: Problem Statement
    add_content_slide(
        "Problem Statement & Solution",
        [
            "❌ Problem: Employees struggle to find HR policy information",
            "   • Manual handbook searching is time-consuming",
            "   • Information scattered across multiple documents",
            "   • Inconsistent policy interpretations",
            "",
            "✅ Solution: AI-powered chatbot with RAG",
            "   • Instant answers to HR policy questions",
            "   • Source tracking (exact handbook pages)",
            "   • Consistent, policy-based responses",
        ]
    )
    
    # SLIDE 4: How RAG Works
    add_content_slide(
        "How It Works: RAG Pipeline",
        [
            "1️⃣ PDF Loading: Employee Handbook loaded and parsed",
            "2️⃣ Text Chunking: Document split into 1000-char chunks",
            "3️⃣ Embeddings: Text converted to vector embeddings (OpenAI)",
            "4️⃣ Vector Store: Embeddings stored in FAISS database",
            "5️⃣ Retrieval: When user asks, top 5 relevant chunks retrieved",
            "6️⃣ Generation: LLM generates answer using retrieved context",
        ]
    )
    
    # SLIDE 5: Architecture
    add_two_column_slide(
        "System Architecture",
        [
            "Frontend:",
            "• CLI Interface",
            "• Streamlit Web App",
            "• Tkinter Desktop GUI",
            "",
            "Backend:",
            "• LangChain Framework",
            "• OpenAI LLM (GPT-3.5)",
            "• FAISS Vector Store",
        ],
        [
            "Data Pipeline:",
            "• PyPDF: Load handbook",
            "• RecursiveTextSplitter",
            "• OpenAI Embeddings",
            "• FAISS Index",
            "",
            "Key Features:",
            "• Conversation history",
            "• Source citations",
            "• Follow-up handling",
        ]
    )
    
    # SLIDE 6: Features
    add_content_slide(
        "Key Features",
        [
            "🤖 No Code Tools: Pure RAG, no external function calls",
            "💬 Natural Language: Ask questions conversationally",
            "📖 Smart Retrieval: Finds relevant handbook sections",
            "🔗 Source Citations: Shows exact page numbers",
            "📝 Follow-up Context: Remembers previous questions",
            "⚡ Smart Deduction: Makes logical inferences from policies",
            "🖥️ Multiple Interfaces: CLI, Web, Desktop options",
        ]
    )
    
    # SLIDE 7: Interface Options
    add_content_slide(
        "Three User Interfaces",
        [
            "1. CLI (Command Line Interface)",
            "   • python pdf_chatbot.py",
            "   • Direct terminal interaction",
            "",
            "2. Web Interface (Streamlit)",
            "   • streamlit run streamlit_app.py",
            "   • Browser-based at localhost:8501",
            "   • Chat history, source details",
            "",
            "3. Desktop Application (.exe)",
            "   • Standalone Windows executable",
            "   • No Python installation required",
            "   • Tkinter GUI with professional layout",
        ]
    )
    
    # SLIDE 8: Technologies & Stack
    add_two_column_slide(
        "Technology Stack",
        [
            "LLM & Embeddings:",
            "• OpenAI GPT-3.5-turbo",
            "• OpenAI Embeddings API",
            "",
            "Vector Database:",
            "• FAISS (Facebook AI)",
            "• Semantic search engine",
            "",
            "Python Libraries:",
            "• LangChain (orchestration)",
            "• PyPDF (document loading)",
        ],
        [
            "Frontend Frameworks:",
            "• Streamlit (web UI)",
            "• Tkinter (desktop GUI)",
            "",
            "Development Tools:",
            "• Python 3.8+",
            "• PyInstaller (exe build)",
            "• Virtual environment",
            "",
            "Deployment:",
            "• Windows executables",
            "• No external dependencies",
        ]
    )
    
    # SLIDE 9: Setup & Installation
    add_content_slide(
        "Setup & Installation",
        [
            "Prerequisites: Python 3.8+, OpenAI API Key",
            "",
            "1. Clone/setup project directory",
            "2. Create virtual environment: python -m venv venv",
            "3. Activate: venv\\Scripts\\activate",
            "4. Install dependencies: pip install -r requirements.txt",
            "5. Configure .env file with OpenAI API key and PDF path",
            "6. Run your preferred interface (CLI, Web, or Desktop)",
        ]
    )
    
    # SLIDE 10: Usage Examples
    add_content_slide(
        "Usage Examples",
        [
            "Example Q1: 'What is the bereavement leave policy?'",
            "→ Returns specific bereavement leave info with page citation",
            "",
            "Example Q2: 'Is group mediclaim for all employees?'",
            "→ Confirms eligibility based on handbook wording",
            "",
            "Example Q3: 'Can probation employees get mediclaim?'",
            "→ Follow-up detection: applies previous answer logic",
            "",
            "Example Q4: 'How many holidays in 2026?'",
            "→ Retrieves specific holiday count from handbook",
        ]
    )
    
    # SLIDE 11: Accuracy Features
    add_content_slide(
        "Accuracy & Reliability",
        [
            "✅ Strict Prompt Rules:",
            "   • Use ONLY exact text from handbook",
            "   • Quote when stating policies",
            "   • Make logical deductions (not assumptions)",
            "",
            "✅ Smart Follow-up Handling:",
            "   • Detects direct follow-up questions",
            "   • References previous answers",
            "   • Applies logic within context",
            "",
            "✅ Uncertainty Handling:",
            "   • 'The handbook is unclear on this point'",
            "   • 'This information is not available'",
        ]
    )
    
    # SLIDE 12: Building Desktop Executable
    add_content_slide(
        "Building Desktop Application",
        [
            "Transform Python app into standalone .exe:",
            "",
            "Option 1: Using Batch File",
            "   → build_exe.bat",
            "",
            "Option 2: Using PowerShell",
            "   → .\\build_exe.ps1",
            "",
            "Option 3: Manual Build",
            "   → pyinstaller --noconfirm --clean chatbot_gui.spec",
            "",
            "Result: dist/HR_Chatbot.exe (~500MB, fully portable)",
        ]
    )
    
    # SLIDE 13: Deployment
    add_content_slide(
        "Deployment Options",
        [
            "1. Local Desktop: Run .exe from dist folder",
            "",
            "2. Web Server: Host Streamlit app on cloud",
            "",
            "3. Distribution: Share .exe file with other users",
            "   • No dependencies needed on recipient's machine",
            "   • Works on Windows 7 and later",
            "   • ~500MB total size",
            "",
            "4. API Server: Deploy as REST API endpoint",
        ]
    )
    
    # SLIDE 14: Project Files Structure
    add_content_slide(
        "Project Structure",
        [
            "Core Files:",
            "  • pdf_chatbot.py - RAG pipeline (main logic)",
            "  • chatbot_gui.py - Desktop Tkinter interface",
            "  • streamlit_app.py - Web interface",
            "  • config.py - Configuration settings",
            "",
            "Build & Setup:",
            "  • build_exe.bat/ps1 - Executable builders",
            "  • chatbot_gui.spec - PyInstaller spec",
            "  • requirements.txt - Python dependencies",
            "",
            "Database:",
            "  • chroma_db/ - FAISS vector store cache",
        ]
    )
    
    # SLIDE 15: Key Improvements Made
    add_content_slide(
        "Recent Improvements",
        [
            "🔧 Enhanced Prompt Specificity",
            "   • Answer ONLY what is asked",
            "   • Don't list all options unless requested",
            "",
            "🔄 Better Context Management",
            "   • Conversation history tracking",
            "   • Follow-up question detection",
            "",
            "🎨 Improved UI/UX",
            "   • Color-coded chat bubbles",
            "   • Source expansion buttons",
            "   • Clear history functionality",
            "",
            "📊 Vector Store Optimization",
            "   • Increased retrieval context (k=5)",
            "   • Better semantic matching",
        ]
    )
    
    # SLIDE 16: Future Enhancements
    add_content_slide(
        "Future Enhancements",
        [
            "🚀 Planned Features:",
            "   • Multi-language support",
            "   • Advanced analytics dashboard",
            "   • Fine-tuned custom models",
            "   • Database backend (PostgreSQL)",
            "",
            "🔐 Security Enhancements:",
            "   • User authentication",
            "   • Audit logging",
            "   • Rate limiting",
            "",
            "⚡ Performance:",
            "   • Local LLM models (Ollama)",
            "   • Cache optimization",
        ]
    )
    
    # SLIDE 17: Troubleshooting
    add_content_slide(
        "Troubleshooting & Maintenance",
        [
            "❌ Issue: Incorrect answers?",
            "   ✓ Rebuild vector store: Remove chroma_db folder",
            "",
            "❌ Issue: API key errors?",
            "   ✓ Check .env file configuration",
            "   ✓ Verify OpenAI API key is valid",
            "",
            "❌ Issue: PDF not loading?",
            "   ✓ Ensure PDF path in config.py is correct",
            "   ✓ Check file exists and readable",
            "",
            "❌ Issue: Slow responses?",
            "   ✓ Check internet connection (API calls)",
            "   ✓ Reduce retrieval context (k parameter)",
        ]
    )
    
    # SLIDE 18: Benefits & ROI
    add_content_slide(
        "Business Benefits",
        [
            "📈 Increased Productivity:",
            "   • Instant policy access (seconds vs. minutes)",
            "   • Reduced HR support tickets",
            "",
            "💰 Cost Savings:",
            "   • Fewer HR staff queries",
            "   • Automated policy information delivery",
            "",
            "✨ Improved User Experience:",
            "   • 24/7 availability",
            "   • Accurate, consistent information",
            "   • Source transparency",
            "",
            "🎯 Better Compliance:",
            "   • Policy adherence tracking",
            "   • Audit trail of inquiries",
        ]
    )
    
    # SLIDE 19: Demo & Live Testing
    add_content_slide(
        "Live Demo",
        [
            "🎬 Ready for Live Demonstration:",
            "",
            "Option 1: CLI Demo",
            "   • python pdf_chatbot.py",
            "   • Direct terminal interaction",
            "",
            "Option 2: Web Demo",
            "   • streamlit run streamlit_app.py",
            "   • Browser-based interface",
            "",
            "Option 3: Desktop Demo",
            "   • Run dist/HR_Chatbot.exe",
            "   • Professional GUI interface",
        ]
    )
    
    # SLIDE 20: Summary & Next Steps
    add_content_slide(
        "Summary & Next Steps",
        [
            "✅ Summary:",
            "   • AI-powered RAG chatbot for HR policies",
            "   • Multiple interfaces (CLI, Web, Desktop)",
            "   • Accurate, source-backed answers",
            "",
            "📋 Next Steps:",
            "   1. Configure OpenAI API key",
            "   2. Test with employee handbook",
            "   3. Deploy to target environment",
            "   4. Gather user feedback",
            "   5. Iterate and improve",
        ]
    )
    
    # SLIDE 21: Contact & Resources
    add_title_slide(
        "Questions?",
        "Contact | Documentation | Demo Available"
    )
    
    # Save presentation
    output_path = "HR_Chatbot_Presentation.pptx"
    prs.save(output_path)
    print(f"✅ Presentation created successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    create_presentation()
