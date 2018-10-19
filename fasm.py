from __future__ import print_function
import textx
import os.path
import argparse
from collections import namedtuple
import enum

class ValueFormat(enum.Enum):
    PLAIN = 0
    VERILOG_DECIMAL = 1
    VERILOG_HEX = 2
    VERILOG_BINARY = 3
    VERILOG_OCTAL = 4

# Python version of a SetFasmFeature line.
# feature is a string
# start and end are ints.  When FeatureAddress is missing, start=None and end=None.
# value is an int.
#
# When FeatureValue is missing, value=1.
# value_format determines what to output the value.
# Should be a ValueFormat or None.
# If None, value must be 1 and the value will be omited.
SetFasmFeature = namedtuple('SetFasmFeature', 'feature start end value value_format')

Annotation = namedtuple('Annotation', 'name value')

# Python version of FasmLine.
# set_feature should be a SetFasmFeature or None.
# annotations should be a tuple of Annotation or None.
# comment should a string or None.
FasmLine = namedtuple('FasmLine', 'set_feature annotations comment')

def assert_max_width(width, value):
    """ Given a width and integer value, asserts if the value is greater than the width. """
    assert value < (2 ** width), (width, value)

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
        width, value, value_format = verilog_value_to_int(set_feature_model.feature_value)

        if width is not None:
            assert width <= address_width

        assert value < (2 ** address_width), (value, address_width)


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
            skipws=False
            )

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
            annotations = tuple(Annotation(name=annotation.name, value=annotation.value if annotation.value else '')
                    for annotation in fasm_line.annotations.annotations)

        if fasm_line.comment:
            comment = fasm_line.comment.comment

        yield FasmLine(
            set_feature=set_feature,
            annotations=annotations,
            comment=comment,
            )


def parse_fasm_string(s):
    """ Parse FASM string, returning list of FasmLine named tuples."""
    return fasm_model_to_tuple(get_fasm_metamodel().model_from_str(s))

def parse_fasm_filename(filename):
    """ Parse FASM file, returning list of FasmLine named tuples."""
    return fasm_model_to_tuple(get_fasm_metamodel().model_from_file(filename))

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
    max_feature_value = 2 ** feature_width
    assert set_feature.value < max_feature_value

    if check_if_canonical:
        assert feature_width == 1
        assert set_feature.end is None
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
                    value_format=set_feature.value_format
                    ))

    return '{}{}{}'.format(feature, address, feature_value)

def canonical_features(set_feature):
    """ Yield SetFasmFeature tuples that are of canonical form (e.g. width 1, and value 1). """
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

    for address in range(set_feature.start, set_feature.end+1):
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
                yield set_feature_to_str(
                    feature,
                    check_if_canonical=True)

        return

    parts = []

    if fasm_line.set_feature:
        parts.append(set_feature_to_str(fasm_line.set_feature))

    if fasm_line.annotations and not canonical:
        annotations = '{{ {} }}'.format(', '.join('{} = "{}"'.format(
            annotation.name, annotation.value)
                for annotation in fasm_line.annotations
                ))

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

def main():
    parser = argparse.ArgumentParser('FASM tool')
    parser.add_argument('file', help='Filename to process')
    parser.add_argument('--canonical', action='store_true', help='Return canonical form of FASM.')

    args = parser.parse_args()

    fasm_tuples = parse_fasm_filename(args.file)

    print(fasm_tuple_to_string(fasm_tuples, args.canonical))

if __name__ == '__main__':
    main()
