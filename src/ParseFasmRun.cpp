// Copyright (C) 2020  The SymbiFlow Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

#include "ParseFasm.cpp"

/// This can be used as a standalone utility.
/// parse_fasm [file] [-hex]
///   file  : The file to parse, otherwise use stdin.
///   -hex  : Enable hex mode.
int main(int argc, char* argv[]) {
        /// If no args say otherwise,
        /// run as a filter (stdin -> parse_fasm -> stdout)
        bool filter = true;

        /// Parse flags first
        for (int i = 1; i < argc; i++) {
                std::string arg(argv[i]);
                if (arg == "-hex") {
                        hex_mode = true;
                }
        }

        /// Run parse on file arguments
        for (int i = 1; i < argc; i++) {
                std::string arg(argv[i]);
                if (arg[0] == '-') {
                        std::ifstream in;
                        in.open(arg);
                        parse_fasm(in, std::cout);
                }
        }

        /// Run as a filter
        if (filter) {
                std::istringstream in_line;
                for (std::string line; std::getline(std::cin, line);) {
                        in_line.str(line);
                        parse_fasm(in_line, std::cout);
                }
        }
        return 0;
}
