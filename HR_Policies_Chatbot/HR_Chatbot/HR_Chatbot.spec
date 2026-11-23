# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['chatbot_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('chroma_db', 'chroma_db')],
    hiddenimports=['langchain', 'langchain_openai', 'langchain_classic', 'langchain_text_splitters', 'faiss', 'pypdf', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HR_Chatbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HR_Chatbot',
)
