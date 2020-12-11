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
""" Output utilities for FASM.

merge_features - Combines multiple FASM SetFasmFeature into one.
merge_and_sort - Groups and sorts FASM lines, useful for non-canonical output.

"""
import enum
from fasm import SetFasmFeature, FasmLine, ValueFormat


def is_only_comment(line):
    """ Returns True if line is only a comment. """
    return not line.set_feature and not line.annotations and line.comment


def is_only_annotation(line):
    """ Returns True if line is only an annotations. """
    return not line.set_feature and line.annotations and not line.comment


def is_blank_line(line):
    """ Returns True if line is blank. """
    return not line.set_feature and not line.annotations and not line.comment


def merge_features(features):
    """ Combines features with varying addresses but same feature.

    A[0] = 1
    A[1] = 1

    becomes

    A[1:0] = 2'b11

    and

    A[5] = 1
    A[7] = 1

    A[7:0] = 8'b10100000

    """
    # Ensure all features are for the same feature
    assert len(set(feature.feature for feature in features)) == 1

    set_bits = set()
    cleared_bits = set()

    for feature in features:
        start = 0
        end = 0
        value = 1

        if feature.start is None:
            assert feature.end is None
        else:
            start = feature.start
            if feature.end is not None:
                end = feature.end
            else:
                end = start

        if feature.value is not None:
            value = feature.value

        for bit in range(start, end + 1):
            bit_is_set = ((value >> (bit - start)) & 1) != 0
            if bit_is_set:
                assert bit not in cleared_bits
                set_bits.add(bit)
            else:
                assert bit not in set_bits
                cleared_bits.add(bit)

    max_bit = max(set_bits | cleared_bits)

    final_value = 0
    for bit in set_bits:
        final_value |= (1 << bit)

    return SetFasmFeature(
        feature=features[0].feature,
        start=0,
        end=max_bit,
        value=final_value,
        value_format=ValueFormat.VERILOG_BINARY)


class MergeModel(object):
    """ Groups and merges features.

    Grouping logic:
     - Consecutive comments will be grouped.
     - Comments groups will attach to the next non-comment entry.
     - Consecutive annotations will be grouped.
     - Empty lines will be discarded
     - Features will be grouped by their first feature part.
     - Features within the same feature with different addresses will be
       merged.

    If a feature has a comment in its group, it is not eligable for address
    merging.

    """

    class State(enum.Enum):
        """ State of grouper. """
        NoGroup = 1
        InCommentGroup = 2
        InAnnotationGroup = 3

    def __init__(self):
        self.state = MergeModel.State.NoGroup
        self.groups = []
        self.current_group = None

    def start_comment_group(self, line):
        """ Start a new group of comments.

        Requires that input line is a comment and not already in a comment
        group.

        """
        assert self.state != MergeModel.State.InCommentGroup
        assert is_only_comment(line)

        if self.current_group is not None:
            self.groups.append(self.current_group)

        self.state = MergeModel.State.InCommentGroup
        self.current_group = [line]

    def add_to_comment_group(self, line):
        assert self.state == MergeModel.State.InCommentGroup

        if is_only_comment(line):
            self.current_group.append(line)
        elif is_only_annotation(line):
            self.current_group.append(line)
            self.state = MergeModel.State.InAnnotationGroup
        else:
            if not is_blank_line(line):
                self.current_group.append(line)

            self.groups.append(self.current_group)
            self.state = MergeModel.State.NoGroup

    def start_annotation_group(self, line):
        assert self.state != MergeModel.State.InAnnotationGroup
        assert is_only_annotation(line)

        if self.current_group is not None:
            self.groups.append(self.current_group)

        self.state = MergeModel.State.InAnnotationGroup
        self.current_group = [line]

    def add_to_annotation_group(self, line):
        assert self.state == MergeModel.State.InAnnotationGroup

        if is_only_comment(line):
            self.start_comment_group(line)
        elif is_only_annotation(line):
            self.current_group.append(line)
            self.state = MergeModel.State.InAnnotationGroup
        else:
            self.groups.append(self.current_group)

            self.current_group = None
            self.state = MergeModel.State.NoGroup

            self.add_to_model(line)

    def add_to_model(self, line):
        """ Add a line to the MergeModel.

        Will be grouped per MergeModel rules.
        This method is stateful, so order of insert matters, per grouping
        rules.

        """
        if self.state == MergeModel.State.NoGroup:
            if is_only_comment(line):
                self.start_comment_group(line)
            elif is_only_annotation(line):
                self.start_annotation_group(line)
            else:
                if not is_blank_line(line):
                    self.groups.append([line])

        elif self.state == MergeModel.State.InCommentGroup:
            self.add_to_comment_group(line)

        elif self.state == MergeModel.State.InAnnotationGroup:
            self.add_to_annotation_group(line)

        else:
            assert False

    def merge_addresses(self):
        """ Merges address features when possible.

        Call after all lines have been added to the model.
        """
        for group in self.groups:
            for line in group:
                assert not is_blank_line(line)

        def find_eligable_feature(group):
            if len(group) > 1:
                return None

            if group[0].annotations:
                return None

            if group[0].comment:
                return None

            return group[0].set_feature

        eligable_address_features = {}

        non_eligable_groups = []
        non_eligable_features = set()

        for group in self.groups:
            feature = find_eligable_feature(group)

            if feature is None:
                non_eligable_groups.append(group)
                for line in group:
                    if line.set_feature is not None:
                        non_eligable_features.add(line.set_feature.feature)
            else:
                if feature.feature not in eligable_address_features:
                    eligable_address_features[feature.feature] = []

                eligable_address_features[feature.feature].append(feature)

        self.groups = non_eligable_groups

        for feature_group in eligable_address_features.values():
            if feature_group[0].feature in non_eligable_features:
                for feature in feature_group:
                    self.groups.append(
                        [
                            FasmLine(
                                set_feature=feature,
                                annotations=None,
                                comment=None)
                        ])
            else:
                if len(feature_group) > 1:
                    self.groups.append(
                        [
                            FasmLine(
                                set_feature=merge_features(feature_group),
                                annotations=None,
                                comment=None)
                        ])
                else:
                    for feature in feature_group:
                        self.groups.append(
                            [
                                FasmLine(
                                    set_feature=feature,
                                    annotations=None,
                                    comment=None)
                            ])

    def output_sorted_lines(self, zero_function=None, sort_key=None):
        """ Yields sorted FasmLine's.

        zero_function - Function that takes a feature string, and returns true
                        that feature has no bits set.  This allows tiles with
                        only zero features to be dropped.

        sort_key -      Function that takes a string argument and returns a key
                        for the first feature part. Example:

        """
        feature_groups = {}
        non_feature_groups = []

        for group in self.groups:
            is_feature_group = False
            for line in group:
                if line.set_feature:
                    group_id = line.set_feature.feature.split('.')[0]

                    if group_id not in feature_groups:
                        feature_groups[group_id] = []

                    feature_groups[group_id].append(group)
                    is_feature_group = True
                    break

            if not is_feature_group:
                non_feature_groups.append(group)

        output_groups = []

        def feature_group_key(group):
            for line in group:
                if line.set_feature:
                    assert line.set_feature.feature is not None
                    return line.set_feature.feature

            assert False

        if sort_key is None:
            group_ids = sorted(feature_groups.keys())
        else:
            group_ids = sorted(feature_groups.keys(), key=sort_key)

        for group_id in group_ids:
            flattened_group = []
            for group in sorted(feature_groups[group_id],
                                key=feature_group_key):
                flattened_group.extend(group)

            if zero_function is not None:
                if all(zero_function(line.set_feature.feature)
                       for line in flattened_group
                       if line.set_feature):
                    continue

            output_groups.append(flattened_group)

        output_groups.extend(non_feature_groups)

        for idx in range(len(output_groups)):
            for line in output_groups[idx]:
                yield line

            if idx != len(output_groups) - 1:
                yield FasmLine(
                    set_feature=None, annotations=None, comment=None)


def merge_and_sort(model, zero_function=None, sort_key=None):
    """ Given a model, groups and sorts entries.

    zero_function - Function that takes a feature string, and returns true
                    that feature has no bits set.  This allows tiles with only
                    zero features to be dropped.

    sort_key -      Function that takes a string argument and returns a key
                    for the first feature part. Example:

        A_X2Y1, A_X2Y100, A_X2Y2

        could be sorted as

        A_X2Y1, A_X2Y2, A_X2Y100

        with if the key function returns (A, 2, 1) for A_X2Y1.

    Yields FasmLine's.

    Grouping logic:
     - Consecutive comments will be grouped.
     - Comments groups will attach to the next non-comment entry.
     - Consecutive annotations will be grouped.
     - Empty lines will be discarded
     - Features will be grouped by their first feature part.
     - Features within the same feature with different addresses will be
    merged.

    Sorting logic:
     - Features will appear before raw annotations.
    """
    merged_model = MergeModel()

    for line in model:
        merged_model.add_to_model(line)

    # Add the last processed annotation or comment blocks to the model
    if merged_model.state != MergeModel.State.NoGroup:
        if merged_model.current_group is not None:
            merged_model.groups.append(merged_model.current_group)

    merged_model.merge_addresses()
    return merged_model.output_sorted_lines(
        zero_function=zero_function, sort_key=sort_key)
