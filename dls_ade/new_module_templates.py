# py_files: initial files for a python module
# tools_files: initial files for a tools module
# Escape braces { with an extra brace of the same type. This is for the 'format' string method
# eg. "dict = {}" -> "dict = {{}}"

py_files = {}

py_files['setup.py'] = """from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

setup(
#    install_requires = ['cothread'], # require statements go here
    name = '{module_name:s}',
    version = version,
    description = 'Module',
    author = '{getlogin:s}',
    author_email = '{getlogin:s}@fed.cclrc.ac.uk',
    packages = ['{module_name:s}'],
#    entry_points = {{'console_scripts': ['test-python-hello-world = {module_name:s}.{module_name:s}:main']}}, # this makes a script
#    include_package_data = True, # use this to include non python files
    zip_safe = False
    )
"""

py_files['Makefile'] = """# Specify defaults for testing
PREFIX := $(shell pwd)/prefix
PYTHON = dls-python
MODULEVER=0.0

# Override with any release info
-include Makefile.private

# This is run when we type make
# It can depend on other targets e.g. the .py files produced by pyuic4
dist: setup.py $(wildcard {module_name:s}/*.py)
\tMODULEVER=$(MODULEVER) $(PYTHON) setup.py bdist_egg
\ttouch dist
\t$(MAKE) -C documentation

# Clean the module
clean:
\t$(PYTHON) setup.py clean
\t-rm -rf build dist *egg-info installed.files prefix
\t-find -name '*.pyc' -exec rm {{}} \\;
\t$(MAKE) -C documentation clean

# Install the built egg and keep track of what was installed
install: dist
\t$(PYTHON) setup.py easy_install -m \\
\t\t--record=installed.files \\
\t\t--prefix=$(PREFIX) dist/*.egg
"""

py_files['{module_name:s}/{module_name:s}.py'] = """def main():
    print("Hello world from {module_name:s}")
"""

py_files['{module_name:s}/__init__.py'] = ""

py_files['documentation/Makefile'] = """# this is the doxygen output dir
DOCDIR := doxygen

# this is the doxygen executable
DOXYGEN := doxygen

# add the documentation files to the install target
all install: $(DOCDIR)

# rule for documentation
$(DOCDIR): config.cfg manual.src
\tmkdir -p $(DOCDIR)
\t$(DOXYGEN) config.cfg

# Remove entire documentation/doxygen dir on clean
clean:
\trm -rf $(DOCDIR)
"""

py_files['documentation/index.html'] = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Documentation</title>
<!-- This tag redirects to the doxygen index -->
<meta http-equiv="REFRESH" content="0;url=doxygen/index.html"></HEAD>
<body/>
</html>
"""

py_files['documentation/config.cfg'] = """# info about project
PROJECT_NAME           = {module_name:s}
PROJECT_NUMBER         =
# use <module>.<func> instead of <module>::<func>
OPTIMIZE_OUTPUT_JAVA   = YES
# need this to get all function/variable docs
SHOW_NAMESPACES        = YES
# add the input dir
INPUT                 += ../{module_name:s} .
# add some examples
# EXAMPLE_PATH           = examples
# add the extensions
FILE_PATTERNS          = *.py manual.src
# don't warn on undocumented elements
QUIET                  = YES
# where to output to
OUTPUT_DIRECTORY       = doxygen
# where to find images
# IMAGE_PATH             = images
# create a search engine
SEARCHENGINE           = YES
# make class diagrams
CLASS_DIAGRAMS         = YES
# don't make latex output
GENERATE_LATEX         = NO
# put html in .
HTML_OUTPUT            = .
# include sources
SOURCE_BROWSER         = YES
# make everything, even if no doc strings
EXTRACT_ALL            = YES
"""

py_files['documentation/manual.src'] = r"""/**
\mainpage {module_name:s} Python Module
\section intro_sec Introduction
I'm going to describe the module here, possibly with a <a href="http://www.google.co.uk">web link to the manufacturers webpage</a>. \n
You can also link to \ref {module_name:s}.py "internally generated documentation" with alternate text, or by just by mentioning its name, e.g. {module_name:s}.py

\section Installation

Type make && make install

\section Usage

I'm going to describe how to use the module here
*/
"""

py_files['.gitignore'] = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]

# C extensions
*.so

# Distribution / packaging
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*,cover

# Translations
*.mo
*.pot

# Django stuff:
*.log

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# PyCharm and Eclipse project files
/.idea/
/.project
/.cproject
/.settings/
/.pydevproject

# DLS build dir and virtual environment
/prefix/
/venv/
/installed.files

"""

# tools_module: initial files for a tools module

tools_files = {}

tools_files['build'] = """PROGRAM={module_name:s}
VERSION=<insert version here>
# EXTENSION=<The tar or zip extension, defaults to .tar.gz.>
# TAR_FILE=<The tar file name or list of tar files. Defaults to ${{PROGRAM}}-${{VERSION}}${{EXTENSION}}>

build()
{{
    # Insert build instructions here. For example, for a Python tool with a setupegg.py:
    # setuptools_build setupegg.py
}}

# vim: set filetype=sh:
"""

default_files = {}

default_files['.gitignore'] = """bin\ndata\ndb\ndbd\ninclude\nlib\n"""  # Taken from svn:ignore statements