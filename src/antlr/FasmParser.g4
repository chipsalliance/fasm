// Copyright (C) 2020  The SymbiFlow Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

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
