# Copyright (C) 2017-2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi;
env: requirements.txt
	python3 -mvenv env
	$(IN_ENV) pip install --upgrade -r requirements.txt

define with_files
  $(IN_ENV) git ls-files | grep -ve '^third_party\|^\.' | grep -e $(1) | xargs -r -P $$(nproc) $(2)
endef

define with_py
  $(call with_files, '.py$$', $(1))
endef

define with_c
  $(call with_files, '\.cpp$$\|\.h$$', $(1))
endef

# These checks should be run before pushing to save time.
.PHONY: quick-checks
quick-checks: format lint check format-cpp build test check-license check-python-scripts

PYTHON_FORMAT ?= yapf
.PHONY: format
format:
	$(call with_py, yapf -p -i)

.PHONY: lint
lint:
	$(call with_py, flake8)

.PHONY: format-cpp
format-cpp:
	$(call with_c, clang-format -style=file -i)

.PHONY: build install clean develop
build install clean develop:
	$(IN_ENV) python setup.py $@

.PHONY: build-shared
build-shared:
	$(IN_ENV) python setup.py build --antlr-runtime=shared

.PHONY: check
check:
	$(IN_ENV) python setup.py check -m -s

.PHONY: test
test:
	$(IN_ENV) py.test -s tests

.PHONY: check-license
check-license:
	@./.github/check_license.sh

.PHONY: check-python-scripts
check-python-scripts:
	@./.github/check_python_scripts.sh
