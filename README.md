Example, a file (called something like `setup.sh`) that contains something like this:

```bash
export BLENDER_PATH="~/Desktop/Blenders/Blender3.3.app"
alias bpy=$(b3denv bpy)
alias blender=$(b3denv blender)
```

Then you can run it:

`. ./setup.sh`

And you'll have `bpy` and `blender` available as aliases in your bash (dynamically)