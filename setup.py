from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

# find our scripts
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "py_scripts"))
entry_points = [ x.replace('_','-') + " = py_scripts." + x[:-3] + ":"+x.replace('dls_','')[:-3] 
                    for x in os.listdir(script_dir) if x.endswith(".py") and x != "__init__.py" ]
install_requires = []

setup(
    # name of the module
    name = "dls_ade",
    # version: over-ridden by the release script
    version = version,
    description = 'DLS Controls Group Application Development Environment scripts',
    author = 'Diamond Light Source Controls Group',
    install_requires = install_requires,
    packages = ["py_scripts","dls_environment"],
    package_data = {},
    # define console_scripts
    entry_points = { 'console_scripts': entry_points },
    zip_safe = False
    )
