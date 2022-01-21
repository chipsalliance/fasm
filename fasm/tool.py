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

import argparse
import importlib
import fasm.parser
from fasm import fasm_tuple_to_string


def nullable_string(val):
    if not val:
        return None
    return val


def get_fasm_parser(name=None):
    module_name = None
    if name is None:
        module_name = 'fasm.parser'
    elif name in fasm.parser.available:
        module_name = 'fasm.parser.' + name
    else:
        raise Exception("Parser '{}' is not available.".format(name))
    return importlib.import_module(module_name)


def main():
    parser = argparse.ArgumentParser('FASM tool')
    parser.add_argument('file', help='Filename to process')
    parser.add_argument(
        '--canonical',
        action='store_true',
        help='Return canonical form of FASM.')
    parser.add_argument(
        '--parser',
        type=nullable_string,
        help='Select FASM parser to use. '
        'Default is to choose the best implementation available.')

    args = parser.parse_args()

    try:
        fasm_parser = get_fasm_parser(args.parser)
        fasm_tuples = fasm_parser.parse_fasm_filename(args.file)
        print(fasm_tuple_to_string(fasm_tuples, args.canonical))
    except Exception as e:
        print('Error: ' + str(e))


if __name__ == '__main__':
    main()
