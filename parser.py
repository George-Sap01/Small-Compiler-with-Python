"""
Parser Module
=============

    This module provides a recursive descent parser for a custom BASIC-like language. 
    It processes tokens emitted by the `Lexer` to validate program syntax, check symbol 
    declarations, track control flow labels, and ensure correct statement execution structure.

Grammar Rules:
---------------------
    program    ::= {statement}
    statement  ::= "PRINT" (expression | string) nl
                 | "IF" comparison "THEN" nl {statement} "ENDIF" nl
                 | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
                 | "LABEL" ident nl
                 | "GOTO" ident nl
                 | "LET" ident "=" expression nl
                 | "INPUT" ident nl
    nl         ::= '\n'+
    comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    expression ::= term { ("-" | "+") term }
    term       ::= unary { ("/" | "*") unary }
    unary      ::= ["+" | "-"] primary
    primary    ::= NUMBER | IDENT
"""

import sys
from lexer import *
from emit import *

class Parser:
    """
    A class representing a recursive descent parser.
    ------------------------------------------

    Attributes

    - lexer: Lexer                  \n
        The lexer instance providing tokens from the source string.

    - symbols: set of str           \n
        Symbol table storing declared variable identifiers.

    - labelsDeclared: set of str    \n
        Set tracking labels declared via the `LABEL` keyword.

    - labelsGotoed: set of str      \n
        Set tracking targeted label names referenced by `GOTO`.

    - curToken: Token               \n
        The token currently being inspected.

    - peekToken: Token              \n
        The lookahead token.
    ------------------------------------------
        
    Methods
    
    - checkToken(kind: TokenType) -> bool:
        Checks whether the current token matches the given `TokenType`.

    - checkPeek(kind: TokenType) -> bool:
        Checks whether the next (lookahead) token matches the given `TokenType`.

    - match(kind: TokenType):
        Validates the current token against expected `TokenType` and advances, given error calls the abort().

    - nextToken():
        Advances the cursor to set `curToken` to `peekToken` and retrieves a new `peekToken`.

    - abort(message: str):
        Terminates parser execution with an error message.

    - program():
        Entry point for parsing the root production rule.

    - statement():
        Parses individual language statements (PRINT, IF, WHILE, LABEL, GOTO, LET, INPUT).

    - nl():
        Ensures proper handling of one or more statement-terminating newlines.

    - comparison():
        Parses logical comparison operations across expressions.

    - isComparisonOperator() -> bool:
        Determines whether `curToken` is a valid comparison operator.

    - expression():
        Parses arithmetic expressions with standard addition and subtraction precedence.

    - term():
        Parses multiplication and division arithmetic terms.

    - unary():
        Handles optional unary standard signed prefixes (`+` or `-`).

    - primary():
        Parses foundational value terminals (literals and initialized variables).

    """
    def __init__(self, lexer: Lexer, emitter: Emitter):
        """
            Parameters

            lexer:  Lexer
                An active Lexer instance bound to source code.
        """
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()         # Variables declared so far    
        self.labelsDeclared = set()  # Keep track of all labels declared
        self.labelsGotoed = set()    # All labels goto'ed, so we know if they exist or not.

        self.curToken:  Token = None
        self.peekToken: Token = None
        self.nextToken()
        self.nextToken()             # Call this twice to initiliaze current and peek

    # Return true if the current token matches
    def checkToken(self, kind: TokenType):
        """Returns True if the current token matches the specified token kind."""
        return kind == self.curToken.kind

    # Return true if the next token matches.
    def checkPeek(self, kind: TokenType):
        """Returns True if the peek token matches the specified token kind."""
        return kind == self.peekToken.kind

    # Try to match current token. If not, error. Advances the current token.
    def match(self, kind: TokenType):
        """
        Verifies that the current token matches the expected kind.
        
        Advances to the next token if valid; otherwise calls `abort()`.
        """
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances the current token
    def nextToken(self):
        """Advances current and lookahead token positions."""
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # No need to worry about passing the EOF, lexer handles that.

    def abort(self, message):
        """Terminates compiler execution and displays a syntax error message."""
        sys.exit("Error: " + message)

    # Production rules.

    # program ::= {statement}
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")

        # Since some newlines are required in our grammar, need to skip the excess.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all the statements in the program
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # Wrap things up.
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        # Check that each label referenced in a GOTO is declared.
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)


    # one of the following statements...
    def statement(self):
        """Terminates compiler execution and displays a syntax error message."""

        # Check the first token to see what kind of statement this is.

        # `PRINT` (expression | string) nl
        if self.checkToken(TokenType.PRINT):
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # Simple string, so print it.
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()
            else:
                # Expect an expression and print the result as a float
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(") 
                self.expression()
                self.emitter.emitLine("));")

        # `IF` comparison `THEN` nl {statement} `ENDIF` nl
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            # Zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()
            
            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")

        # `WHILE` comparison `REPEAT` nl {statement} `ENDWHILE` nl
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

        # `LABEL` ident nl
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()

            # Make sure this label doesn't already exist.
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        # `GOTO` ident nl
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # `LET` ident `=` expression nl
        elif self.checkToken(TokenType.LET):
            self.nextToken()

            # Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emitLine(";")

        # `INPUT` ident nl
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()

            # Check if ident exists in symbol table. If not, declare it.
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            # Emit scnaf but also validate the input. If invalid, set the variable to 0 and clear the input
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid Statement at :" + self.curToken.text + " (" +  self.curToken.kind.name + ")") 

        # Newline
        self.nl()

    # nl ::= '\n'+
    def nl(self):
        """Consumes one or more contiguous newline tokens."""
        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        """Parses relational comparison expressions."""
        self.expression()
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)

        # Can have 0 or more comparison operator and expressions.
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    def isComparisonOperator(self):
        """Helper to verify if curToken belongs to relational operator types."""
        comparison_op_list = [TokenType.EQEQ, TokenType.NOTEQ, TokenType.LT, TokenType.LTEQ, TokenType.GT, TokenType.GTEQ]
        return any( [self.checkToken(comparison_op) for comparison_op in comparison_op_list] )
        # instead of: return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        """Parses additive terms (`+` / `-`)."""
        self.term()
        # Can have 0 or more +/- expressions.
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        """Parses multiplicative factors (`*` / `/`)."""
        self.unary()
        # Can have 0 or more *// expressions.
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):
        """Parses optional signed prefixes (`+` / `-`) for primary factors."""        
        # Optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        """Parses numeric literal values or assigned identifier tokens."""
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: "+ self.curToken.text)

            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)


def main():
    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as inputFile:
        source = inputFile.read()

    # Initialize the lexer and parser
    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program() # Start the parser.
    print("Parsing completed.")


if __name__ == "__main__":
    main()