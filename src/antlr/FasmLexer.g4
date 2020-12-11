// Copyright (C) 2020  The SymbiFlow Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

lexer grammar FasmLexer;

// White space
S : [ \t] -> skip ;  // Skip all outer white space
NEWLINE : [\n\r] ;   // NEWLINE is not skipped, because it is needed to break lines.

// Matches a feature identifier
fragment IDENTIFIER : [a-zA-Z] [0-9a-zA-Z_]* ;
FEATURE : IDENTIFIER ('.' IDENTIFIER)* ;

// Number values
// The leading '[hbdo] is kept in the same token to
// disambiguate the grammar.
HEXADECIMAL_VALUE : '\'h' [ \t]* [0-9a-fA-F_]+ ;
BINARY_VALUE      : '\'b' [ \t]* [01_]+ ;
DECIMAL_VALUE     : '\'d' [ \t]* [0-9_]+ ;
OCTAL_VALUE       : '\'o' [ \t]* [0-7_]+ ;
INT : [0-9]+ ;

// Everything after a # until a newline.
COMMENT_CAP : '#' (~[\n\r])* ;

// Simple tokens
// These are not referenced in the parser by name,
// but instead by the character they match.
// They need to be here so the lexer will tokenize them.
// This is needed because otherwise an IDENTIFIER with
// a leading dot, or no dot, could also be an ANNOTATION_NAME.
EQUAL : '=' ;
OPEN_BRACKET : '[' ;
COLON : ':' ;
CLOSE_BRACKET : ']' ;

// An opening curly bracket enters ANNOTATION_MODE
BEGIN_ANNOTATION : '{' -> pushMode(ANNOTATION_MODE) ;

// https://github.com/antlr/antlr4/issues/1226#issuecomment-230382658
// Any character which does not match one of the above rules will appear in the token stream as
// an ErrorCharacter token. This ensures the lexer itself will never encounter a syntax error,
// so all error handling may be performed by the parser.
ErrorCharacter
    :   .
    ;

// Inside an annotation, only the rules below apply.
// That is why there is some duplication.
mode ANNOTATION_MODE;

// White space is skipped.
ANNOTATION_S : [ \t] -> skip ;

ANNOTATION_NAME : [.a-zA-Z] [0-9a-zA-Z_]* ;
fragment NON_ESCAPE_CHARACTERS : ~[\\"] ;
fragment ESCAPE_SEQUENCES : [\\] [\\"] ;
ANNOTATION_VALUE : '"' (NON_ESCAPE_CHARACTERS | ESCAPE_SEQUENCES)* '"' ;

// Simple tokens.
ANNOTATION_EQUAL : '=' ;
ANNOTATION_COMMA : ',' ;

// A closing curly bracket pops out of ANNOTATION_MODE
END_ANNOTATION : '}' -> popMode ;
