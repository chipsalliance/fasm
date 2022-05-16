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

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from pathlib import Path
from re import sub as re_sub
from os import environ, path as os_path, popen
# from sys import path as sys_path

# sys_path.insert(0, os_path.abspath('.'))

# -- General configuration ------------------------------------------------

project = 'FPGA Assembly (FASM)'
author = 'F4PGA Authors'
copyright = f'{author}, 2018 - 2022'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.doctest',
    'sphinx.ext.imgmath',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx_markdown_tables',
]

templates_path = ['_templates']

source_suffix = ['.rst', '.md']

master_doc = 'index'

on_rtd = environ.get('READTHEDOCS', None) == 'True'

if on_rtd:
    docs_dir = os_path.abspath(os_path.dirname(__file__))
    print("Docs dir is:", docs_dir)
    import subprocess
    subprocess.call('git fetch origin --unshallow', cwd=docs_dir, shell=True)
    subprocess.check_call('git fetch origin --tags', cwd=docs_dir, shell=True)

release = re_sub('^v', '', popen('git describe').read().strip())
# The short X.Y version.
version = release

exclude_patterns = ['_build', 'env', 'Thumbs.db', '.DS_Store']

pygments_style = 'default'

todo_include_todos = True

# -- Options for HTML output ----------------------------------------------

# Enable github links when not on readthedocs
if not on_rtd:
    html_context = {
        "display_github": True,  # Integrate GitHub
        "github_user": "chipsalliance",  # Username
        "github_repo": "fasm",  # Repo name
        "github_version": "master",  # Version
        "conf_py_path": "/docs/",
    }

html_show_sourcelink = True

html_theme = 'sphinx_f4pga_theme'

html_theme_options = {
    'repo_name': 'chipsalliance/fasm',
    'github_url': 'https://github.com/chipsalliance/fasm',
    'globaltoc_collapse': True,
    'color_primary': 'indigo',
    'color_accent': 'blue',
}

html_static_path = ['_static']

html_logo = str(Path(html_static_path[0]) / 'logo.svg')
html_favicon = str(Path(html_static_path[0]) / 'favicon.svg')

# -- Options for HTMLHelp output ------------------------------------------

htmlhelp_basename = 'f4pga-fasm'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {}

latex_documents = [
    (
        master_doc,
        'fasm.tex',
        u'F4PGA FASM Documentation',
        u'F4PGA',
        'manual',
    ),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (
        master_doc,
        'f4pga-fasm',
        u'F4PGA FASM Documentation',
        [author],
        1,
    ),
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (
        master_doc,
        'FASM',
        u'F4PGA FASM Documentation',
        author,
        'FASM',
        'One line description of project.',
        'Miscellaneous',
    ),
]

# -- Sphinx.Ext.InterSphinx -----------------------------------------------

intersphinx_mapping = {'https://docs.python.org/': None}


def setup(app):
    pass
