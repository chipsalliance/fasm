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

parser grammar FasmParser;

// Reference tokens from the lexer.
options { tokenVocab=FasmLexer; }

// fasmFile is the root of the parser
fasmFile : fasmLine (NEWLINE fasmLine)* EOF ;

// Describes one line
fasmLine : setFasmFeature?
           annotations?
           COMMENT_CAP?
         ;

// Example: a.b.c[31:0] = 3'o7
setFasmFeature : FEATURE featureAddress? (EQUAL value)? ;
featureAddress : '[' INT (':' INT)? ']' ;

// Matches an ordinary decimal integer, or a Verilog integer literal.
value : INT? verilogDigits # VerilogValue
      | INT                # PlainDecimal
      ;

// Matches the portion of a Verilog integer literal starting with
// the quote character (') e.g. 'b1101
verilogDigits : HEXADECIMAL_VALUE # HexValue
              | BINARY_VALUE      # BinaryValue
              | DECIMAL_VALUE     # DecimalValue
              | OCTAL_VALUE       # OctalValue
              ;

// Example: { a = "b", c = "d" }
annotations : BEGIN_ANNOTATION annotation (',' annotation)* END_ANNOTATION ;
annotation : ANNOTATION_NAME ANNOTATION_EQUAL ANNOTATION_VALUE ;
