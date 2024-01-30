pyinstaller b3denv.spec

#if [[ "$OSTYPE" == "linux-gnu"* ]]; then
#    # not yet supported

if [[ "$OSTYPE" == "darwin"* ]]; then
    ditto dist/b3denv ~/Coldtype/bin
else
    python -c "from shutil import copy2; from pathlib import Path; copy2('dist/b3denv.exe', Path('~/Coldtype/bin/').expanduser())"
fi