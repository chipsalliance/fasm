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

from __future__ import print_function
import textx
import os.path
from fasm.model import \
    ValueFormat, SetFasmFeature, Annotation, FasmLine

implementation = 'textx'
"""
Module name of the default parser implementation, accessible as fasm.parser
"""


def assert_max_width(width, value):
    """ asserts if the value is greater than the width. """
    assert value < (2**width), (width, value)


def verilog_value_to_int(verilog_value):
    """ Convert VerilogValue model to width, value, value_format """
    width = None

    if verilog_value.plain_decimal:
        return width, int(verilog_value.plain_decimal), ValueFormat.PLAIN

    if verilog_value.width:
        width = int(verilog_value.width)

    if verilog_value.hex_value:
        value = int(verilog_value.hex_value.replace('_', ''), 16)
        value_format = ValueFormat.VERILOG_HEX
    elif verilog_value.binary_value:
        value = int(verilog_value.binary_value.replace('_', ''), 2)
        value_format = ValueFormat.VERILOG_BINARY
    elif verilog_value.decimal_value:
        value = int(verilog_value.decimal_value.replace('_', ''), 10)
        value_format = ValueFormat.VERILOG_DECIMAL
    elif verilog_value.octal_value:
        value = int(verilog_value.octal_value.replace('_', ''), 8)
        value_format = ValueFormat.VERILOG_OCTAL
    else:
        assert False, verilog_value

    if width is not None:
        assert_max_width(width, value)

    return width, value, value_format


def set_feature_model_to_tuple(set_feature_model):
    start = None
    end = None
    value = 1
    address_width = 1
    value_format = None

    if set_feature_model.feature_address:
        if set_feature_model.feature_address.address2:
            end = int(set_feature_model.feature_address.address1, 10)
            start = int(set_feature_model.feature_address.address2, 10)
            address_width = end - start + 1
        else:
            start = int(set_feature_model.feature_address.address1, 10)
            end = None
            address_width = 1

    if set_feature_model.feature_value:
        width, value, value_format = verilog_value_to_int(
            set_feature_model.feature_value)

        if width is not None:
            assert width <= address_width

        assert value < (2**address_width), (value, address_width)

    return SetFasmFeature(
        feature=set_feature_model.feature,
        start=start,
        end=end,
        value=value,
        value_format=value_format,
    )


def get_fasm_metamodel():
    return textx.metamodel_from_file(
        file_name=os.path.join(os.path.dirname(__file__), 'fasm.tx'),
        skipws=False)


def fasm_model_to_tuple(fasm_model):
    """ Converts FasmFile model to list of FasmLine named tuples. """
    if not fasm_model:
        return

    for fasm_line in fasm_model.lines:
        set_feature = None
        annotations = None
        comment = None

        if fasm_line.set_feature:
            set_feature = set_feature_model_to_tuple(fasm_line.set_feature)

        if fasm_line.annotations:
            annotations = tuple(
                Annotation(
                    name=annotation.name,
                    value=annotation.value if annotation.value else '')
                for annotation in fasm_line.annotations.annotations)

        if fasm_line.comment:
            comment = fasm_line.comment.comment

        yield FasmLine(
            set_feature=set_feature,
            annotations=annotations,
            comment=comment,
        )


def parse_fasm_string(s):
    """ Parse FASM string, returning list of FasmLine named tuples.

    >>> parse_fasm_string('a.b.c = 1')[0].set_feature.feature
    'a.b.c'

    Args:
        s: The string containing FASM source to parse.

    Returns:
        A list of fasm.model.FasmLine.
    """
    return fasm_model_to_tuple(get_fasm_metamodel().model_from_str(s))


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
    return fasm_model_to_tuple(get_fasm_metamodel().model_from_file(filename))
