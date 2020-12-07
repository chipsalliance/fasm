#!/usr/bin/env bash
# Copyright (C) 2017-2020  The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

echo
echo "==========================="
echo "Check SPDX identifier"
echo "==========================="
echo

ERROR_FILES=""
FILES_TO_CHECK=`git ls-files | grep -ve '^third_party\|^\.' | grep -e '\.sh$\|\.py$\|\.cpp$\|\.h$\|CMakeLists.txt$\|Makefile$'`

for file in $FILES_TO_CHECK; do
    echo "Checking $file"
    grep -q "SPDX-License-Identifier" $file || ERROR_FILES="$ERROR_FILES $file"
done

if [ ! -z "$ERROR_FILES" ]; then
    for file in $ERROR_FILES; do
        echo "ERROR: $file does not have license information."
    done
    exit 1
fi
