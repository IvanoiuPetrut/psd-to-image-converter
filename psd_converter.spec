# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Get the absolute path to the src directory
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))

# Collect all data files from src directory
datas = []
for root, dirs, files in os.walk(src_path):
    for file in files:
        if file.endswith(('.py', '.ico', '.png')):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, os.path.dirname(__file__))
            datas.append((rel_path, os.path.dirname(rel_path)))

# Collect all hidden imports
hidden_imports = [
    'PIL',
    'PIL._tkinter_finder',
    'psd_tools',
    'dateutil',
    'xml.etree.ElementTree'
]

a = Analysis(
    ['src/main.py'],  # Changed to use the new main entry point
    pathex=[src_path],  # Add src directory to path
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Platform-specific settings
if sys.platform.startswith('win'):
    icon_file = 'icon.ico'
    console = False
elif sys.platform.startswith('linux'):
    icon_file = 'icon.png'  # Linux typically uses PNG for icons
    console = False
else:  # macOS
    icon_file = 'icon.icns'  # macOS uses .icns files
    console = False

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PSD Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file if os.path.exists(icon_file) else None
) 