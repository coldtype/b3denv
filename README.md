# b3denv

Sometimes you want to work with the Python that comes bundled with Blender.

Unfortunately, it's kind of a pain to remember where the Python binary is located, especially if you have multiple Blender versions installed on your computer.

`b3denv` is a command-line tool to simplify the process of running Blender and Blender’s python from the command-line. Also it can help with addon development.

## Installation

`b3denv` is designed to work with _any_ version of Python, since the whole idea of `b3denv` is to leverage your system Python to find and use Blender’s embedded Python to create a virtualenv (so your virtualenv will match the version of Blender’s python exactly, and you won’t have to install any other python (if you don't want to)).

So, on the command line:

```
pip install b3denv
```

This installs a `b3denv` command-line tool. (If it doesn’t, `b3denv` should still be available as a subprocess of your python interpreter, i.e. you could replace `b3denv` as a command with `py.exe -m b3denv` and get the same results, if you're on Windows and only have a py.exe for instance.)

To verify `b3denv` is working:

- `b3denv paths`

This should show the blender executable and blender python paths for the default installation location.

## Use

`b3denv print blender` will print the Blender executable path, i.e. what you want to call in order to start Blender from the command-line. To actually start Blender, you can run `b3denv blender`. To run the embedded python, you can run `b3denv python`, and to show its path, you can run `b3denv print python`.

## Non-default Blender installs

To use `b3denv` with a Blender _not_ located at the standard install location for your platform, you'll need to set a `BLENDER_PATH` environment variable on your system, like so:

```bash
export BLENDER_PATH="~/Desktop/Blenders/Blender3.3.app"
```

Then you can run `b3denv paths` to verify that `b3denv` is pointed at that version.

You can also do this on a single-line without modifying your bash location, if you’re looking to create a virtualenv using a specific version of Blender, like so: `BLENDER_PATH="~/Desktop/Blenders/Blender3.3.app" b3denv -m venv b33venv`. Using `b3denv` with that virtualenv activated will then automatically use the version of Blender specified when the virtualenv was created (unless overridden again in subsequent calls to `b3denv`).

## Working on Blender addons

If you’re working on a Blender addon locally, in the folder containing your addon code, you can run `b3denv install <addon-name>`, and b3denv will install a symlink to make the addon available in Blender itself.

You can also run `b3denv uninstall <addon-name>` to uninstall, and `b3denv show` to open the folder containing all of your installed addons.

## Development

- `python -m venv venv`
- activate the venv
- `pip install -e .`

## Building an executable

- `pyinstaller b3denv.spec`
- `ditto dist/b3denv/b3denv ~/Coldtype/bin` (to test the b3denv executable on Rob’s particular setup, i.e. Coldtype/bin is on the PATH)

## Command reference

- `b3denv`
    - prints current `b3denv` version and opens Blender from the command-line
- `b3denv -v`/`b3denv --version`
    - prints the current b3denv version
- `b3denv python`
    - finds the python bundled with Blender and starts the interactive python interpreter
- `b3denv show`
    - opens the directory where addons are installed for Blender
- `b3denv paths`
    - prints all relevant paths to the currently configured Blender, it’s Python, and it’s addon folder
- `b3denv print blender`
    - prints the path to the current Blender
- `b3denv print python`
    - prints the path to the current Blender-provided Python
- `b3denv download`
    - attempts to download and install the Python c headers that don’t come bundled with Blender’s embedded Python (useful for compiling c-based python packages using the Blender Python)
- `b3denv install <folder>`
    - installs the folder you provide as a symlink-ed addon in Blender
- `b3denv uninstall <folder>`
    - uninstalls the folder you provide (deletes the symlink)
- `b3denv release <folder>`
    - creates a downloadable zip of the addon
- `b3denv inline <folder>`
    - inlines the current venv/benv into the addon source code, so it can be bundled with the zipped addon

## Helpful additional things (notes to self)

- https://blender.stackexchange.com/questions/155247/how-to-add-a-shortcut-for-reload-scripts
- May be necessary: https://github.com/txoof/codesign

