#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2017-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from ctypes import CDLL, POINTER, CFUNCTYPE, c_char, c_size_t, c_char_p
import os
from fasm.parser import antlr_to_tuple
import platform
from pathlib import Path

implementation = 'antlr'
"""
Module name of the default parser implementation, accessible as fasm.parser
"""

try:
    if platform.system() == 'Darwin':
        parse_fasm_lib = "libparse_fasm.dylib"
    else:
        parse_fasm_lib = "libparse_fasm.so"

    here = Path(os.path.dirname(os.path.realpath(__file__)))
    parse_fasm = CDLL(str(here / parse_fasm_lib))
except OSError:
    raise ImportError('Could not find parse_fasm library.')


def parse_fasm_string(s):
    """ Parse FASM string, returning list of FasmLine named tuples.

    >>> parse_fasm_string('a.b.c = 1')[0].set_feature.feature
    'a.b.c'

    Args:
        s: The string containing FASM source to parse.

    Returns:
        A list of fasm.model.FasmLine.
    """
    result = [None]
    error = [None]

    # Use a closure to parse while allowing C++ to handle memory.
    @CFUNCTYPE(None, POINTER(c_char), c_size_t)
    def callback(s, n):
        data = s[:n]
        assert len(data) == n
        result[0] = antlr_to_tuple.parse_fasm_data(data)
        error[0] = None

    @CFUNCTYPE(None, c_size_t, c_size_t, c_char_p)
    def error_callback(line, position, message):
        result[0] = None
        error[0] = Exception(
            'Parse error at {}:{} - {}'.format(
                line, position, message.decode('ascii')))

    parse_fasm.from_string(bytes(s, 'ascii'), 0, callback, error_callback)

    if error[0] is not None:
        raise error[0]

    return result[0]


def parse_fasm_filename(filename):
    """ Parse FASM file, returning list of FasmLine named tuples.

    >>> parse_fasm_filename('examples/feature_only.fasm')[0]\
        .set_feature.feature
    'EXAMPLE_FEATURE.X0.Y0.BLAH'

    Args:
        filename: The file containing FASM source to parse.

    Returns:
        A list of fasm.model.FasmLine.
    """
    result = [None]
    error = [None]

    # Use a closure to parse while allowing C++ to handle memory.
    @CFUNCTYPE(None, POINTER(c_char), c_size_t)
    def callback(s, n):
        data = s[:n]
        assert len(data) == n
        result[0] = antlr_to_tuple.parse_fasm_data(data)
        error[0] = None

    @CFUNCTYPE(None, c_size_t, c_size_t, c_char_p)
    def error_callback(line, position, message):
        result[0] = None
        error[0] = Exception(
            'Parse error at {}:{} - {}'.format(
                line, position, message.decode('ascii')))

    parse_fasm.from_file(bytes(filename, 'ascii'), 0, callback, error_callback)

    if error[0] is not None:
        raise error[0]

    return result[0]
