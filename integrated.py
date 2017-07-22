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
    test_data = '''
    (let ([v 1])
        (let ([w 46])
            (let ([x (+ v 7)]) 
                (let ([y (+ 4 x)]) 
                    (let ([z (+ x w)])
                        (+ z (- y))
                    )
                )
            )
        )
    )
    '''
    # test_data = '(let ([x 42]) (let ([y x]) y))'
    input_filename = None
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
        lines = []
        with open(input_filename, 'r') as rf:
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

    sch_ast = Uniquify(ast)
    PrintSourceCode('Source code after uniquify', SchSourceCode(sch_ast))

    ir_ast = Flatten(sch_ast)
    PrintSourceCode('IR source code', IrSourceCode(ir_ast))

    x86_formatter = X86InternalFormatter()
    x86_ast = SelectInstruction(ir_ast)
    PrintSourceCode('X86 (Select Instruction)',
                    X86SourceCode(x86_ast, x86_formatter))

    x86_ast = UncoverLive(x86_ast)
    x86_formatter.include_live_afters = True
    PrintSourceCode('X86 (Uncover Live)',
                    X86SourceCode(x86_ast, x86_formatter))

    x86_ast = AllocateRegisterOrStack(x86_ast)
    x86_formatter.include_live_afters = False
    PrintSourceCode('X86 (Allocate Register or Stack)',
                    X86SourceCode(x86_ast, x86_formatter))

    x86_ast = PatchInstruction(x86_ast)
    PrintSourceCode('X86 (Patch Instructions)',
                    X86SourceCode(x86_ast, x86_formatter))

    x86_src_code = GenerateX86(x86_ast)
    PrintSourceCode('X86 (Assembly)', x86_src_code)

    if input_filename is not None:
        import os
        output_filename = os.path.basename(input_filename)
        output_filename = os.path.splitext(output_filename)[0] + '.s'
        output_filename = os.path.join('runtime', output_filename)
        with open(output_filename, 'w') as wf:
            wf.write(x86_src_code)
            wf.write('\n')
