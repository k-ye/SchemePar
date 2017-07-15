from __future__ import print_function

import ply.yacc as yacc
import lexer
from sch_ast import *

tokens = lexer.tokens


def p_program(p):
    'program : LPAREN PROGRAM expr RPAREN'
    p[0] = SchProgramNode(p[3])


def p_expr_int(p):
    'expr_int : INT'
    p[0] = SchIntNode(p[1])


def p_expr_var(p):
    'expr_var : VAR'
    p[0] = SchVarNode(p[1])


def p_expr_int_var(p):
    '''expr : expr_int
            | expr_var'''
    p[0] = p[1]


def p_expr_let(p):
    'expr : LPAREN LET let_var_binds expr RPAREN'
    p[0] = SchLetNode(p[3], p[4])


def p_let_var_binds(p):
    'let_var_binds : LPAREN let_var_list RPAREN'
    p[0] = p[2]


def p_let_var_list(p):
    '''let_var_list : var_def_pair
                    | var_def_pair let_var_list'''
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] = p[0] + p[2]


def p_var_def_pair(p):
    'var_def_pair : LBRACKET expr_var expr RBRACKET'
    p[0] = (p[2], p[3])


def p_expr_apply(p):
    'expr : LPAREN apply_inner RPAREN'
    p[0] = p[2]


def p_apply_inner(p):
    '''apply_inner : READ
                   | MINUS expr
                   | ADD expr expr'''
    method = p[1]
    arg_list = []
    for i in xrange(2, len(p)):
        arg_list.append(p[i])
    p[0] = SchApplyNode(method, arg_list)


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    raise RuntimeError('Error syntax, p={}'.format(p))

if __name__ == '__main__':
    parser = yacc.yacc()
    test_data = '''
    (program
        (let  ([foo 43] [bar (- 1)])
            (+ foo bar)
        )
    )
    '''
    sc_lexer = lexer.SchemeLexer()
    result = parser.parse(test_data, lexer=sc_lexer)
    print(result.source_code())
