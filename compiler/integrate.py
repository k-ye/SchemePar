from __future__ import print_function

from lexer import SchemeLexer
from parser import SchemeParser
from compiler import Compile

def Main():
    test_data = '''
    ; a test Scheme program using R1 grammar
    (program
        (let  ([foo 43] [bar (- 1)])
            (+ 
                (let ([foo 42]) (+ foo bar))
                foo
            )
        )
    )
    '''
    lexer = SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)
    ast = Compile(ast)
    print(ast.source_code())

if __name__ == '__main__':
    Main()