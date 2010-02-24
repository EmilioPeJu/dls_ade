# Specify where we should build for testing
INSTALL_DIR=/dls_sw/work/tools/RHEL5/lib/python2.6/site-packages
SCRIPT_DIR=/dls_sw/work/tools/RHEL5/bin
PYTHON=/dls_sw/work/tools/RHEL5/bin/dls-python2.6

INSTALL_DIR=testlib
SCRIPT_DIR=testbin

build: setup.py $(wildcard dls_scripts/*.py)
	$(PYTHON) setup.py build

clean:
	$(PYTHON) setup.py clean
	-rm -rf build dist *egg-info installed.files
	-find -name '*.pyc' -exec rm {} \;

SHELL_SCRIPTS=$(patsubst shell_scripts/%,$(SCRIPT_DIR)/%,$(wildcard shell_scripts/*.sh))

install: $(SHELL_SCRIPTS)
	$(PYTHON) setup.py install \
		--record installed.files \
		--install-lib $(INSTALL_DIR) \
		--install-script $(SCRIPT_DIR)
			
$(SCRIPT_DIR)/%: shell_scripts/%
	install $^ $@
	
