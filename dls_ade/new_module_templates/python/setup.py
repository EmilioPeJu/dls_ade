from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

setup(
#    install_requires = ['cothread'], # require statements go here
    name = '{module_name:s}',
    version = version,
    description = 'Module',
    author = '{user_login:s}',
    author_email = '{user_login:s}@fed.cclrc.ac.uk',
    packages = ['{module_name:s}'],
#    entry_points = {{'console_scripts': ['test-python-hello-world = {module_name:s}.{module_name:s}:main']}}, # this makes a script
#    include_package_data = True, # use this to include non python files
    zip_safe = False
    )
