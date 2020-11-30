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

from collections import namedtuple
import enum


class ValueFormat(enum.Enum):
    """ Number format used for a FASM value. """
    PLAIN = 0  # 42
    VERILOG_DECIMAL = 1  # 8'd42
    VERILOG_HEX = 2  # 8'h2a
    VERILOG_BINARY = 3  # 8'b00101010
    VERILOG_OCTAL = 4  # 8'o52


# Python version of a SetFasmFeature line.
# feature is a string
# start and end are ints.  When FeatureAddress is missing, start=None and
# end=None.
# value is an int.
#
# When FeatureValue is missing, value=1.
# value_format determines what to output the value.
# Should be a ValueFormat or None.
# If None, value must be 1 and the value will be omited.
SetFasmFeature = namedtuple(
    'SetFasmFeature', 'feature start end value value_format')

Annotation = namedtuple('Annotation', 'name value')

# Python version of FasmLine.
# set_feature should be a SetFasmFeature or None.
# annotations should be a tuple of Annotation or None.
# comment should a string or None.
FasmLine = namedtuple('FasmLine', 'set_feature annotations comment')
