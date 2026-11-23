# HR Policies Chatbot - Desktop Application Guide

## 🚀 Overview

The HR Policies Chatbot now has **two interfaces**:

1. **Web Interface** (Streamlit) - For development and web use
2. **Desktop Application** (Tkinter) - Standalone .exe for easy distribution

## 📦 Desktop Application (New!)

### Benefits of Desktop Application:
- ✅ Standalone .exe - no Python installation needed
- ✅ No web server required
- ✅ Faster startup and response times
- ✅ Cached vector store - works without repeated API calls
- ✅ Easy distribution to other users
- ✅ Professional desktop UI

### System Requirements:
- Windows 7 or later
- 500 MB free disk space
- (No internet required after first setup)

---

## 🛠️ Building the .exe File

### Step 1: Prepare Your System

Ensure your virtual environment is activated:

**PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**
```bash
venv\Scripts\activate.bat
```

### Step 2: Build the Executable

Choose your method:

**Option A - Using Batch File (Easiest):**
```bash
build_exe.bat
```

**Option B - Using PowerShell:**
```powershell
.\build_exe.ps1
```

**Option C - Manual Build:**
```bash
pip install pyinstaller
pyinstaller --noconfirm --clean chatbot_gui.spec
```

### Step 3: Find Your Executable

After building, the .exe will be located at:
```
dist/HR_Chatbot.exe
```

---

## 📂 Distribution

### Creating a Portable Package

1. **Build the .exe** (follow steps above)

2. **Copy the dist folder:**
   - Entire `dist` folder contains the application
   - All dependencies are bundled inside

3. **Share with others:**
   - Users can run `HR_Chatbot.exe` directly
   - No Python installation needed
   - No setup.bat or configuration needed

4. **Folder structure they'll see:**
   ```
   HR_Chatbot/
   ├── HR_Chatbot.exe
   ├── chroma_db/          (Cached vector store)
   ├── _internal/          (Dependencies - auto-created)
   └── ... other files
   ```

---

## 🎯 Using the Desktop Application

### First Time Setup:
1. Run `HR_Chatbot.exe`
2. Wait for "Building vector store from PDF..." message
3. This creates a local cache of all HR documents
4. Process takes 2-5 minutes (one time only)

### After Setup:
1. Run `HR_Chatbot.exe`
2. Says "Loaded from cache" - instant startup
3. Ask questions about HR policies
4. All answers are generated locally (requires OpenAI API key)

### Features:
- **Chat Area** - View conversation history
- **Input Field** - Type your questions (press Enter or click Send)
- **Clear Chat** - Remove chat history
- **Reload Vector Store** - Rebuild from PDF if needed
- **About** - View application information

---

## 🔑 API Key Management

### Setup (First Time):
The `.env` file in your project contains:
```
PDFCHATBOT_API_KEY=your-api-key-here
```

### Distribution Without API Key:
If building for others without API access:

1. **Option 1: Pre-build with Your Key**
   - User doesn't see the key (it's bundled in the .exe)
   - User can share .exe safely

2. **Option 2: Local LLM (Recommended for Privacy)**
   - Install Ollama: https://ollama.ai
   - Use local Llama 2 model (free, no API key needed)
   - Modify `pdf_chatbot.py` to use local LLM instead of OpenAI

3. **Option 3: Ask User for Key**
   - Create setup wizard in GUI
   - Let user enter API key on first run
   - Store it securely

---

## 🔄 Workflow Summary

### Development:
```
Edit code → Run streamlit_app.py → Test in browser
```

### Distribution:
```
Final code → build_exe.bat → dist/HR_Chatbot.exe → Share with others
```

---

## 📋 Troubleshooting

### Build Fails with "icon.ico not found"
**Solution:** Comment out the `icon` line in `chatbot_gui.spec`

### .exe doesn't run
**Solution:** Check Windows Defender/Antivirus isn't blocking it

### "Cannot find module" error
**Solution:** Rebuild with `--noconfirm --clean` flags

### Vector store not loading
**Solution:** Delete `chroma_db` folder and use "Reload Vector Store" button

---

## 📝 Files Overview

| File | Purpose |
|------|---------|
| `chatbot_gui.py` | Main desktop application code |
| `chatbot_gui.spec` | PyInstaller configuration |
| `build_exe.bat` | Windows batch build script |
| `build_exe.ps1` | PowerShell build script |
| `pdf_chatbot.py` | Core chatbot logic |
| `config.py` | Configuration settings |

---

## 🚀 Next Steps

### To Build Your First .exe:
```bash
# 1. Activate virtual environment
.\venv\Scripts\activate.ps1

# 2. Run build script
.\build_exe.bat

# 3. Find executable
# dist/HR_Chatbot.exe
```

### To Test Desktop App Before Building:
```bash
# Run the desktop GUI directly
python chatbot_gui.py
```

---

## 💡 Tips

- **Cache is Your Friend**: Vector store is cached locally, so startup gets faster
- **Backup Your Code**: Always keep a backup before rebuilding
- **Test on Clean PC**: If possible, test the .exe on a computer without Python installed
- **Professional Look**: Add an icon.ico file for a professional application icon

---

## ❓ Need Help?

If you encounter issues:
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Test the GUI directly: `python chatbot_gui.py`
3. Check console for error messages during build
4. Ensure your `.env` file has a valid OpenAI API key

---

**Happy chatting! 🤖**
