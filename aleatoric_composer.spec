# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Aleatoric Composer para la Escuela SUR (beta)
Builds a standalone executable with ZERO network capability.
"""

import sys

block_cipher = None

# --- Exclusions -----------------------------------------------------------
# Network modules to exclude from bundle.
# NOTE: socket/ssl are NOT excluded because multiprocessing depends on them.
# Instead, a runtime hook (hooks/rthook_block_network.py) monkey-patches
# socket.connect to block ALL outbound connections at runtime.
NETWORK_EXCLUDES = [
    'http.server', 'http.cookiejar',
    'ftplib', 'smtplib', 'imaplib', 'poplib', 'telnetlib',
    'xmlrpc', 'socketserver', 'websocket', 'requests', 'aiohttp', 'httpx',
]

# PySide6 modules we don't use (avoids recursion & shrinks bundle)
PYSIDE6_EXCLUDES = [
    'PySide6.QtNetwork', 'PySide6.QtNetworkAuth',
    'PySide6.QtWebEngine', 'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets', 'PySide6.QtWebSockets',
    'PySide6.QtWebChannel',
    'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.Qt3DAnimation',
    'PySide6.Qt3DExtras', 'PySide6.Qt3DInput', 'PySide6.Qt3DLogic',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
    'PySide6.QtBluetooth', 'PySide6.QtNfc',
    'PySide6.QtSensors', 'PySide6.QtSerialPort', 'PySide6.QtSerialBus',
    'PySide6.QtSql', 'PySide6.QtTest',
    'PySide6.QtCharts', 'PySide6.QtDataVisualization',
    'PySide6.QtGraphs', 'PySide6.QtGraphsWidgets',
    'PySide6.QtHttpServer', 'PySide6.QtLocation',
    'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
    'PySide6.QtPositioning', 'PySide6.QtPrintSupport',
    'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuick3D',
    'PySide6.QtQuickControls2', 'PySide6.QtQuickWidgets',
    'PySide6.QtRemoteObjects', 'PySide6.QtScxml',
    'PySide6.QtSpatialAudio', 'PySide6.QtStateMachine',
    'PySide6.QtSvg', 'PySide6.QtSvgWidgets',
    'PySide6.QtTextToSpeech', 'PySide6.QtUiTools', 'PySide6.QtXml',
    'PySide6.QtDesigner', 'PySide6.QtDBus', 'PySide6.QtConcurrent',
    'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
]

# Unneeded large modules
SIZE_EXCLUDES = [
    'tkinter',
    'pip', 'ensurepip', 'pytest', 'pygments',
]

ALL_EXCLUDES = NETWORK_EXCLUDES + PYSIDE6_EXCLUDES + SIZE_EXCLUDES

a = Analysis(
    ['src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pedalboard',
        'soundfile',
        'librosa',
        'librosa.core',
        'librosa.effects',
        'scipy.signal',
        'scipy.signal.windows',
        'scipy.ndimage',
        'numpy',
        'pydub',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_block_network.py'],
    excludes=ALL_EXCLUDES,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AleatoricComposer',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AleatoricComposer',
)

# macOS .app bundle (ignored on Windows)
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='AleatoricComposer.app',
        icon=None,
        bundle_identifier='com.escuelasur.aleatoriccomposer',
        info_plist={
            'CFBundleName': 'Aleatoric Composer',
            'CFBundleDisplayName': 'Aleatoric Composer para la Escuela SUR',
            'CFBundleVersion': '0.1.0',
            'CFBundleShortVersionString': '0.1.0',
            'NSHumanReadableCopyright': '\u00a9 Alvaro Hernandez Altozano 2026',
            'LSMinimumSystemVersion': '13.0',
        },
    )
