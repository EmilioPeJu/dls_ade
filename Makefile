# Specify defaults for testing
PREFIX = /dls_sw/prod/tools/RHEL5
PYTHON = $(PREFIX)/bin/python2.6
INSTALL_DIR = /dls_sw/work/common/python/test/packages
SCRIPT_DIR = /dls_sw/work/common/python/test/scripts
MODULEVER = 0.0

# Override with any release info
-include Makefile.private

build: setup.py $(wildcard */*.py)
	$(PYTHON) setup.py build
	./patchpath.sh

clean:
	$(PYTHON) setup.py clean
	-rm -rf build installed.files
	-find -name '*.pyc' -exec rm {} \;

install:
	MODULEVER=$(MODULEVER) $(PYTHON) setup.py install \
		--record installed.files \
		--install-lib $(INSTALL_DIR) \
		--install-script $(SCRIPT_DIR)
