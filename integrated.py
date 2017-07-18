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

    def PrintSourceCode(header, code):
        print(header)
        print(code)
        print('---\n')

    PrintSourceCode('Source code', test_data)

    lexer = SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)
    assert ast.type == 'program'

    sch_ast = Uniquify(ast)
    PrintSourceCode('Source code after uniquify', sch_ast.source_code())

    ir_ast = Flatten(sch_ast)
    PrintSourceCode('IR source code', ir_ast.source_code())

    x86_ast = SelectInstruction(ir_ast)
    PrintSourceCode('X86 (Select Instruction)', x86_ast.source_code())

    x86_ast = AssignHome(x86_ast)
    PrintSourceCode('X86 (Assign Home)', x86_ast.source_code())
