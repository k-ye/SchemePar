from __future__ import print_function

import ply.yacc as yacc
import lexer
from ast.sch_ast import *

tokens = lexer.tokens


class ParsingError(Exception):
    pass


def SchemeParser():
    def p_expr_int_var(p):
        '''expr : expr_int
                | expr_var'''
        p[0] = p[1]

    def p_expr_int(p):
        'expr_int : INT'
        p[0] = MakeSchIntNode(p[1])

    def p_expr_var(p):
        'expr_var : VAR'
        p[0] = MakeSchVarNode(p[1])

    def p_expr_let(p):
        'expr : LPAREN LET let_var_binds expr RPAREN'
        p[0] = MakeSchLetNode(p[3], p[4])

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
        '''var_def_pair : LBRACKET expr_var expr RBRACKET
                        | LPAREN expr_var expr RPAREN'''
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
        p[0] = MakeSchApplyNode(method, arg_list)

    # def p_empty(p):
    #     'empty :'
    #     pass

    def p_error(p):
        raise ParsingError('Error syntax, p={}'.format(p))

    class ParserImpl(object):

        def __init__(self, yacc):
            self._yacc = yacc

        def parse(self, source, lexer):
            ast = self._yacc.parse(input=source, lexer=lexer)
            ast = MakeSchProgramNode(ast)
            return ast

    return ParserImpl(yacc.yacc())

if __name__ == '__main__':
    test_data = '''
    ; a test Scheme program using R1 grammar
    (let ([foo 43] [bar (- 1)])
        (+ foo bar)
    )
    '''
    lexer = lexer.SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)
    print(SchSourceCode(ast))
