# -*- mode: python -*-
a = Analysis(['slicer.py'],
             pathex=['C:\\Documents and Settings\\user\\Ubuntu One\\python\\slicer'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'slicer.exe'),
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='data\\ixi_transp.ico')
app = BUNDLE(exe,
             name=os.path.join('dist', 'slicer.exe.app'))
