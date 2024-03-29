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

# ** WARNING **
# This file is auto-generated by the update_version.py script.
# ** WARNING **

version_str = "0.0.2.post66"
version_tuple = (0, 0, 2, 66)
try:
    from packaging.version import Version as V
    pversion = V("0.0.2.post66")
except ImportError:
    pass

git_hash = "c0b734e6d373fcffd0522acdd102814bcefb626a"
git_describe = "v0.0.2-66-gc0b734e"
git_msg = """\
commit c0b734e6d373fcffd0522acdd102814bcefb626a
Author: Tim 'mithro' Ansell <me@mith.ro>
Date:   Fri Feb 19 13:05:20 2021 -0800

    Improve the warning message when falling back to the textX.

    Signed-off-by: Tim 'mithro' Ansell <me@mith.ro>

"""
