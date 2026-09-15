"""Lexer for a text 

    The code implements a hand-written lexical analyzer (tokenizer) in Python designed to break source code strings 
    into discrete tokens (keywords, identifiers, numbers, strings, operators, and symbols) for a custom interpreter or compiler.

    This script does not require any external modules outside standard Python.

    This file can also be imported as a module and contains the following
    classes:

        * TokenType - contains all the types of a Token
        * Token     - The class for a Token 
        * Lexer     - The class that models a Lexer 
"""

import sys
from enum import Enum


"""
    Classifying Tokens
    ------------------

    Operator:    One or two consecutive characters that matches: + - * / = == != > < >= <=
    String:      Double quotation followed by zero or more characters and a double quotation. Such as: "hello, world!" and ""
    Number:      One or more numeric characters followed by an optional decimal point and one or more numeric characters. Such as: 15 and 3.14
    Identifier:  An alphabetical character followed by zero or more alphanumeric characters.
    Keyword:     Exact text match of: LABEL, GOTO, PRINT, INPUT, LET, IF, THEN, ENDIF, WHILE, REPEAT, ENDWHILE
"""


# TokenType is our enum for all types of tokens
class TokenType(Enum):
    """
        A class to represent the different types of Tokens, using an enum pattern
    """
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201  
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


# Token contains the original text and the type of token 
class Token:
    """
    A class to represent a Token and its properties

    ----------------------------------------
    Attributes

    - text : str        \n
        the string of the token
    - kind : TokenType  \n
        the kind of token
    --------------------
    Methods

    - checkIfKeyword(tokenText: str):
        Checks if a tokens text is a keyword. Returns: TokenType | None
    """

    def __init__(self, tokenText: str, tokenKind: TokenType):
        self.text = tokenText   # The token's actual text. Used for identifiers, strings and numbers 
        self.kind = tokenKind   # The TokenType that this token is classified as.

    @staticmethod
    def checkIfKeyword(tokenText: str):
        """
        Checks if a token's text is a keyword

        --------------------
        Parameters

        tokenText: str
            The token's text
        --------------------
        Returns

            TokenType | None  
        """
        for kind in TokenType:
            # Relies on all keyword enum values being 1xx.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None


class Lexer:
    """
    A class used to represent the Lexer

    ----------------------------------------
    Attributes
    
    * source: str               \n
        the code that is being interpreted 
    * curChar: str(char)        \n
        the current char in the source string
    * curPos: int               \n
        the position of the current char in source string
    ----------------------------------------
    Methods

    - nextChar():
        Gets the next character in the source (string) (curChar and curPos change) | '\\0' when EOF. 

    - peek():
        Gets the next character of the curChar (curChar nor curPos change) | '\\0' when EOF.
    
    - abort(message: str)
        Using sys.exit prints message when ERROR occurs.

    - skipWhitespace():
        Filters (continuous) whitespaces, it explicitly preserves '\\n' to end statements.

    - skipComments():
        Filters comments, it explicitly preserves '\\n' to end statements.

    - getToken():
        Makes a word to a token, returns a Token object.
        
    """
    def __init__(self, source: str):
        """
            Parameters

            source: str
                the code that is being interpeted 
        """
        self.source  = source + '\n' # Source code to lex as a string. Append newline to simplify lexing/parsing the last token/statement 
        self.curChar = ''            # Current character in the string 
        self.curPos  = -1            # Current position in the string 
        self.nextChar()


    # Process the next character 
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0'   # EOF
        else:
            self.curChar = self.source[self.curPos]

    # Return the lookahead character
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos + 1]

    # Invalid token found, print error message and exit
    def abort(self, message: str):
        sys.exit("Lexing Error: " + message)

    # Skip whitespace except newlines, which will use to indicate  the end of a statement 
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()

    # Skip comments in the code
    def skipComments(self):
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()

    # Return the next token 
    def getToken(self):
        """
        Check the first character of this token to see if we can decide what it is.
        If it is a multiple character operator (e.g. !=), number, identifier or keyword then we will process the rest.
        
        -------
        Returns

            A Token object
        """
        self.skipWhitespace()
        self.skipComments()
        token = None
        if self.curChar == '+':                                  # Plus token 
            token = Token(self.curChar, TokenType.PLUS)           
        elif self.curChar == '-':                                # Minus token 
            token = Token(self.curChar, TokenType.MINUS)         
        elif self.curChar == '*':                                # Asterisk token 
            token = Token(self.curChar, TokenType.ASTERISK)      
        elif self.curChar == '/':                                # Slash token 
            token = Token(self.curChar, TokenType.SLASH)         
        elif self.curChar == '=':                                #  EQ  or EQEQ Token
            # Check whether this token is = or ==                 
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)      
        elif self.curChar == '>':                                #  GT  or GTEQ
            # Check whether this token > or >=                    
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == '<':                                #  LT or LTEQ
            # Check whether this token is < or <=                 
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == '!':                                #  NOTEQ
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.curChar == '\n':                               # Newline token 
            token = Token(self.curChar, TokenType.NEWLINE)        
        elif self.curChar == '\0':                               # EOF token 
            token = Token(self.curChar, TokenType.EOF)           
        elif self.curChar == '\"':                               # STRING
            # Get characters between quotations
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '\"':
                # Don't allow special characters in the strings. No escape characters, newlines, tabs or %.
                # We will be using C's printf on this string.
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string.")
                self.nextChar()

            tokText = self.source[startPos : self.curPos]  # Get the substring.
            token = Token(tokText, TokenType.STRING)
        elif self.curChar.isdigit():                           # NUMBER
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()

            if self.peek() == '.': # Decimal
                self.nextChar()
                # Must have at least one digit after decimal.
                if not self.peek().isdigit():
                    # Error !
                    self.abort("Illegal character in number.")

                while self.peek().isdigit():
                    self.nextChar()

            tokText = self.source[startPos : self.curPos + 1] # Get the substring
            token = Token(tokText, TokenType.NUMBER)
        elif self.curChar.isalpha():                           # IDENTIFIER 
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alpha numeric characters.
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.curPos + 1] # Get the substring.  
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # Identifier
                token = Token(tokText, TokenType.IDENT)
            else: # keyword
                token = Token(tokText, keyword)
        else:
            # Unknown token!
            self.abort(f"Unknown token: '{self.curChar}'")

        self.nextChar()
        return token


def main():

    """
    source = "123\n" -> length = 4

    while lexer.peek() != '\0':
        print(lexer.curChar)
        lexer.nextChar() 
    """
    source = "+- */"
    lexer = Lexer(source)

    token = lexer.getToken()
    while token.kind != TokenType.EOF:
        print(token.kind)
        token = lexer.getToken()


if __name__ == "__main__":
    main()

