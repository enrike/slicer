# -*- mode: python -*-
a = Analysis(['data\\ixi_transp.ico', 'slicer.py'],
             pathex=['C:\\Documents and Settings\\user\\Ubuntu One\\python\\slicer'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'ixi_transp.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='-w')
