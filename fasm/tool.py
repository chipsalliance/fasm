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

import argparse
from fasm import fasm_tuple_to_string, parse_fasm_filename


def main():
    parser = argparse.ArgumentParser('FASM tool')
    parser.add_argument('file', help='Filename to process')
    parser.add_argument(
        '--canonical',
        action='store_true',
        help='Return canonical form of FASM.')

    args = parser.parse_args()

    fasm_tuples = parse_fasm_filename(args.file)

    print(fasm_tuple_to_string(fasm_tuples, args.canonical))


if __name__ == '__main__':
    main()
