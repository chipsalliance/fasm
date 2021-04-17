# Copyright (C) 2017-2021  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# The top directory where environment will be created.
TOP_DIR := $(realpath $(dir $(lastword $(MAKEFILE_LIST))))

# A pip `requirements.txt` file.
# https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format
REQUIREMENTS_FILE := requirements.txt

# A conda `environment.yml` file.
# https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html
ENVIRONMENT_FILE := environment.yml

# Rule to checkout the git submodule if it wasn't cloned.
$(TOP_DIR)/third_party/make-env/conda.mk: $(TOP_DIR)/.gitmodules
	cd $(TOP_DIR); git submodule update --init third_party/make-env
	touch $(TOP_DIR)/third_party/make-env/conda.mk

-include $(TOP_DIR)/third_party/make-env/conda.mk

# Update the version file
# ------------------------------------------------------------------------
fasm/version.py: update_version.py | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) python ./update_version.py

setup.py: fasm/version.py
	touch setup.py --reference fasm/version.py

# Build/install into the conda environment.
# ------------------------------------------------------------------------
build-clean:
	rm -rf build dist fasm.egg-info
	rm -f fasm/parser/antlr_to_tuple.c
	rm -f fasm/parser/*.so

clean:: build-clean

.PHONY: build-clean

build: setup.py | $(CONDA_ENV_PYTHON)
	make build-clean
	$(IN_CONDA_ENV) python setup.py sdist bdist_wheel

.PHONY: build

# Install into environment
install: setup.py | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) python setup.py develop

.PHONY: install

# Info about the environment
info:
	@make --no-print-directory env-info
	@echo
	@$(IN_CONDA_ENV) python -W ignore .github/actions/download-and-run-tests/fasm-version.py

.PHONY: info

# Build/install locally rather than inside the environment.
# ------------------------------------------------------------------------
local-build: setup.py
	python setup.py build

.PHONY: local-build

local-build-shared: setup.py
	python setup.py build --antlr-runtime=shared

.PHONY: local-build-shared

local-install: setup.py
	python setup.py install

.PHONY: local-install


# Test, lint, auto-format.
# ------------------------------------------------------------------------

# Run the tests
test: fasm/version.py | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) py.test -s tests

.PHONY: test

tests: test
	@true

.PHONY: tests

# Find files to apply tools to while ignoring files.
define with_files
  $(IN_CONDA_ENV) git ls-files | grep -ve '^third_party\|^\.|^env' | grep -e $(1) | xargs -r -P $$(nproc) $(2)
endef

# Lint the python files
lint: | $(CONDA_ENV_PYTHON)
	$(call with_py_files, flake8)

.PHONY: lint

# Format the python files
define with_py_files
  $(call with_files, '.py$$', $(1))
endef

PYTHON_FORMAT ?= yapf
format-py: | $(CONDA_ENV_PYTHON)
	$(call with_py_files, yapf -p -i)

.PHONY: format-py

# Format the C++ files
define with_cpp_files
  $(call with_files, '\.cpp$$\|\.h$$', $(1))
endef

format-cpp:
	$(call with_cpp_files, clang-format -style=file -i)

.PHONY: format-cpp

# Format the GitHub workflow files
GHA_WORKFLOW_SRCS = $(wildcard .github/workflows-src/*.yml)
GHA_WORKFLOW_OUTS = $(addprefix .github/workflows/,$(notdir $(GHA_WORKFLOW_SRCS)))

.github/workflows/%.yml: .github/workflows-src/%.yml $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) python -m actions_includes $< $@

format-gha: $(GHA_WORKFLOW_OUTS)
	echo $(GHA_WORKFLOW_OUTS)
	@true

# Format all the files!
format: format-py format-cpp
	true

# Check - ???
check: setup.py | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) python setup.py check -m -s

.PHONY: check

# Check files have license headers.
check-license:
	@./.github/check_license.sh

.PHONY: check-license

# Check python scripts have the correct headers.
check-python-scripts:
	@./.github/check_python_scripts.sh

.PHONY: check-python-scripts

# Upload to PyPI servers
# ------------------------------------------------------------------------

# PYPI_TEST = --repository-url https://test.pypi.org/legacy/
PYPI_TEST = --repository testpypi

# Check before uploading
upload-check: build | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) twine check dist/*

.PHONY: upload-check

# Upload to test.pypi.org
upload-test: check | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) twine upload ${PYPI_TEST}  dist/*.tar.gz
	$(IN_CONDA_ENV) twine upload ${PYPI_TEST}  dist/*.whl

.PHONY: upload-test

# Upload to the real pypi.org
upload: check | $(CONDA_ENV_PYTHON)
	$(IN_CONDA_ENV) twine upload ${PYPI_TEST}  dist/*.tar.gz
	$(IN_CONDA_ENV) twine upload ${PYPI_TEST}  dist/*.whl

.PHONY: upload
