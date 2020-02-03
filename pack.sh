python -O ~/Mahaigaina/PyInstaller-2.1/pyinstaller.py -F -w -d -c -i ./data/ixi_transp.ico slicer.py

cp -r ./dist/* ~/Mahaigaina/slicer0.2.1_linux

rm -rf ./dist
rm -rf ./build