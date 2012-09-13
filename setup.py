from distutils.core import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

# find our scripts
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "py_scripts"))
scripts = [os.path.join(script_dir, x) for x in os.listdir(script_dir) if x.endswith(".py") or x.endswith(".sh") ]

build_scripts = [ "dlsbuild_scripts/Linux/support.sh",
                  "dlsbuild_scripts/Linux/ioc.sh",
                  "dlsbuild_scripts/Linux/etc.sh",
                  "dlsbuild_scripts/Linux/matlab.sh",
                  "dlsbuild_scripts/Linux/python.sh",
                  "dlsbuild_scripts/Linux/tools.sh",
                  "dlsbuild_scripts/Linux/archive.sh",
                  "dlsbuild_scripts/Windows/support.bat",
                  "dlsbuild_scripts/Windows/ioc.bat" ]

setup(
    # name of the module
    name = "dls_scripts",
    # version: over-ridden by the release script
    version = version,
    packages = ["dls_scripts"],
    package_data = {'dls_scripts' : ["def_config.cfg", "COPYING", "COPYING.LESSER"]+build_scripts },
    # define console_scripts
    scripts = scripts,
    )
