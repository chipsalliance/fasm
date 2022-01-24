#!/usr/bin/env bash
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

echo
echo "==================================="
echo "Check Python UTF coding and shebang"
echo "==================================="
echo

ERROR_FILES_SHEBANG=""
ERROR_FILES_UTF_CODING=""
FILES_TO_CHECK=`git ls-files | grep -ve '^third_party\|^\.' | grep -e '.py$'`

for file in $FILES_TO_CHECK; do
    echo "Checking $file"
    grep -q "\#\!/usr/bin/env python3" $file || ERROR_FILES_SHEBANG="$ERROR_FILES_SHEBANG $file"
    grep -q "\#.*coding: utf-8" $file || ERROR_FILES_UTF_CODING="$ERROR_FILES_UTF_CODING $file"
done

if [ ! -z "$ERROR_FILES_SHEBANG" ]; then
    for file in $ERROR_FILES_SHEBANG; do
        echo "ERROR: $file does not have the python3 shebang."
    done
    exit 1
fi

if [ ! -z "$ERROR_FILES_UTF_CODING" ]; then
    for file in $ERROR_FILES_UTF_CODING; do
        echo "ERROR: $file does not have the UTF encoding set."
	echo "Add # coding: utf-8"
    done
    exit 1
fi

echo
