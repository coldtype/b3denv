import platform, re, os, sys, glob, subprocess, shutil, zipfile

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
            print("failed", e)
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
        blender_executable = os.path.join(blender, "Contents/MacOS/Blender")
        # output = subprocess.check_output([blender_executable, "-b", "--python-expr", "import sys;print('>>>',sys.executable)"])
        # if isinstance(output, bytes):
        #     output = output.decode("utf-8")
        #     try:
        #         python_executable = re.search(r">>> ([^\n]+)\n", output).group(1)
        #     except:
        #         raise Exception("Could not find embedded python")
        res = os.path.join(blender, "Contents/Resources")
        version = None
        for p in os.listdir(res):
            if os.path.isdir(os.path.join(res, p)):
                name = os.path.basename(p)
                if re.match(r"[234]{1}\.[0-9]{1,2}", name):
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

        return {
            "addon_name": addon_name,
            "addon_source": addon_source,
            "addon_path": addon_path,
            "addon": addon,
            "python": python,
            "version": version,
            #"python_executable": python_executable,
            #"python_match": str(python == python_executable),
            "blender": blender_executable
        }
    elif on_linux():
        blender_executable = os.path.join(blender, "blender")
        
        version = None
        for p in os.listdir(blender):
            if os.path.isdir(os.path.join(blender, p)):
                name = os.path.basename(p)
                if re.match(r"[234]{1}\.[0-9]{1,2}", name):
                    version = name
        
        addon_path = "".join(["~/.config/blender", version, "/scripts/addons"])
        addon_path = os.path.abspath(os.path.expanduser(addon_path))
        if addon_name:
            addon = os.path.join(addon_path, addon_name)
        else:
            addon = None
        
        python_folder = os.path.join(blender, version, "python/bin")
        python = None

        for f in os.listdir(python_folder):
            name = os.path.basename(f)
            if name.startswith("python"):
                python = os.path.join(python_folder, f)

        return {
            "addon_name": addon_name,
            "addon_source": addon_source,
            "addon_path": addon_path,
            "addon": addon,
            "python": python,
            "version": version,
            "blender": blender_executable
        }

    elif on_windows():
        version = None
        parent = os.path.dirname(blender)
        
        for p in os.listdir(parent):
            if os.path.isdir(os.path.join(parent, p)):
                name = os.path.basename(p)
                if re.match(r"[234]{1}\.[0-9]{1,2}", name):
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

def clean_dependencies(vars):
    addon_source = vars.get("addon_source")
    inline_packages = os.path.join(addon_source, "inline-packages")
    if os.path.exists(inline_packages):
        shutil.rmtree(inline_packages)

def inline_dependencies(vars, require_b3denv_venv=False):
    addon_source = vars.get("addon_source")
    parent = os.path.dirname(addon_source)

    b3denv_venv = os.path.join(parent, "b3denv_venv")
    venv = os.path.join(parent, "venv")
    benv = os.path.join(parent, "benv")

    primary_venv = b3denv_venv

    if not require_b3denv_venv:
        if not os.path.exists(b3denv_venv):
            primary_venv = venv
            if not os.path.exists(venv):
                primary_venv = benv
    
    if not os.path.exists(primary_venv):
        print("no b3denv_venv found!")
        return
    
    if on_windows():
        packages = os.path.join(primary_venv, "Lib", "site-packages")
    else:
        packages = glob.glob(os.path.join(primary_venv, "lib", "*", "site-packages"))
        if packages and os.path.exists(packages[0]):
            packages = packages[0]
    print(packages)
    shutil.copytree(packages, os.path.join(addon_source, "inline-packages"))


def fill_out_python(vars):
    python = vars.get("python")

    python_version_output = subprocess.check_output([python, "--version"])
    if isinstance(python_version_output, bytes):
        python_version_output = python_version_output.decode("utf-8")
    python_version = python_version_output.split(" ")[-1].strip()

    #import urllib.request
    import shutil
    import requests, tarfile, tempfile

    package = os.path.dirname(os.path.abspath(__file__))
    versions_folder = os.path.join(package, "b3denv_versions")
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
        dst_include = os.path.join(os.path.dirname(os.path.dirname(python)), "include")

        python_name = os.path.basename(python)
        
        if not os.path.exists(dst_include):
            os.mkdir(dst_include)
        
        if not os.path.exists(os.path.join(dst_include, python_name)):
            os.mkdir(os.path.join(dst_include, python_name))
        
        dst = os.path.join(dst_include, os.listdir(dst_include)[0])

        for f in os.listdir(src):
            src_fp = os.path.join(src, f)
            dst_fp = os.path.join(dst, f)

            print("---")
            print(src_fp)
            print(dst_fp)

            try:
                if os.path.isdir(src_fp):
                    shutil.copytree(src_fp, dst_fp)
                else:
                    shutil.copy2(src_fp, dst_fp)
            except OSError:
                pass
        
        #dst_headers_symlink = os.path.join(os.path.dirname(dst_include), "Headers")
        #os.symlink(dst, dst_headers_symlink)

    download(python_version)
    print("done")


def install(vars):
    uninstall(vars)

    addon_source = vars.get("addon_source")
    addon = vars.get("addon")

    if on_mac() or on_linux():
        subprocess.call(["ln", "-s", addon_source, addon])
        print("SOURCE", addon_source)
        print("SYMLINK", addon)
    elif on_windows():
        os.makedirs(os.path.dirname(addon), exist_ok=True)
        os.symlink(addon_source, addon)


def uninstall(vars):
    addon = vars.get("addon")

    if os.path.exists(addon):
        if os.path.islink(addon):
            os.unlink(addon)
            print("Uninstalled symlink:", addon)
        else:
            shutil.rmtree(addon)
            print("Uninstalled source:", addon)


def release(vars, inline=False, suffix=None):
    setup(vars, do_install=False, inline=inline)

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

    release_name = addon_name + "-v" + mj + "-" + mn
    if suffix:
        release_name = release_name + "_Blender" + vars.get("version") + "_" + suffix
    
    release = os.path.join(releases, release_name + ".zip")
    if os.path.exists(release):
        os.unlink(release)

    zf = zipfile.ZipFile(release, "w")

    for file in os.listdir(addon_name):
        f = os.path.join(addon_name, file)
        if not os.path.isdir(f) and ".DS_Store" not in f:
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


def setup(vars, inline=False, do_install=True):
    uninstall(vars)
    
    if inline:
        venv = "b3denv_venv"
        if os.path.exists(venv):
            shutil.rmtree(venv)

        blender_python = vars.get("python")
        subprocess.call([blender_python, "-m", "venv", venv])

        venv_python = os.path.join(venv, "bin", "python")
        if not os.path.exists(venv_python):
            venv_python = os.path.join(venv, "Scripts", "python.exe")
        
        print(">", venv_python)
        subprocess.call([venv_python, "--version"])

        requirements = "requirements_mac.txt"
        if on_windows():
            requirements = "requirements_win.txt"
        elif on_linux():
            requirements = "requirements_lin.txt"
        
        subprocess.call([venv_python, "-m", "pip", "install", "-r", requirements])

    clean_dependencies(vars)
    if inline:
        inline_dependencies(vars, require_b3denv_venv=True)
    if do_install:
        install(vars)


def addon(vars):
    # third-party use of an addon that spec'd to work with b3denv
    # download the git repo to a folder
    # cd into the folder?
    # run setup on the addon
    
    addon_name = vars.get("addon_name")

    def download_git_repo(url):
        dest_folder = addon_name

        git_url = "https://github.com/"
        zip_url = url + "/archive/master.zip"
        response = urllib2.urlopen(zip_url)
        
        # Save the zip file
        zip_file_path = os.path.join(dest_folder + ".zip")
        with open(zip_file_path, "wb") as f:
            f.write(response.read())

        print("Repo '{}' downloaded as '{}.zip'.".format(url, dest_folder))

        # Unzip the downloaded file
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(dest_folder)

        print("Repo '{}' unzipped to '{}'.".format(url, dest_folder))

    # Example usage
    url = "https://github.com/username/repo"
    download_git_repo(url)


def for_alias(s):
    if on_windows():
        s = '"' + os.path.abspath(s).replace('\\', '/') + '"'
        s = s.replace("C:", "/c")
    return s

def show_in_finder(path):
    if on_mac() or on_linux():
        subprocess.call(["open", path])
    elif on_windows():
        subprocess.call(["explorer", path])
    else:
        print("show not implemented for this platform")

version = "0.0.19"

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
            print_header()
            return

    if arg_count == 1:
        print_header()
        vars = get_vars(None)
        current_blender = vars.get("blender")
        print("-"*len(str(current_blender)))
        print(current_blender)
        print("-"*len(str(current_blender)))
        action = "blender"
    else:
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
    elif action == "blender" or action == "b":
        vars = get_vars(None)
        binary = str(vars.get("blender"))
        ps = []
        for p in args[2:]:
            ps.extend(p.split("="))
        ps.insert(0, binary)
        print(ps)
        subprocess.call(ps)
    elif action == "bpy" or action == "python" or action == "py" or action == "p":
        vars = get_vars(None)
        binary = str(vars.get("python"))
        ps = []
        for p in args[2:]:
            ps.extend(p.split("="))
        ps.insert(0, binary)
        subprocess.call(ps)
    elif action == "download":
        fill_out_python(get_vars(None))
        print("-------------------------------")
        print("!!! You may now need to `pip install setuptools -U` to get around an issue with pip not finding Python.h correctly")
        print("-------------------------------")
    else:
        addon_name = None

        from json import load
        with open("b3denv.spec.json", "r") as file:
            spec_data = load(file)
            addon_name = spec_data.get("addon_name", None)
        
        kwargs = {}
        if len(args) > 2 and "=" in args[2]:
            pairs = [p.split("=") for p in args[2].split(",")]
            kwargs = {k:v for k,v in pairs}
        
        vars = get_vars(addon_name)

        if action == "addon":
            addon(vars)
        elif action == "setup":
            setup(vars, inline=bool(kwargs.get("inline")))
        elif action == "install":
            install(vars)
        elif action == "uninstall":
            uninstall(vars)
        elif action == "show":
            if addon_name in ["blender", "python"]:
                show_in_finder(os.path.dirname(vars.get(addon_name)))
            else:
                addon_path = vars.get("addon_path")
                show_in_finder(addon_path)
        elif action == "release":
            release(vars, suffix=kwargs.get("suffix"), inline=bool(kwargs.get("inline")))
        elif action == "inline":
            inline_dependencies(vars)
        elif action == "clean":
            clean_dependencies(vars)
        else:
            print("Action not recognized", action)


if __name__ == "__main__":
    main()