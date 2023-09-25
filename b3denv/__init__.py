import platform, re, os, sys, glob, subprocess, shutil

def _os(): return platform.system()
def on_windows(): return _os() == "Windows"
def on_mac(): return _os() == "Darwin"
def on_linux(): return _os() == "Linux"

root = os.path.abspath(".")

def get_vars(addon_name):
    if addon_name:
        addon_source = os.path.join(root, addon_name)
    else:
        addon_source = None
    
    blender = os.environ.get("BLENDER_PATH")
    
    if not blender:
        # try to figure out if we're in a virtualenv created with an embedded version of Blender's python
        # if we are, set the blender to that version of Blender
        try:
            p1 = subprocess.Popen(["which", "python"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p1.communicate()
            which_python = out.strip()
            p2 = subprocess.Popen([which_python, "-c", "import sysconfig;print(sysconfig.get_config_var('installed_base'))"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p2.communicate()
            installed_base = out.strip()
            if isinstance(installed_base, bytes):
                installed_base = installed_base.decode("utf-8")
            #print("Installed base", installed_base)
            if on_mac():
                d1 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(installed_base))))
                if "Blender" in os.path.basename(d1):
                    blender = d1
        except Exception as e:
            #print("failed", e)
            pass
    
    if not blender:
        if on_mac():
            blender = "/Applications/Blender.app/"
        elif on_windows():
            folder = "C:\\Program Files\\Blender Foundation"
            blenders = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
            blenders.sort()
            if len(blenders) == 0:
                print("Could not find a blender installation. Either install one to the default location or specify one with environment variable BLENDER_PATH")
            blender = os.path.join(blenders[-1], "blender.exe")

    blender = os.path.abspath(os.path.expanduser(blender))

    if on_mac():
        res = os.path.join(blender, "Contents/Resources")
        version = None
        for p in os.listdir(res):
            if os.path.isdir(os.path.join(res, p)):
                name = os.path.basename(p)
                if re.match(r"[23]{1}\.[0-9]{1,2}", name):
                    version = name
        
        addon_path = "".join(["~/Library/Application Support/Blender/", version, "/scripts/addons"])
        addon_path = os.path.abspath(os.path.expanduser(addon_path))
        if addon_name:
            addon = os.path.join(addon_path, addon_name)
        else:
            addon = None
        
        python_folder = os.path.join(blender, "Contents/Resources", version, "python/bin")
        python = None

        for f in os.listdir(python_folder):
            name = os.path.basename(f)
            if name.startswith("python"):
                python = os.path.join(python_folder, f)

        blender_executable = os.path.join(blender, "Contents/MacOS/Blender")

        return {
            "addon_name": addon_name,
            "addon_source": addon_source,
            "addon_path": addon_path,
            "addon": addon,
            "python": python,
            "blender": blender_executable
        }
    elif on_windows():
        version = None
        parent = os.path.dirname(blender)
        
        for p in os.listdir(parent):
            if os.path.isdir(os.path.join(parent, p)):
                name = os.path.basename(p)
                if re.match(r"[23]{1}\.[0-9]{1,2}", name):
                    version = name
        
        python_folder = os.path.join(parent, version, "python\\bin")
        python = os.path.join(python_folder, "python.exe")

        blenders_appdata = os.path.abspath(os.path.expanduser("~\\AppData\\Roaming\\Blender Foundation\\Blender"))
        addon_path = os.path.join(blenders_appdata, version, "scripts\\addons")

        if addon_name:
            addon = os.path.join(addon_path, addon_name)
        else:
            addon = None

        blender_executable = blender

        return {
            "addon_name": addon_name,
            "addon_source": addon_source,
            "addon_path": addon_path,
            "addon": addon,
            "python": python,
            "blender": blender_executable
        }


def inline_dependencies(vars):
    addon_source = vars.get("addon_source")
    parent = os.path.dirname(addon_source)
    venv = os.path.join(parent, "venv")

    if not os.path.exists(venv):
        print("no venv found!")
        return
    
    if on_windows():
        packages = os.path.join(venv, "Lib", "site-packages")
    else:
        packages = glob.glob(os.path.join(venv, "lib", "*", "site-packages"))
        if packages and os.path.exists(packages[0]):
            packages = packages[0]
    print(packages)
    shutil.copytree(packages, os.path.join(addon_source, "inline-packages"))


def fill_out_python(vars):
    python = vars.get("python")
    python_version = subprocess.check_output([python, "--version"]).split(" ")[-1].strip()

    #import urllib.request
    import shutil
    import requests, tarfile, tempfile

    package = os.path.dirname(os.path.abspath(__file__))
    versions_folder = os.path.join(package, "versions")
    version_folder = os.path.join(versions_folder, python_version)
    if not os.path.exists(versions_folder):
        os.mkdir(versions_folder)
    if not os.path.exists(version_folder):
        os.mkdir(version_folder)

    def download(version):
        tgz = "".join(["https://www.python.org/ftp/python/", version, "/Python-", version, ".tgz"])
        print(tgz)
        response = requests.get(tgz, stream=True)
        
        file = tarfile.open(fileobj=response.raw, mode="r|gz")

        file.extractall(path=version_folder)
        src = os.path.join(version_folder, ("Python-" + version + "/Include"))
        dst_include = os.path.join(os.path.dirname(os.path.dirname(python)),  "include")
        dst = os.path.join(dst_include, os.listdir(dst_include)[0])

        for f in os.listdir(src):
            src_fp = os.path.join(src, f)
            dst_fp = os.path.join(dst, f)

            print("---")
            print(src_fp)
            print(dst_fp)

            if os.path.isdir(src_fp):
                shutil.copytree(src_fp, dst_fp)
            else:
                shutil.copy2(src_fp, dst_fp)

    download(python_version)
    print("done")


def install(vars):
    addon_source = vars.get("addon_source")
    addon = vars.get("addon")
    
    if os.path.exists(addon):
        os.unlink(addon)

    if on_mac():
        subprocess.call(["ln", "-s", addon_source, addon])
        print("SOURCE", addon_source)
        print("SYMLINK", addon)
    elif on_windows():
        os.makedirs(os.path.dirname(addon), exist_ok=True)
        os.symlink(addon_source, addon)


def uninstall(vars):
    addon_source = vars.get("addon_source")
    addon = vars.get("addon")

    if on_mac():
        if os.path.exists(addon): os.unlink(addon)
        print("Uninstalled symlink:", addon)
        #subprocess.call(["ln", "-s", addon_source, addon])
        #print("SOURCE", addon_source)
        #print("SYMLINK", addon)


def release(vars, suffix=None):
    import zipfile, re

    addon_name = vars.get("addon_name")
    init = os.path.join(root, addon_name, "__init__.py")
    
    with open(init, "r") as f:
        version_match = re.search(r"\"version\"\:\s\(([0-9]{1}),\s?([0-9]{1,2})\)", f.read())
        #mj, mn = version_match[1], version_match[2]

    mj, mn = version_match.groups()

    releases = os.path.join(root, "_releases")

    if not os.path.exists(releases):
        os.mkdir(releases)

    release_name = "ST2-v" + mj + "-" + mn
    if suffix:
        release_name = release_name + "_" + suffix
    
    release = os.path.join(releases, release_name + ".zip")
    if os.path.exists(release):
        os.unlink(release)

    zf = zipfile.ZipFile(release, "w")
    for file in os.listdir(addon_name):
        f = os.path.join(addon_name, file)
        if not os.path.isdir(f):
            print("> " + f)
            zf.write(f)
        else:
            if "inline-packages" in f:
                for _root, _dirs, _files in os.walk(f):
                    for _file in _files:
                        if ("__pycache__" not in _root
                            #and "/pkg_resources/" not in _root
                            #and "/setuptools/" not in _root
                            #and "/pip-" not in _root
                            #and "/pip/" not in _root
                            ):
                            print(os.path.join(_root, _file))
                            zf.write(os.path.join(_root, _file))
    zf.close()


def for_alias(s):
    if on_windows():
        s = '"' + os.path.abspath(s).replace('\\', '/') + '"'
        s = s.replace("C:", "/c")
    return s

version = "0.0.9"

def print_header():
    print(
""" _   ___   _             
| |_|_  |_| |___ ___ _ _ 
| . |_  | . | -_|   | | |
|___|___|___|___|_|_|\_/ v""" + version)


def main():
    argv = sys.argv
    args = []

    arg_count = len(argv)
    
    for a in argv:
        args.append(a)
    
    if arg_count == 2:
        if "-v" in args or "--version" in args:
            print(version)
            return

    if arg_count == 1:
        print_header()
        return

    action = args[1]

    if action == "paths":
        vars = get_vars(None)
        out = []
        for k, v in vars.items():
           if v:
               out.append('  "' + k + '": "' + v + '"')
        print("{")
        print(",\n".join(out))
        print("}")
    elif action == "print":
        vars = get_vars(None)
        sys.stdout.write(for_alias(vars.get(args[2])))
    elif action == "blender":
        vars = get_vars(None)
        binary = str(vars.get("blender"))
        ps = []
        for p in args[2:]:
            ps.extend(p.split("="))
        ps.insert(0, binary)
        subprocess.call(ps)
    elif action == "bpy" or action == "python":
        vars = get_vars(None)
        binary = str(vars.get("python"))
        ps = []
        for p in args[2:]:
            ps.extend(p.split("="))
        ps.insert(0, binary)
        subprocess.call(ps)
    elif action == "download":
        fill_out_python(get_vars(None))
    else:
        if len(args) > 2:
            addon_name = args[2]
        else:
            addon_name = None
        
        kwargs = {}
        if len(args) > 3 and "=" in args[3]:
            pairs = [p.split("=") for p in args[3].split(",")]
            kwargs = {k:v for k,v in pairs}
        
        vars = get_vars(addon_name)

        if action == "install":
            install(vars)
        elif action == "uninstall":
            uninstall(vars)
        elif action == "show":
            addon_path = vars.get("addon_path")
            if on_mac():
                subprocess.call(["open", addon_path])
            elif on_windows():
                subprocess.call(["explorer", addon_path])
            else:
                print("not implemented for this platform")
        elif action == "release":
            release(vars, suffix=kwargs.get("suffix"))
        elif action == "inline":
            inline_dependencies(vars)
        else:
            print("Action not recognized", action)


if __name__ == "__main__":
    main()