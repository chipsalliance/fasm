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

import os
import re
import setuptools
import shutil
import subprocess
import sys
import traceback

from Cython.Build import cythonize
from distutils.command.build import build
from distutils.version import LooseVersion
from setuptools import Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.develop import develop
from setuptools.command.install import install

__dir__ = os.path.dirname(os.path.abspath(__file__))

# Read in the description
with open("README.md", "r") as fh:
    long_description = fh.read()

# Read in the version information
FASM_VERSION_FILE = os.path.join(__dir__, 'fasm', 'version.py')
with open(FASM_VERSION_FILE) as f:
    version_line = [
        v.strip() for v in f.readlines() if v.startswith('version_str')
    ]
assert len(version_line) == 1, version_line
version_value = version_line[0].split(' = ', 1)[-1]
assert version_value[0] == '"', version_value
assert version_value[-1] == '"', version_value
version = version_value[1:-1]


# Based on: https://www.benjack.io/2018/02/02/python-cpp-revisited.html
# GitHub: https://github.com/benjaminjack/python_cpp_example
class CMakeExtension(Extension):
    def __init__(self, name, sourcedir='', prefix=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)
        self.prefix = prefix


# Used to share options between two classes.
class SharedOptions():
    ANTLR_RUNTIMES = ['static', 'shared']
    options = [
        (
            'antlr-runtime=', None,
            "Whether to use a 'static' or 'shared' ANTLR runtime.")
    ]

    def __init__(self):
        self.antlr_runtime = 'static'

    def initialize(self, other):
        other.antlr_runtime = None

    def load(self, other):
        if other.antlr_runtime is not None:
            self.antlr_runtime = other.antlr_runtime
            assert self.antlr_runtime in SharedOptions.ANTLR_RUNTIMES, \
                'Invalid antlr_runtime {}, expected one of {}'.format(
                    self.antlr_runtime, SharedOptions.ANTLR_RUNTIMES)


# Global to allow sharing options.
shared_options = SharedOptions()


class AntlrCMakeBuild(build_ext):
    user_options = SharedOptions.options

    def copy_extensions_to_source(self):
        original_extensions = list(self.extensions)
        self.extensions = [
            ext for ext in self.extensions
            if not isinstance(ext, CMakeExtension)
        ]
        super().copy_extensions_to_source()
        self.extensions = original_extensions

    def run(self):
        shared_options.load(self)
        try:
            super().run()

            try:
                out = subprocess.check_output(['cmake', '--version'])
            except OSError:
                raise RuntimeError(
                    "CMake must be installed to build "
                    "the following extensions: " + ", ".join(
                        e.name for e in self.extensions))

            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.7.0':
                raise RuntimeError("CMake >= 3.7.0 is required.")

            for ext in self.extensions:
                self.build_extension(ext)

        except BaseException as e:
            print(
                "Failed to build ANTLR parser, "
                "falling back on slower textX parser. Error:\n", e)
            traceback.print_exc()

    # FIXME: Remove this function - https://github.com/SymbiFlow/fasm/issues/50
    def add_flags(self):
        if sys.platform.startswith('win'):
            return

        for flag in ["CFLAGS", "CXXFLAGS"]:
            flags = [os.environ.get(flag, "")]
            if not flags[0]:
                flags.pop(0)

            if shared_options.antlr_runtime == 'static':
                # When linking the ANTLR runtime statically, -fPIC is
                # still necessary because libparse_fasm will be a
                # shared library.
                flags.append("-fPIC")

            # FIXME: These should be in the cmake config file?
            # Disable excessive warnings currently in ANTLR runtime.
            # warning: type attributes ignored after type is already defined
            # `class ANTLR4CPP_PUBLIC ATN;`
            flags.append('-Wno-attributes')

            # Lots of implicit fallthroughs.
            # flags.append('-Wimplicit-fallthrough=0')

            if flags:
                os.environ[flag] = " ".join(flags)

    def build_extension(self, ext):
        if isinstance(ext, CMakeExtension):
            extdir = os.path.join(
                os.path.abspath(
                    os.path.dirname(self.get_ext_fullpath(ext.name))),
                ext.prefix)
            cmake_args = [
                '-DCMAKE_INSTALL_PREFIX=' + extdir,
                '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                '-DPYTHON_EXECUTABLE=' + sys.executable,
                '-DANTLR_RUNTIME_TYPE=' + shared_options.antlr_runtime
            ]

            cfg = 'Debug' if self.debug else 'Release'
            build_args = ['--config', cfg]
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            if not sys.platform.startswith('win'):
                build_args += ['--', '-j']

            env = os.environ.copy()
            env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
                env.get('CXXFLAGS', ''), self.distribution.get_version())

            # Remove the existing build_temp directory if it already exists.
            if os.path.exists(self.build_temp):
                shutil.rmtree(self.build_temp, ignore_errors=True)
            os.makedirs(self.build_temp, exist_ok=True)

            self.add_flags()

            subprocess.check_call(
                ['cmake', ext.sourcedir] + cmake_args,
                cwd=self.build_temp,
                env=env)
            subprocess.check_call(
                ['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
            subprocess.check_call(
                ['cmake', '--install', '.'], cwd=self.build_temp)
            subprocess.check_call(['ctest'], cwd=self.build_temp)
            print()  # Add an empty line for cleaner output
        else:
            super().build_extension(ext)

    def initialize_options(self):
        super().initialize_options()
        shared_options.initialize(self)

    def finalize_options(self):
        super().finalize_options()
        shared_options.load(self)


class BuildCommand(build):
    user_options = build.user_options + SharedOptions.options

    def initialize_options(self):
        super().initialize_options()
        shared_options.initialize(self)

    def finalize_options(self):
        super().finalize_options()
        shared_options.load(self)

    def run(self):
        shared_options.load(self)
        super().run()


class InstallCommand(install):
    user_options = install.user_options + SharedOptions.options

    def initialize_options(self):
        super().initialize_options()
        shared_options.initialize(self)

    def finalize_options(self):
        super().finalize_options()
        shared_options.load(self)

    def run(self):
        shared_options.load(self)
        super().run()


class DevelopCommand(develop):
    user_options = develop.user_options + SharedOptions.options

    def initialize_options(self):
        super().initialize_options()
        shared_options.initialize(self)

    def finalize_options(self):
        super().finalize_options()
        shared_options.load(self)

    def run(self):
        shared_options.load(self)
        super().run()


setuptools.setup(
    name="fasm",
    version=version,
    author="SymbiFlow Authors",
    author_email="symbiflow@lists.librecores.org",
    description="FPGA Assembly (FASM) Parser and Generation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SymbiFlow/fasm",
    packages=setuptools.find_packages(exclude=('tests*', )),
    install_requires=['textx'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['fasm=fasm:main'],
    },
    ext_modules=[
        CMakeExtension('parse_fasm', sourcedir='src', prefix='fasm/parser')
    ] + cythonize("fasm/parser/antlr_to_tuple.pyx"),
    cmdclass={
        'build_ext': AntlrCMakeBuild,
        'build': BuildCommand,
        'develop': DevelopCommand,
        'install': InstallCommand,
    },
)
