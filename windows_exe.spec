# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mLRS_Flasher.py'],
    pathex=[],
    binaries=[],
    datas=[('venv\\Lib\\site-packages\\pymavlink\\dialects', 'pymavlink/dialects'), ('venv\\Lib\\site-packages\\esptool\\targets\\stub_flasher', 'esptool/targets/stub_flasher'), ('assets\\*', 'assets'), ('thirdparty\\stm32cubeprogrammer\\win*', 'stm32cubeprogrammer')],
    hiddenimports=['pymavlink', 'pymavlink.mavutil', 'pymavlink.dialects.v20.common'],
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
    a.binaries,
    a.datas,
    [],
    name='mLRS_Flasher',
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
    icon=['assets\\mLRS_logo_round.ico'],
)
