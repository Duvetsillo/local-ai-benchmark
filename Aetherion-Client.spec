# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/local_ai_benchmark/client/native.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/local_ai_benchmark/client/qt/assets', 'local_ai_benchmark/client/qt/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtQml', 'PySide6.QtQuick'],
    noarchive=False,
    optimize=0,
)
# Qt on Windows imports the operating system ICU API (unsuffixed exports).
# A development PATH containing Poppler/Conda can cause PyInstaller to collect
# another icuuc.dll with version-suffixed exports. Use Windows' system DLL.
import sys
if sys.platform == 'win32':
    a.binaries = [item for item in a.binaries
                  if item[0].lower() not in {'icuuc.dll', 'icudt78.dll'}]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Aetherion-Client',
    icon='src/local_ai_benchmark/client/qt/assets/aetherion.ico',
    version='src/local_ai_benchmark/client/qt/assets/version_info.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    manifest='src/local_ai_benchmark/client/qt/assets/aetherion.manifest',
)
