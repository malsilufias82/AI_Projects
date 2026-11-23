# Fix Chatbot Accuracy - Rebuild Vector Store

The chatbot prompt has been updated to be **much stricter** about not inferring or assuming information.

## 🔄 Rebuild the Vector Store

To apply the new stricter rules, rebuild the vector store:

### **Option 1: Using Desktop GUI**
1. Run the app: `python chatbot_gui.py`
2. Click the "Reload Vector Store" button
3. Wait for the rebuild to complete (2-3 minutes)
4. Try your questions again

### **Option 2: Delete and Recreate**
```powershell
# Remove old vector store
Remove-Item -Recurse -Force chroma_db

# Run the app to rebuild
python chatbot_gui.py
```

### **Option 3: Use Clear Command in CLI**
```powershell
# Delete vector store
rmdir /s /q chroma_db

# Run CLI version
python pdf_chatbot.py
```

---

## ✅ What Changed

The chatbot now:
- ✅ Uses ONLY exact text from the handbook
- ✅ Does NOT infer or make assumptions
- ✅ Does NOT change "everyone" to "confirmed employees"
- ✅ Quotes the exact wording
- ✅ Admits when information is unclear
- ✅ Retrieves more context (5 pages instead of 3)

---

## 🧪 Test After Rebuild

Ask these questions:

**Test 1**: "Does the company offer group mediclaim?"
- Expected: Yes + Page 61

**Test 2**: "Is group mediclaim for all employees or confirmed only?"
- Expected: Based on handbook page 61, should say "all employees" if that's what the handbook states

**Test 3**: "Who is eligible for bereavement leave?"
- Expected: Confirmed employees only + Page 56

---

## 📝 Important Note

If the chatbot is still giving incorrect answers after rebuild:
1. Check if it's pulling from the right page
2. Verify the handbook actually says what you expect
3. The chatbot quotes the handbook - if it's wrong, the handbook text might need clarification

---

**Rebuild your vector store and test again!** 🚀
