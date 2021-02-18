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

import os.path

from fasm.model import ValueFormat, SetFasmFeature, Annotation, FasmLine
from fasm.parser import parse_fasm_filename, parse_fasm_string

try:
    from fasm.version import version_str
except ImportError:
    version_str = "UNKNOWN"
__dir__ = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
__version__ = version_str


def fasm_value_to_str(value, width, value_format):
    """ Convert value from SetFasmFeature to a string. """
    if value_format == ValueFormat.PLAIN:
        return '{}'.format(value)
    elif value_format == ValueFormat.VERILOG_HEX:
        return "{}'h{:X}".format(width, value)
    elif value_format == ValueFormat.VERILOG_DECIMAL:
        return "{}'d{}".format(width, value)
    elif value_format == ValueFormat.VERILOG_OCTAL:
        return "{}'o{:o}".format(width, value)
    elif value_format == ValueFormat.VERILOG_BINARY:
        return "{}'b{:b}".format(width, value)
    else:
        assert False, value_format


def set_feature_width(set_feature):
    if set_feature.end is None:
        return 1
    else:
        assert set_feature.start is not None
        assert set_feature.start >= 0
        assert set_feature.end >= set_feature.start

        return set_feature.end - set_feature.start + 1


def set_feature_to_str(set_feature, check_if_canonical=False):
    """ Convert SetFasmFeature tuple to string. """
    feature_width = set_feature_width(set_feature)
    max_feature_value = 2**feature_width
    assert set_feature.value < max_feature_value

    if check_if_canonical:
        assert feature_width == 1
        assert set_feature.end is None
        if set_feature.start is not None:
            assert set_feature.start != 0
        assert set_feature.value_format is None

    feature = set_feature.feature
    address = ''
    feature_value = ''

    if set_feature.start is not None:
        if set_feature.end is not None:
            address = '[{}:{}]'.format(set_feature.end, set_feature.start)
        else:
            address = '[{}]'.format(set_feature.start)

    if set_feature.value_format is not None:
        feature_value = ' = {}'.format(
            fasm_value_to_str(
                value=set_feature.value,
                width=feature_width,
                value_format=set_feature.value_format))

    return '{}{}{}'.format(feature, address, feature_value)


def canonical_features(set_feature):
    """ Yield SetFasmFeature tuples that are of canonical form.

    EG width 1, and value 1.
    """
    if set_feature.value == 0:
        return

    if set_feature.start is None:
        assert set_feature.value == 1
        assert set_feature.end is None
        yield SetFasmFeature(
            feature=set_feature.feature,
            start=None,
            end=None,
            value=1,
            value_format=None,
        )

        return

    if set_feature.start is not None and set_feature.end is None:
        assert set_feature.value == 1

        if set_feature.start == 0:
            yield SetFasmFeature(
                feature=set_feature.feature,
                start=None,
                end=None,
                value=1,
                value_format=None,
            )
        else:
            yield SetFasmFeature(
                feature=set_feature.feature,
                start=set_feature.start,
                end=None,
                value=1,
                value_format=None,
            )

        return

    assert set_feature.start is not None
    assert set_feature.start >= 0
    assert set_feature.end >= set_feature.start

    for address in range(set_feature.start, set_feature.end + 1):
        value = (set_feature.value >> (address - set_feature.start)) & 1
        if value:
            if address == 0:
                yield SetFasmFeature(
                    feature=set_feature.feature,
                    start=None,
                    end=None,
                    value=1,
                    value_format=None,
                )
            else:
                yield SetFasmFeature(
                    feature=set_feature.feature,
                    start=address,
                    end=None,
                    value=1,
                    value_format=None,
                )


def fasm_line_to_string(fasm_line, canonical=False):
    if canonical:
        if fasm_line.set_feature:
            for feature in canonical_features(fasm_line.set_feature):
                yield set_feature_to_str(feature, check_if_canonical=True)

        return

    parts = []

    if fasm_line.set_feature:
        parts.append(set_feature_to_str(fasm_line.set_feature))

    if fasm_line.annotations and not canonical:
        annotations = '{{ {} }}'.format(
            ', '.join(
                '{} = "{}"'.format(annotation.name, annotation.value)
                for annotation in fasm_line.annotations))

        parts.append(annotations)

    if fasm_line.comment is not None and not canonical:
        comment = '#{}'.format(fasm_line.comment)
        parts.append(comment)

    if len(parts) == 0 and canonical:
        return

    yield ' '.join(parts)


def fasm_tuple_to_string(model, canonical=False):
    """ Returns string of FASM file for the model given.

    Note that calling parse_fasm_filename and then calling fasm_tuple_to_string
    will result in all optional whitespace replaced with one space.
    """

    lines = []
    for fasm_line in model:
        for line in fasm_line_to_string(fasm_line, canonical=canonical):
            lines.append(line)

    if canonical:
        lines = list(sorted(set(lines)))

    return '\n'.join(lines) + '\n'
