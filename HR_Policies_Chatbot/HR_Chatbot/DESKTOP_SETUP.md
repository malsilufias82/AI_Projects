# HR Policies Chatbot - Desktop App - Quick Setup

## 🚀 First Time Running the Desktop App

### Option 1: Run Directly (Easiest)
```powershell
python chatbot_gui.py
```

Or use the launcher:
```powershell
.\run_desktop.bat
```

### Option 2: Run the Built .exe
```powershell
.\build_exe.bat          # Build first time (takes 2-5 minutes)
.\dist\HR_Chatbot\HR_Chatbot.exe   # Run the app
```

---

## ⚙️ Configuration on First Run

When you first run the app, you'll see an error message if configuration is missing. 

**Don't worry!** Just click **"Yes"** when asked to configure.

### Configuration Dialog:
1. **PDF File Path**
   - Click "Browse..." button
   - Select your `Employee Handbook.pdf` file
   - Default location: `C:\Saif\FromVLink\Employee Handbook.pdf`

2. **OpenAI API Key**
   - Get your key from: https://platform.openai.com/api-keys
   - Paste it in the field
   - Must start with `sk-`

3. **Save & Restart**
   - Click "Save & Restart" button
   - App will restart automatically
   - Everything should work now!

---

## ✅ Troubleshooting

### "Failed to initialize chatbot" Error

**Solution 1: Configure Settings**
- Click the "Configure" button at the bottom
- Update PDF path and API key
- Click "Save & Restart"

**Solution 2: Check .env File**
- Open `.env` file in your project
- Should contain:
  ```
  PDFCHATBOT_API_KEY=sk-xxxxx...
  PDF_PATH=C:\Path\To\Employee Handbook.pdf
  ```

**Solution 3: Test Direct Run**
```powershell
python chatbot_gui.py
# or
python pdf_chatbot.py
```

### "PDF file not found" Error
- Make sure the PDF file path is correct
- Click "Configure" and browse for the file
- Save & Restart

### "API Key Error" Error
- Verify your OpenAI API key is valid
- Check it starts with `sk-`
- Get a new key from: https://platform.openai.com/api-keys
- Click "Configure" and update it

---

## 🎯 Using the App

After configuration, when you start the app:

1. **First launch**: Wait for "Building vector store..." (2-5 minutes, one time only)
2. **Subsequent launches**: "Loaded from cache" (instant startup)
3. **Ask questions**: Type your question and press Enter or click "Send"
4. **View sources**: Click "View Sources" to see citations

---

## 🔧 Configuration Button

The app has a "Configure" button that lets you:
- Change the PDF file
- Update your API key
- Reload settings

Just click it anytime!

---

## 📋 File Checklist

Before running, make sure you have:

- ✅ `Employee Handbook.pdf` (or your PDF file)
- ✅ OpenAI API key (from platform.openai.com)
- ✅ `.env` file (or let the app create one)

---

## 🐛 Debug Mode

To see detailed error messages in the console:

```powershell
python chatbot_gui.py
# (Keep the console open to see any errors)
```

---

**Ready? Start the app and let the configuration wizard guide you!** 🎯
