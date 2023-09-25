# b3denv

Sometimes you want to work with the Python that comes bundled with Blender.

Unfortunately, it's kind of a pain to remember where the Python binary is located, especially if you have multiple Blender versions installed on your computer.

`b3denv` is a command-line tool to simplify the process of running Blender and Blender’s python from the command-line.

## Installation

`b3denv` is designed to work with _any_ version of Python, since the whole idea of `b3denv` is to leverage your system Python to find and use Blender’s embedded Python to create a virtualenv (so your virtualenv will match the version of Blender’s python exactly, and you won’t have to install any other python (if you don't want to)).

So, on the command line:

```
pip install b3denv
```

This installs a `b3denv` command-line tool.

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

You’ll want a file (called something like `setup.sh`) that contains something like this:

```bash
export BLENDER_PATH="~/Desktop/Blenders/Blender3.3.app"
alias bpy=$(b3denv print python)
alias blender=$(b3denv print blender)
```

Then you can run it:

`. ./setup.sh`

And you'll have `bpy` and `blender` available as aliases in your bash (dynamically)

## Development

- `pip install -e .`
- `b3denv python -m venv venv`
- `source venv/bin/activate`