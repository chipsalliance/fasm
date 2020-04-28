# Minimal makefile for Sphinx documentation
#

SHELL = /bin/bash
MAKEDIR := $(dir $(lastword $(MAKEFILE_LIST)))

# You can set these variables from the command line.
SPHINXOPTS      =
SPHINXBUILD     = [ -e env/bin/activate ] && source env/bin/activate; sphinx-build
SPHINXAUTOBUILD = [ -e env/bin/activate ] && source env/bin/activate; sphinx-autobuild
SPHINXPROJ      = SymbiFlowV2X
SOURCEDIR       = .
BUILDDIR        = _build
OSFLAG          =
UNAME_S := $(shell uname -s)
ifneq (, $(findstring Linux, $(UNAME_S)))
	OSFLAG := Linux
endif
ifeq ($(UNAME_S), Darwin)
	OSFLAG := MacOSX
endif
ifneq (, $(findstring Cygwin, $(UNAME_S)))
	OSFLAG := Linux
endif
ifneq (, $(findstring MINGW, $(UNAME_S)))
	OSFLAG := Linux
endif


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml:
	@$(SPHINXAUTOBUILD) -b html --ignore \*.swp --ignore \*~ $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/html"

.PHONY: help livehtml Makefile


env/Miniconda3-latest-$(OSFLAG)-x86_64.sh:
	mkdir env
	wget https://repo.anaconda.com/miniconda/Miniconda3-latest-$(OSFLAG)-x86_64.sh -O env/Miniconda3-latest-$(OSFLAG)-x86_64.sh
	chmod a+x env/Miniconda3-latest-$(OSFLAG)-x86_64.sh

env:
	rm -rf env
	make env/Miniconda3-latest-$(OSFLAG)-x86_64.sh
	./env/Miniconda3-latest-$(OSFLAG)-x86_64.sh -p $(PWD)/env -b -f
	source env/bin/activate; conda config --system --add envs_dirs $(PWD)/env/envs
	source env/bin/activate; conda config --system --add pkgs_dirs $(PWD)/env/pkgs
	source env/bin/activate; conda env update --name base --file ./environment.yml

.PHONY: env
