import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from pdf_chatbot import PDFChatbot
import os
import sys
import math
from config import PDF_PATH, OPENAI_API_KEY
import json

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VLink HR Policies Chatbot")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.icon_image = None
        
        # Load app icon
        self._load_app_icon()
        
        # Initialize chatbot
        self.chatbot = None
        self.is_initialized = False
        self.config_file = "chatbot_config.json"
        
        # Load configuration
        self.load_config()
        
        # Create GUI
        self.create_widgets()
        self.initialize_chatbot()
        
    def load_config(self):
        """Load saved configuration."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            self.config = {}
    
    def save_config(self):
        """Save configuration."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    
    def _load_app_icon(self):
        """Load the application icon and assign it to the root window."""
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VLink_Icon.PNG")
        if os.path.exists(icon_path):
            try:
                # Load a high-quality icon for the window
                window_icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, window_icon)
                self.window_icon = window_icon

                # Use Pillow for a higher-quality scaled title icon if available
                if Image and ImageTk:
                    pil_icon = Image.open(icon_path)
                    desired_height = 60
                    ratio = desired_height / pil_icon.height
                    desired_width = int(pil_icon.width * ratio)
                    pil_icon = pil_icon.resize((desired_width, desired_height), Image.LANCZOS)
                    self.icon_image = ImageTk.PhotoImage(pil_icon)
                else:
                    # Fallback to Tkinter scaling if Pillow is not present
                    icon = tk.PhotoImage(file=icon_path)
                    orig_height = icon.height()
                    if orig_height > 60:
                        scale_factor = max(1, orig_height // 60)
                        self.icon_image = icon.subsample(scale_factor, scale_factor)
                    elif orig_height < 60:
                        scale_factor = math.ceil(60 / orig_height)
                        self.icon_image = icon.zoom(scale_factor, scale_factor)
                    else:
                        self.icon_image = icon
            except Exception:
                self.icon_image = None
        else:
            self.icon_image = None

    def create_widgets(self):
        """Create GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title with icon
        title_frame = tk.Frame(main_frame, bg=self.root.cget('bg'))
        title_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        title_frame.columnconfigure(0, weight=1)

        title_text = "HR Policies Chatbot"
        if self.icon_image:
            title_label = tk.Label(
                title_frame,
                text=title_text,
                image=self.icon_image,
                compound=tk.LEFT,
                font=("Arial", 18, "bold"),
                bg=self.root.cget('bg'),
                anchor=tk.CENTER,
                padx=10,
            )
        else:
            title_label = tk.Label(
                title_frame,
                text=title_text,
                font=("Arial", 18, "bold"),
                bg=self.root.cget('bg'),
                anchor=tk.CENTER,
            )

        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Initializing...", 
                                      foreground="orange")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Chat display area
        chat_frame = ttk.LabelFrame(main_frame, text="Conversation", padding="10")
        chat_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       padx=5, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=20, width=80,
                                                     wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure tags for styling
        self.chat_display.tag_config("user", foreground="#667eea", font=("Arial", 10, "bold"), justify=tk.RIGHT)
        self.chat_display.tag_config("bot", foreground="#2e7d32", font=("Arial", 10), justify=tk.LEFT)
        self.chat_display.tag_config("source", foreground="#1976d2", font=("Arial", 9, "italic"), justify=tk.LEFT)
        self.chat_display.tag_config("error", foreground="#d32f2f", font=("Arial", 10), justify=tk.LEFT)
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Input field
        self.input_field = ttk.Entry(input_frame, width=80)
        self.input_field.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        self.input_field.bind('<Return>', lambda e: self.send_question())
        
        # Send button
        self.send_button = ttk.Button(input_frame, text="Send ➤", command=self.send_question)
        self.send_button.grid(row=0, column=1, padx=5)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Clear chat button
        clear_button = ttk.Button(control_frame, text="Clear Chat", command=self.clear_chat)
        clear_button.grid(row=0, column=0, padx=5)
        
        # Reinitialize button
        reinit_button = ttk.Button(control_frame, text="Reload Vector Store", 
                                   command=self.reinitialize_chatbot)
        reinit_button.grid(row=0, column=1, padx=5)
        
        # Configure button
        config_button = ttk.Button(control_frame, text="Configure", command=self.setup_configuration)
        config_button.grid(row=0, column=2, padx=5)
        
        # About button
        about_button = ttk.Button(control_frame, text="About", command=self.show_about)
        about_button.grid(row=0, column=3, padx=5)

        # Exit button
        exit_button = ttk.Button(control_frame, text="Exit", command=self.root.destroy)
        exit_button.grid(row=0, column=4, padx=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
    
    def initialize_chatbot(self):
        """Initialize chatbot in a separate thread."""
        thread = threading.Thread(target=self._init_chatbot_thread, daemon=True)
        thread.start()
    
    def _init_chatbot_thread(self):
        """Run initialization in background thread."""
        try:
            # First, validate configuration
            config_error = self.validate_configuration()
            if config_error:
                self.update_status(f"✗ Configuration Error", "red")
                # Show configuration dialog
                self.root.after(0, self.show_config_error_dialog, config_error)
                return
            
            self.chatbot = PDFChatbot()
            
            # Try to load existing vector store
            if self.chatbot.load_existing_vector_store():
                self.update_status("✓ Chatbot ready! (Loaded from cache)", "green")
                self.is_initialized = True
            else:
                # Initialize from PDF
                self.update_status("Building vector store from PDF (this may take a moment)...", "orange")
                if self.chatbot.initialize():
                    self.update_status("✓ Chatbot initialized and ready!", "green")
                    self.is_initialized = True
                else:
                    self.update_status("✗ Failed to initialize chatbot", "red")
                    self.root.after(0, messagebox.showerror, "Error", "Failed to initialize chatbot from PDF. Please check your configuration.")
        except FileNotFoundError as e:
            error_msg = f"File not found: {str(e)}\n\nPlease ensure the PDF file exists at the configured path."
            self.update_status(f"✗ File Error", "red")
            self.root.after(0, messagebox.showerror, "File Error", error_msg)
        except ValueError as e:
            error_msg = f"Configuration Error: {str(e)}\n\nPlease check your .env file and API key."
            self.update_status(f"✗ Configuration Error", "red")
            self.root.after(0, messagebox.showerror, "Configuration Error", error_msg)
        except Exception as e:
            error_msg = f"Error initializing chatbot:\n{type(e).__name__}: {str(e)}"
            self.update_status(f"✗ Error: {str(e)}", "red")
            self.root.after(0, messagebox.showerror, "Initialization Error", error_msg)
    
    def show_config_error_dialog(self, error_msg):
        """Show configuration error dialog with option to configure."""
        result = messagebox.askyesno(
            "Configuration Error",
            f"Configuration Error:\n{error_msg}\n\nWould you like to configure now?"
        )
        if result:
            self.setup_configuration()
    
    def validate_configuration(self):
        """Validate configuration before initialization."""
        try:
            import importlib
            import sys
            
            # Reload config module to get fresh values
            if 'config' in sys.modules:
                importlib.reload(sys.modules['config'])
            
            from config import PDF_PATH, OPENAI_API_KEY
            
            # Check PDF path
            if not PDF_PATH:
                return "PDF_PATH not configured in config.py"
            
            if not os.path.exists(PDF_PATH):
                return f"PDF file not found at:\n{PDF_PATH}\n\nPlease configure the correct path."
            
            # Check API key
            if not OPENAI_API_KEY:
                return "OPENAI_API_KEY not set in .env file"
            
            if len(OPENAI_API_KEY.strip()) < 10:
                return "OPENAI_API_KEY appears to be invalid (too short)"
            
            return None
        except Exception as e:
            return f"Failed to load configuration: {str(e)}"
    
    def update_status(self, message, color="black"):
        """Update status label."""
        self.status_label.config(text=message, foreground=color)
        self.root.update()
    
    def send_question(self):
        """Send a question to the chatbot."""
        question = self.input_field.get().strip()
        
        if not question:
            messagebox.showwarning("Input Error", "Please enter a question.")
            return
        
        if not self.is_initialized:
            messagebox.showerror("Not Ready", "Chatbot is not initialized yet. Please wait.")
            return
        
        # Disable input while processing
        self.send_button.config(state=tk.DISABLED)
        self.input_field.config(state=tk.DISABLED)
        
        # Add user message to display with right alignment and spacing
        self.append_chat("\nYou: " + question + "\n", "user")
        
        # Process in separate thread
        thread = threading.Thread(target=self._process_question_thread, 
                                 args=(question,), daemon=True)
        thread.start()
    
    def _process_question_thread(self, question):
        """Process question in background thread."""
        try:
            self.update_status("Thinking...", "orange")
            response = self.chatbot.answer_question(question)
            
            if response:
                self.append_chat("\n", "")
                self.append_chat("Chatbot: ", "bot")
                self.append_chat(response["answer"] + "\n", "")
                
                if response["sources"]:
                    self.append_chat("\nSource: ", "source")
                    page_numbers = [str(source['page']) for source in response["sources"]]
                    self.append_chat("Page " + ", ".join(page_numbers) + "\n", "source")
            else:
                self.append_chat("Chatbot: ", "bot")
                self.append_chat("Sorry, I couldn't process your question. Please try again.\n", "error")
            
            self.update_status("✓ Ready", "green")
        except Exception as e:
            self.append_chat("Chatbot: ", "bot")
            self.append_chat(f"Error: {str(e)}\n", "error")
            self.update_status("✗ Error occurred", "red")
        finally:
            # Re-enable input
            self.send_button.config(state=tk.NORMAL)
            self.input_field.config(state=tk.NORMAL)
            self.input_field.delete(0, tk.END)
            self.input_field.focus()
    
    def append_chat(self, text, tag=""):
        """Append text to chat display."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear chat history."""
        if messagebox.askyesno("Confirm", "Clear all chat history?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.config(state=tk.DISABLED)
            # Also clear chatbot conversation history
            if self.chatbot:
                self.chatbot.clear_history()
    
    def reinitialize_chatbot(self):
        """Reinitialize chatbot from PDF."""
        if messagebox.askyesno("Confirm", "This will rebuild the vector store from the PDF. Continue?"):
            self.is_initialized = False
            self.send_button.config(state=tk.DISABLED)
            self.input_field.config(state=tk.DISABLED)
            self.initialize_chatbot()
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About HR Policies Chatbot", 
                          """HR Policies Chatbot v1.0
                          
Powered by LangChain & OpenAI

This chatbot uses AI to answer questions about HR policies from the Employee Handbook.

Features:
• Semantic search through HR documents
• Source citations for transparency
• Offline vector store caching
• Standalone desktop application

The chatbot caches the knowledge base locally, so after first setup, 
API connectivity is only needed for generating new answers.
""")
    
    def setup_configuration(self):
        """Show configuration setup dialog."""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Setup Configuration")
        setup_window.geometry("550x350")
        setup_window.resizable(False, False)
        
        # Make it modal
        setup_window.transient(self.root)
        setup_window.grab_set()
        
        # Title
        title_label = ttk.Label(setup_window, text="Configure Chatbot", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Info label
        info_label = ttk.Label(setup_window, text="Please configure the following settings:", 
                              font=("Arial", 10))
        info_label.pack(pady=5)
        
        # PDF Path section
        pdf_frame = ttk.LabelFrame(setup_window, text="PDF File Path", padding="10")
        pdf_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(pdf_frame, text="Employee Handbook PDF:").pack(anchor=tk.W)
        pdf_path_var = tk.StringVar(value=os.getenv("PDF_PATH", "C:\\Saif\\FromVLink\\Employee Handbook.pdf"))
        pdf_entry = ttk.Entry(pdf_frame, textvariable=pdf_path_var, width=60)
        pdf_entry.pack(pady=5, fill=tk.X)
        
        def browse_pdf():
            file_path = filedialog.askopenfilename(
                title="Select Employee Handbook PDF",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                pdf_path_var.set(file_path)
        
        ttk.Button(pdf_frame, text="Browse...", command=browse_pdf).pack(anchor=tk.W, pady=5)
        
        # API Key section
        api_frame = ttk.LabelFrame(setup_window, text="OpenAI API Key", padding="10")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(api_frame, text="Enter your OpenAI API Key:").pack(anchor=tk.W)
        ttk.Label(api_frame, text="(Get it from https://platform.openai.com/api-keys)", 
                 font=("Arial", 9), foreground="gray").pack(anchor=tk.W)
        
        api_key_var = tk.StringVar(value=os.getenv("OPENAI_API_KEY", ""))
        api_entry = ttk.Entry(api_frame, textvariable=api_key_var, width=60, show="*")
        api_entry.pack(pady=5, fill=tk.X)
        
        # Buttons
        button_frame = ttk.Frame(setup_window)
        button_frame.pack(fill=tk.X, padx=10, pady=15)
        
        def save_config():
            pdf_path = pdf_path_var.get().strip()
            api_key = api_key_var.get().strip()
            
            if not pdf_path:
                messagebox.showerror("Error", "Please specify a PDF file path")
                return
            
            if not os.path.exists(pdf_path):
                messagebox.showerror("Error", f"PDF file not found:\n{pdf_path}")
                return
            
            if not api_key:
                messagebox.showerror("Error", "Please enter your API key")
                return
            
            if len(api_key) < 10:
                messagebox.showerror("Error", "API key appears too short")
                return
            
            # Save to .env file
            try:
                with open(".env", "w") as f:
                    f.write(f'PDFCHATBOT_API_KEY={api_key}\n')
                    f.write(f'PDF_PATH={pdf_path}\n')
                    f.write(f'MODEL_NAME=gpt-3.5-turbo\n')
                    f.write(f'TEMPERATURE=0.7\n')
                
                # Also update environment variables
                os.environ['PDFCHATBOT_API_KEY'] = api_key
                os.environ['PDF_PATH'] = pdf_path
                
                messagebox.showinfo("Success", "Configuration saved!\n\nThe application will now restart.")
                setup_window.destroy()
                self.root.destroy()
                # Restart the application
                os.execv(sys.executable, ['python', __file__])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")
        
        ttk.Button(button_frame, text="Save & Restart", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=setup_window.destroy).pack(side=tk.LEFT, padx=5)
        
        setup_window.mainloop()


def main():
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
