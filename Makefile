# Copyright (C) 2017-2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

.PHONY: build
build:
	python setup.py build

.PHONY: install
install:
	python setup.py install

.PHONY: test
test:
	py.test -s tests

PYTHON_FORMAT ?= yapf
format:
	$(IN_ENV) git ls-files | grep -ve '^third_party\|^\.' | grep -e '.py$$' | xargs -r -P $$(nproc) yapf -p -i
	flake8 .

check-license:
	@./.github/check_license.sh
	@./.github/check_python_scripts.sh

.PHONY: format-cpp
format-cpp:
	git ls-files | grep -e '\.cpp$$\|\.h$$' | xargs -r clang-format -style=file -i
