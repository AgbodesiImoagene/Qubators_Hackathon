# -*- mode: python ; coding: utf-8 -*-
# from PyInstaller.hooks.hookutils import collect_submodules

block_cipher = None


a = Analysis(['appv3_single_async_thread.py'],
             pathex=['C:\\Users\\agbod\\GitHub\\Qubators_Hackathon\\v3'],
             binaries=[],
             datas=[('Logo.ico', '.'), 
                    ('NameCropped.png', '.'), 
                    ('Welcome.png', '.'), 
                    ('Splash.ico', '.'), ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
splash = Splash('NewSplash.ico',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=None,
                text_size=12,
                minify_script=True)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas, 
          splash, 
          splash.binaries,
          [],
          name='AutoTrader',
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
          entitlements_file=None , icon='Logo.ico')