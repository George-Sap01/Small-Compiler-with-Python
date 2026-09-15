
class Emitter:
    """
    Helper class for building and writing C source code files incrementally.
    ----------------------------------
    Attributes 

    * code: str      \n
        is the string containing the C code that is emitted.
    * header: str    \n
        contains things that we will prepend to the code later on.
    * fullPath: str  \n
        is the path to write the file containing C code.
    ----------------------------------
    Methods

    * emit(code: str): 
        add a fragment of C code.
    * emitLine(code: str): 
        add a fragment that ends a line.
    * headerLine(code: str):
        adding a line of C code to the top of the C code file, such as including a library header, the main function, and variable declarations.
    * writeFile():
        writes the C code to a file.

    """
    def __init__(self, fullpath: str):
        self.fullpath = fullpath
        self.header = ""
        self.code = ""

    def emit(self, code: str):
        self.code += code

    def emitLine(self, code: str):
        self.code += code + '\n'

    def headerLine(self, code: str):
        self.header += code + '\n'

    def writeFile(self):
        with open(self.fullpath, 'w') as outputFile:
            outputFile.write(self.header + self.code) 

