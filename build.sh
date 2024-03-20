pyinstaller b3denv.py --onefile

if [[ "$OSTYPE" == "darwin"* ]]; then
    ditto dist/b3denv ~/Coldtype/bin
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    python -c "from shutil import copy2; from pathlib import Path; copy2('dist/b3denv', Path('~/Coldtype/bin/').expanduser())"
else
    python -c "from shutil import copy2; from pathlib import Path; copy2('dist/b3denv.exe', Path('~/Coldtype/bin/').expanduser())"
fi
