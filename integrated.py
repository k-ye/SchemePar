from __future__ import print_function

import sys

from compiler.lexer import SchemeLexer
from compiler.parser import SchemeParser
from compiler.compiler import *

if __name__ == '__main__':
    test_data = '''
    ; a test Scheme program using R1 grammar
    (let ([foo 42] [bar (- 3)])
        (+ 
            (let ([foo 3] [bar bar]) (+ foo bar))
            foo
        )
    )
    ; 42
    '''
    if len(sys.argv) > 1:
        lines = []
        with open(sys.argv[1], 'r') as rf:
            for line in rf:
                lines.append(line)
        test_data = ''.join(lines)

    print('Source code:')
    print(test_data)
    print('---\n')

    lexer = SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)
    assert ast.type == 'program'

    sch_ast = Uniquify(ast)
    print('Souce code after uniquify:')
    print(sch_ast.source_code())
    print('---\n')

    ir_ast = Flatten(sch_ast)
    print('IR Souce code:')
    print(ir_ast.source_code())
    print('---\n')

    x86_ast = SelectInstruction(ir_ast)
