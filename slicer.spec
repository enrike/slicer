# -*- mode: python -*-
a = Analysis(['slicer.py'],
             pathex=['/home/r2d2/Dropbox/ixi/python/slicer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='slicer',
          debug=True,
          strip=None,
          upx=True,
          console=True , icon='dataixi_transp.ico')
