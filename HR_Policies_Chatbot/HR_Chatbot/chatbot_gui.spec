# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for HR Policies Chatbot
Builds a standalone .exe application with all dependencies bundled
"""

a = Analysis(
    ['chatbot_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('chroma_db', 'chroma_db'),  # Include cached vector store
    ],
    hiddenimports=[
        'langchain',
        'langchain_openai',
        'langchain_classic',
        'langchain_text_splitters',
        'faiss',
        'pypdf',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HR_Chatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Optional: uncomment and provide icon file if needed
)
