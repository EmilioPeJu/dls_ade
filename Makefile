# Specify defaults for testing
PREFIX := $(shell pwd)/prefix
PYTHON = dls-python
MODULEVER = 0.0

# Override with any release info
-include Makefile.private

build: setup.py $(wildcard */*.py)
	$(PYTHON) setup.py build

clean:
	$(PYTHON) setup.py clean
	-rm -rf build installed.files
	-find -name '*.pyc' -exec rm {} \;

install:
	MODULEVER=$(MODULEVER) $(PYTHON) setup.py install \
		--record installed.files \
		--prefix $(PREFIX)

.PHONY: clean install
