#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from warnings import warn

available = []
""" List of parser submodules available. Strings should match module names. """

try:
    from fasm.parser.antlr import \
        parse_fasm_filename, parse_fasm_string, implementation
    available.append('antlr')
except ImportError as e:
    warn(
        """Unable to import fast Antlr4 parser implementation.
  ImportError: {}

  Falling back to the much slower pure Python textX based parser
  implementation.

  Getting the faster antlr parser can normally be done by installing the
  required dependencies and then reinstalling the fasm package with:
    pip uninstall
    pip install -v fasm
""".format(e), RuntimeWarning)
    from fasm.parser.textx import \
        parse_fasm_filename, parse_fasm_string, implementation

# The textx parser is available as a fallback.
available.append('textx')
