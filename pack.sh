#python Configure.py
#python -O /home/r2d2/Mahaigaina/pyinstaller-1.5.1/Makespec.py -F -w -i data\ixi_transp.ico slicer.py 
#python -O /home/r2d2/Mahaigaina/pyinstaller-1.5.1/Build.py optimize=True /home/r2d2/Mahaigaina/pyinstaller-1.5.1/slicer/slicer.spec 

python -O /home/r2d2/Mahaigaina/PyInstaller-2.1/pyinstaller.py -F -w -d -c -i ./data\ixi_transp.ico slicer.py

cp -r ./dist/* ~/Mahaigaina/dist

rm -rf ./dist
rm -rf ./build