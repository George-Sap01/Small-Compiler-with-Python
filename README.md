# Teeny Tiny Compiler

A lightweight, single-pass compiler written in Python that translates a custom BASIC-like source language into idiomatic C code.

## Features 

* Lexical Analysis (lexer.py): Hand-written tokenizer identifying keywords, identifiers, numbers, strings, standard operators, and newline statement terminators.

* Recursive Descent Parsing (parser.py): Validates syntax, maintains symbol tables, tracks control flow labels (LABEL / GOTO), and enforces operator precedence.

* C Code Generation (emit.py): Incrementally constructs structured C code, handling headers, dynamic float variable declarations, and input/output procedures.

* Error Handling: Detects and reports invalid syntax, references to undeclared variables, duplicate labels, and targeted GOTO labels that do not exist.

## Language Grammar
```
    program    ::= {statement}
    statement  ::= "PRINT" (expression | string) nl
                | "IF" comparison "THEN" nl {statement} "ENDIF" nl
                | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
                | "LABEL" ident nl
                | "GOTO" ident nl
                | "LET" ident "=" expression nl
                | "INPUT" ident nl
    comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    expression ::= term { ("-" | "+") term }
    term       ::= unary { ("/" | "*") unary }
    unary      ::= ["+" | "-"] primary
    primary    ::= NUMBER | IDENT
    nl         ::= '\n'+
```

## Getting Started

### Prerequisites

- Python 3.x
- GCC or any standard C compiler (to build the generated output code)

### Usage
1. **Write or provide a source file (e.g., average.teeny):**

``` 
LET a = 0
WHILE a < 1 REPEAT
    PRINT "Enter number of scores: "
    INPUT a
ENDWHILE

LET b = 0
LET s = 0
PRINT "Enter one value at a time: "
WHILE b < a REPEAT
    INPUT c
    LET s = s + c
    LET b = b + 1
ENDWHILE

PRINT "Average: "
PRINT s / a
```
2. **Run the compiler:**

```BASH
python teenytiny.py average.teeny
```
This generates an out.c target file upon successful compilation.

3. **Compile and execute the C code:**

```BASH
gcc out.c -o out
./out
```
## Project Structure

* teenytiny.py: Entry point driving the compilation pipeline from source code reading to C file emission.

* lexer.py: Tokenizer class along with Token and TokenType enums.

* parser.py: Syntax analyzer implementing language grammar rules.

* emit.py: C code generation and file writing utility.