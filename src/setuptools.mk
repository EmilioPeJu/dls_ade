# Author: Diamond Light Source, Copyright 2008
#
# License: This file is part of 'dls.environment'
# 
# 'dls.environment' is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# 'dls.environment' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with 'dls.environment'.  If not, see <http://www.gnu.org/licenses/>.

# This makefile builds a versioned python egg of the diamond namespace
# install with easy_install
# see http://peak.telecommunity.com/DevCenter/setuptools

# the python executable you want to use
PYTHON=python2.4
# the place you want to install python scripts using the install target
SCRIPT_DIR=/dls_sw/tools/bin
# by default, the eggs are installed to python's site-packages directory
# for the test target, install to $TEST_INSTALL_DIR instead
# you need to do export PYTHONPATH=$TEST_INSTALL_DIR before trying to use
# setuptools to find the test eggs
TEST_INSTALL_DIR=/dls_sw/work/common/python/test/packages
# the place you want to install python scripts using the test target
TEST_SCRIPT_DIR=/dls_sw/work/common/python/test/scripts
# dls_install installs versioned, commented scripts, easy_install is the
# default install that just puts the scripts in SCRIPT_DIR or TEST_SCRIPT_DIR
INSTALL_TYPE=dls_install

# all target just does dist, can safely add other targets to all
# e.g you might want to do this in some other python module with a PyQT gui:
# TARGETS = $(patsubst %.ui, %_uic.py, $(wildcard src/*.ui))
# %_uic.py: %.ui
#	pyuic2.4 $< > $@
# all: $(TARGETS) dist
all: dist

# clean target just does remove, can safely add other targets to all
# e.g. you might want to do this:
# clean: remove
#	-rm $(TARAGETS)
clean: remove

# some hacking to make dls modules import as dls.<module_name>
dls/__init__.py:
	-mkdir dls
	-echo -e "__import__('pkg_resources').declare_namespace(__name__)" >> dls/__init__.py

# create the egg
dist: dls/__init__.py setup.py
	$(PYTHON) setup.py bdist_egg

# cleanup
remove:
	$(PYTHON) setup.py clean
	-rm -rf build dist *egg-info dls
	-find -iname '*.pyc' -exec rm {} \;
	-find -iname '*~' -exec rm {} \;

# install the egg and scripts in the install location
install: all
	$(PYTHON) setup.py $(INSTALL_TYPE) -m --script-dir=$(SCRIPT_DIR) dist/*.egg

# install the egg and scripts in the test location	
test: all
	$(PYTHON) setup.py $(INSTALL_TYPE) -m --install-dir=$(TEST_INSTALL_DIR) --script-dir=$(TEST_SCRIPT_DIR) dist/*.egg
