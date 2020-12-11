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
    PLAIN = 0
    VERILOG_DECIMAL = 1
    VERILOG_HEX = 2
    VERILOG_BINARY = 3
    VERILOG_OCTAL = 4


ValueFormat.PLAIN.__doc__ = \
    "A decimal number without size or radix e.g. 42"
ValueFormat.VERILOG_DECIMAL.__doc__ = \
    "A decimal number with optional size e.g. 8'd42"
ValueFormat.VERILOG_HEX.__doc__ = \
    "A hexadecimal number with optional size e.g. 8'h2a"
ValueFormat.VERILOG_BINARY.__doc__ = \
    "A binary number with optional size e.g. 8'b00101010"
ValueFormat.VERILOG_OCTAL.__doc__ = \
    "An octal number with optional size e.g. 8'o52"

SetFasmFeature = namedtuple(
    'SetFasmFeature', 'feature start end value value_format')
SetFasmFeature.__doc__ = """
Python version of a SetFasmFeature line such as:
  feature[31:0] = 42

feature is a string e.g. 'feature'

start and end are ints e.g 31, 0
When FeatureAddress is missing, start=None and
end=None.

value is an int e.g. 42
When FeatureValue is missing, value=1.

value_format determines how to output the value e.g. ValueFormat.PLAIN
It should be a ValueFormat or None.
If it is None, the value must be 1 and the value will
be omitted from output.
"""
SetFasmFeature.feature.__doc__ = "Feature name (string)"
SetFasmFeature.start.__doc__ = \
    "Starting value of the feature range (int or None)"
SetFasmFeature.end.__doc__ = \
    "Ending value of the feature range (int or None)"
SetFasmFeature.value.__doc__ = \
    "FeatureValue describing the value, or None"
SetFasmFeature.value_format.__doc__ = \
    "ValueFormat describing the format of the value, or None."

Annotation = namedtuple('Annotation', 'name value')
Annotation.__doc__ = """
Python version of an Annotation, such as:
  { name = "value" }

Both name and value are strings (not None),
holding the name and value, respectively.
"""
Annotation.name.__doc__ = "Annotation name (string)"
Annotation.value.__doc__ = "Annotation value (string)"

FasmLine = namedtuple('FasmLine', 'set_feature annotations comment')
FasmLine.__doc__ = """
Python version of a FasmLine such as:
feature[31:0] = 42 { name = "value" } # comment

set_feature should be a SetFasmFeature or None.
annotations should be a list of Annotation or None.
comment should a string or None, e.g. " comment"
"""
FasmLine.set_feature.__doc__ = "SetFasmFeature or None"
FasmLine.annotations.__doc__ = "List of Annotation or None"
FasmLine.comment.__doc__ = \
    "String or none containing the line comment (after '#')"
