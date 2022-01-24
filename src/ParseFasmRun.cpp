// Copyright 2017-2022 F4PGA Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: Apache-2.0

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
