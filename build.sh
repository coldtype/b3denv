pyinstaller b3denv.spec
python -c "from shutil import copy2; from pathlib import Path; copy2('dist/b3denv.exe', Path('~/Coldtype/bin/').expanduser())"