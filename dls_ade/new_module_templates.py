# py_mod_files: initial files for a python module

py_files = {}

py_files['setup.py'] = """from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

setup(
#    install_requires = ['cothread'], # require statements go here
    name = '%s',
    version = version,
    description = 'Module',
    author = '%s',
    author_email = '%s@fed.cclrc.ac.uk',
    packages = ['%s'],
#    entry_points = {'console_scripts': ['test-python-hello-world = %s.%s:main']}, # this makes a script
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
dist: setup.py $(wildcard %s/*.py)
\tMODULEVER=$(MODULEVER) $(PYTHON) setup.py bdist_egg
\ttouch dist
\t$(MAKE) -C documentation

# Clean the module
clean:
\t$(PYTHON) setup.py clean
\t-rm -rf build dist *egg-info installed.files prefix
\t-find -name '*.pyc' -exec rm {} \\;
\t$(MAKE) -C documentation clean

# Install the built egg and keep track of what was installed
install: dist
\t$(PYTHON) setup.py easy_install -m \\
\t\t--record=installed.files \\
\t\t--prefix=$(PREFIX) dist/*.egg
"""

py_files['module/module.py'] = """def main():
    print("Hello world from %s")
"""

py_files['module/__init__.py'] = ""

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
PROJECT_NAME           = %(module)s
PROJECT_NUMBER         =
# use <module>.<func> instead of <module>::<func>
OPTIMIZE_OUTPUT_JAVA   = YES
# need this to get all function/variable docs
SHOW_NAMESPACES        = YES
# add the input dir
INPUT                 += ../%(module)s .
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
\mainpage %(module)s Python Module
\section intro_sec Introduction
I'm going to describe the module here, possibly with a <a href="http://www.google.co.uk">web link to the manufacturers webpage</a>. \n
You can also link to \ref %(module)s.py "internally generated documentation" with alternate text, or by just by mentioning its name, e.g. %(module)s.py

\section Installation

Type make && make install

\section Usage

I'm going to describe how to use the module here
*/
"""

# tools_module: initial files for a tools module

tools_files = {}

tools_files['build'] = """PROGRAM=%s
VERSION=<insert version here>
# EXTENSION=<The tar or zip extension, defaults to .tar.gz.>
# TAR_FILE=<The tar file name or list of tar files. Defaults to ${PROGRAM}-${VERSION}${EXTENSION}>

build()
{
    # Insert build instructions here. For example, for a Python tool with a setupegg.py:
    # setuptools_build setupegg.py
}

# vim: set filetype=sh:
"""