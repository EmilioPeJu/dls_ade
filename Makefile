# Specify defaults for testing
PREFIX := $(shell pwd)/prefix
PYTHON = dls-python
MODULEVER = 0.0

# Override with any release info
-include Makefile.private

.DEFAULT_GOAL := dist

dist: setup.py $(wildcard */*.py)
	MODULEVER=$(MODULEVER) $(PYTHON) setup.py bdist_egg
	touch dist

clean:
	$(PYTHON) setup.py clean
	-rm -rf build dist *egg-info installed.files
	-rm -rf prefix
	-find -name '*.pyc' -exec rm -f {} \;

install: dist
	mkdir -p $(PREFIX)/lib/python2.7/site-packages
	$(PYTHON) setup.py easy_install -m \
		--record=installed.files \
		--prefix $(PREFIX) dist/*.egg

.PHONY: clean install
