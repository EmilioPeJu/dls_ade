from distutils.core import setup
import os

# this line allows the version to be specified in the release script
globals().setdefault('version', '0.0')

# find our scripts
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "py_scripts"))
scripts = [os.path.join(script_dir, x) for x in os.listdir(script_dir) if x.endswith(".py")]

setup(
    # name of the module
    name = "dls_scripts",
    # version: over-ridden by the release script
    version = version,
    packages = ["dls_scripts"],
    # define console_scripts
    scripts = scripts,
    )
