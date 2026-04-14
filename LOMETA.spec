# LOMETA.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os

block_cipher = None

# Liste de toutes les dépendances
hiddenimports = [
    # Modules standards
    'requests',
    'urllib3',
    'certifi', 
    'chardet',
    'idna',
    
    # PySide6
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtNetwork',
    
    # Autres
    'qrcode',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('addons', 'addons')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LOMETA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LOMETA',
)