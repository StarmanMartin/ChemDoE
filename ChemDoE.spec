# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import sys
import os

# Define the script name
script_name = "ChemDoE/main.py"

# Collect hidden imports for PIL (fixes ImageTk issue)
hidden_imports = ["PIL.ImageTk", "PIL._tkinter_finder"]

# Collect static files
static_files = [
    ("ChemDoE/icons/", "ChemDoE/icons/")  # Copies assets folder
] + collect_data_files("chemotion_api")

# Create an executable build configuration
a = Analysis(
    [script_name],
    pathex=[],
    binaries=[],
    datas=static_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

# Build the executable
pyz = PYZ(a.pure, a.zipped_data, cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ChemDoE",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set True if you want a console window
    icon="ChemDoE/icons/fixed/chemotion-full.ico"  # Change this to your icon file
)
