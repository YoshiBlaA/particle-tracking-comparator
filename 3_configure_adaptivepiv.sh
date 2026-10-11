#!/bin/bash
cd AdaptivePIV_3.7
source venv/bin/activate
cd AdaptivePIV
python setup.py sdist
cd dist
gunzip filename.gz
cd ..
python3.7 setup.py build_ext --inplace --cyth True
pyinstaller --hidden-import=openpiv --hidden-import=bottleneck --hidden-import=PIL._tkinter_finder example.py --noconfirm
cd dist
chmod +x example
