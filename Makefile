# Specify where we should build for testing
PREFIX=/scratch/tools
INSTALL_DIR=$(PREFIX)/lib/python2.6/site-packages
SCRIPT_DIR=$(PREFIX)/bin
PYTHON=$(SCRIPT_DIR)/dls-python2.6

build: setup.py $(wildcard dls_scripts/*.py)
	$(PYTHON) setup.py build

clean:
	$(PYTHON) setup.py clean
	-rm -rf build dist *egg-info installed.files
	-find -name '*.pyc' -exec rm {} \;

SCRIPTS=$(wildcard other_scripts/*.pl) $(wildcard other_scripts/*.sh)

install: $(patsubst other_scripts/%,$(SCRIPT_DIR)/%,$(SCRIPTS))
	$(PYTHON) setup.py install \
		--record installed.files \
		--install-lib $(INSTALL_DIR) \
		--install-script $(SCRIPT_DIR)
			
$(SCRIPT_DIR)/%: other_scripts/%
	install $^ $@
	
