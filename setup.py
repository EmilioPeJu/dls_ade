from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

# find our scripts
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "py_scripts"))
entry_points = [ x.replace('_','-') + " = py_scripts." + x[:-3] + ":"+x.replace('dls_','')[:-3] 
                    for x in os.listdir(script_dir) if x.endswith(".py") and x != "__init__.py" ]
install_requires = [
    'dls_environment==4.5',
    'dls_release==1.0',
    'cx_Oracle==5.0.4',
    'dls_serial_sim==1.17',
    'iocbuilder==3.34',
    'python-ldap==2.3.12',
    'numpy==1.6.2',
    'cothread==2.8']

setup(
    # name of the module
    name = "dls_scripts",
    # version: over-ridden by the release script
    version = version,
    description = 'Various Diamond helper scripts',
    author = 'Diamond Light Source Controls Group',
    install_requires = install_requires,
    packages = ["py_scripts","dls_scripts"],
    package_data = {'dls_scripts' : ["def_config.cfg", "COPYING", "COPYING.LESSER"] },
    # define console_scripts
    entry_points = { 'console_scripts': entry_points },
    zip_safe = False
    )
