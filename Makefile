# Copyright (C) 2017-2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

PYTHON_FORMAT ?= yapf
format:
	$(IN_ENV) find . -name \*.py $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) yapf -p -i
