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

/// Unit tests for ParseFasm

#include <gtest/gtest.h>
#include "ParseFasm.cpp"

// Test the Num class
TEST(ParseFasmTests, Num) {
        std::ostringstream str;
        str << Num('a', 0x74736554);
        if (str.str() == "aTest") {
                std::cout << "little endian" << std::endl;
        } else if (str.str() == "atseT") {
                std::cout << "big endian" << std::endl;
        } else {
                ASSERT_TRUE(false);
        }
}

// Check that count_without() works
TEST(ParseFasmTests, count_without) {
        std::string str = "_01_2_34_";
        EXPECT_EQ(count_without(str.begin(), str.end(), '_'), 5);
}

// clang-format off
// A test of the full parser
// Formatting is disabled to allow indenting the output string
// to illustrate the structure.
TEST(ParseFasmTests, parse_fasm) {
    std::istringstream input("a.b.c[31:0] = 7'o123 { d = \"e\", .f = \"\" } # hello\nthere");
    std::ostringstream output;
    bool stored_hex_mode = hex_mode;
    hex_mode = true;
    parse_fasm(input, output);
    
    /// The below string is the input above encoded in hex mode.
    EXPECT_EQ(output.str(),
        "l<50>" /// Line
          "s<20>" /// Set feature
            "f<5>a.b.c" /// Feature = "a.b.c"
            ":<7><1f><0>" /// Address = 31:0
            "'<7>" /// Width = 7
            "o<4><53>" /// Octal value = 123
          "{<1c>" /// Annotations (list)
            "a<a>" /// Annotation
              ".<1>d" /// Name = "d"
              "=<1>e" /// Value = "e"
            "a<a>" /// Annotation
              ".<2>.f" /// Name = ".f"
              "=<0>" /// Value = ""
          "#<6> hello" /// Comment
        "\n" /// Newline (only in hex mode for readability)
        "l<d>" /// Line
          "s<9>" /// Set feature
            "f<5>there" /// Feature = "there"
        "\n" /// Newline (only in hex mode for readability)
      );
     hex_mode = stored_hex_mode;
}
// clang-format on
