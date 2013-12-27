# -*- mode: python -*-
a = Analysis(['slicer.py'],
             pathex=['C:\\Documents and Settings\\user\\My Documents\\Dropbox\\ixi\\python\\slicer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='slicer.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='data\\ixi_transp.ico')
