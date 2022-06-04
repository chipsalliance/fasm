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

# minimum required CMAKE version
CMAKE_MINIMUM_REQUIRED(VERSION 3.7 FATAL_ERROR)

project(parse_fasm)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/../third_party/antlr4/runtime/Cpp/cmake)

set(CMAKE_CXX_STANDARD 17)
set(ANTLR4_TAG e4c1a74)
if (MSVC_VERSION GREATER_EQUAL "1900")
    include(CheckCXXCompilerFlag)
    CHECK_CXX_COMPILER_FLAG("/std:c++latest" _cpp_latest_flag_supported)
    if (_cpp_latest_flag_supported)
        add_compile_options("/std:c++latest")
    endif()
endif()

if(ANTLR_RUNTIME_TYPE STREQUAL "static")
  # Required if linking to static library
  add_definitions(-DANTLR4CPP_STATIC)

  # Build the static library.
  include(ExternalAntlr4Cpp)
  set(ANTLR4_RUNTIME antlr4_static)
else()
  # Look to see if the shared library is already available.
  find_library(ANTLR4_RUNTIME NAMES antlr4-runtime REQUIRED)
  find_path(ANTLR4_INCLUDE_DIRS antlr4-runtime.h
    HINTS /usr/include/antlr4-runtime
          $ENV{ANTLR4_RUNTIME_INCLUDE})

  # If not, build it.
  if(NOT ANTLR4_RUNTIME OR NOT ANTLR4_INCLUDE_DIRS)
    include(ExternalAntlr4Cpp)
    set(ANTLR4_RUNTIME antlr4_shared)
  endif()
endif()

# add antrl4cpp artifacts to project environment
include_directories(${ANTLR4_INCLUDE_DIRS})

# set variable pointing to the antlr tool that supports C++
# this is not required if the jar file can be found under PATH environment
set(ANTLR_EXECUTABLE ${CMAKE_CURRENT_SOURCE_DIR}/../third_party/antlr4_lib/antlr-4.9.3-complete.jar CACHE PATH "antlr4 generator JAR file")

# add macros to generate ANTLR Cpp code from grammar
find_package(ANTLR REQUIRED)

# Unit testing library
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../third_party/googletest EXCLUDE_FROM_ALL googletest)

# Lexer and parser targets
antlr_target(FasmLexer antlr/FasmLexer.g4 LEXER
  OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMPILE_FLAGS -Xexact-output-dir
  )
antlr_target(FasmParser antlr/FasmParser.g4 PARSER VISITOR
  OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS_ANTLR FasmLexer
  COMPILE_FLAGS -Xexact-output-dir -lib ${ANTLR_FasmLexer_OUTPUT_DIR}
  )

# Explanation:
# line 1: Skip lines starting in #define
#      2: Extract TAGS(...) from dependencies
#      3: Convert from TAGS('c', long_name) -> long_name = b'c, write to file
add_custom_command(OUTPUT tags.py
  COMMAND grep -ve ^\#define ${CMAKE_CURRENT_SOURCE_DIR}/ParseFasm.cpp |
          grep -hoe TAG\([^\)]*\) |
          sed -e s/TAG\(\\\(.*\\\),\ \\\(.*\\\)\)/\\2\ =\ b\\1/ > ${CMAKE_CURRENT_BINARY_DIR}/tags.py
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/ParseFasm.cpp
  VERBATIM
  )
add_custom_target(tags_py ALL DEPENDS tags.py)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/tags.py TYPE LIB)

# Include generated files in project environment
include_directories(${ANTLR_FasmLexer_OUTPUT_DIR})
include_directories(${ANTLR_FasmParser_OUTPUT_DIR})

# Add generated grammar to binary target
add_library(parse_fasm SHARED ParseFasm.cpp
  ${ANTLR_FasmLexer_CXX_OUTPUTS}
  ${ANTLR_FasmParser_CXX_OUTPUTS})
target_link_libraries(parse_fasm ${ANTLR4_RUNTIME})
install(TARGETS parse_fasm)
#target_compile_options(parse_fasm PRIVATE -Wno-attributes) # Disable warning from antlr4-runtime

add_executable(parse_fasm_tests
  ParseFasmTests.cpp
  ${ANTLR_FasmLexer_CXX_OUTPUTS}
  ${ANTLR_FasmParser_CXX_OUTPUTS})
target_link_libraries(parse_fasm_tests ${ANTLR4_RUNTIME})
target_link_libraries(parse_fasm_tests gtest_main)
target_link_libraries(parse_fasm_tests gtest)
#target_compile_options(parse_fasm_tests PRIVATE -Wno-attributes) # Disable warning from antlr4-runtime

# Standalone executable
add_executable(parse_fasm_run EXCLUDE_FROM_ALL
  ParseFasmRun.cpp
  ${ANTLR_FasmLexer_CXX_OUTPUTS}
  ${ANTLR_FasmParser_CXX_OUTPUTS})
target_link_libraries(parse_fasm_run ${ANTLR4_RUNTIME})
set_target_properties(parse_fasm_run PROPERTIES OUTPUT_NAME parse_fasm)
#target_compile_options(parse_fasm_run PRIVATE -Wno-attributes) # Disable warning from antlr4-runtime

# Unit tests
include(CTest)

add_test(NAME parse_fasm_tests
         COMMAND parse_fasm_tests)
enable_testing()
