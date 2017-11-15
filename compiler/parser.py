from __future__ import print_function

import ply.yacc as yacc
import lexer
from ast.sch_ast import *
from ast.base import GetIntX

tokens = lexer.tokens


class ParsingError(Exception):
    pass


def SchemeParser():
    def p_expr_arg(p):
        '''expr : arg_int
                | arg_var
                | arg_bool
                | arg_void'''
        p[0] = p[1]

    def p_expr_int(p):
        'arg_int : INT'
        p[0] = MakeSchIntNode(p[1])

    def p_expr_var(p):
        'arg_var : VAR'
        p[0] = MakeSchVarNode(p[1])

    def p_expr_bool(p):
        'arg_bool : BOOL'
        p[0] = MakeSchBoolNode(p[1])

    def p_expr_void(p):
        'arg_void : LPAREN VOID RPAREN'
        p[0] = MakeSchVoidNode()

    def p_expr_let(p):
        'expr : LPAREN let_inner RPAREN'
        p[0] = p[2]

    def p_let_inner(p):
        'let_inner : LET LPAREN let_var_bind_list RPAREN expr'
        p[0] = MakeSchLetNode(p[3], p[5])

    def p_let_var_bind_list(p):
        '''let_var_bind_list : var_bind_pair
                             | var_bind_pair let_var_bind_list'''
        p[0] = [p[1]]
        if len(p) > 2:
            p[0] = p[0] + p[2]

    def p_var_bind_pair(p):
        '''var_bind_pair : LBRACKET arg_var expr RBRACKET
                         | LPAREN arg_var expr RPAREN'''
        p[0] = (p[2], p[3])

    def p_expr_apply(p):
        'expr : LPAREN apply_inner RPAREN'
        p[0] = p[2]

    def p_apply_inner(p):
        'apply_inner : apply_method maybe_expr_list'
        p[0] = MakeSchApplyNode(p[1], p[2])

    def p_apply_method(p):
        '''apply_method : ARITH_OP
                        | CMP_OP
                        | LOGICAL_OP
                        | RTM_FN'''
        p[0] = p[1]

    def p_maybe_expr_list(p):
        '''maybe_expr_list : empty
                           | expr maybe_expr_list'''
        p[0] = []
        if len(p) > 2:
            p[0] = [p[1]] + p[2]  # non-empty case

    def p_expr_list(p):
        'expr_list : expr maybe_expr_list'
        p[0] = [p[1]] + p[2]

    def p_expr_if(p):
        'expr : LPAREN if_inner RPAREN'
        p[0] = p[2]

    def p_if_inner(p):
        'if_inner : IF expr expr expr'
        cond, then, els = p[2], p[3], p[4]
        p[0] = MakeSchIfNode(cond, then, els)

    def p_expr_vector_init(p):
        'expr : LPAREN VECTOR_INIT expr_list RPAREN'
        p[0] = MakeSchVectorInitNode(p[3])

    def p_expr_vector_ref(p):
        'expr : LPAREN VECTOR_REF expr arg_int RPAREN'
        vec, idx = p[3], p[4]
        assert IsSchIntNode(idx)
        p[0] = MakeSchVectorRefNode(vec, GetIntX(idx))

    def p_expr_vector_set(p):
        'expr : LPAREN VECTOR_SET expr arg_int expr RPAREN'
        vec, idx, val = p[3], p[4], p[5]
        assert IsSchIntNode(idx)
        p[0] = MakeSchVectorSetNode(vec, GetIntX(idx), val)

    def p_empty(p):
        'empty :'
        pass

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
    ; a test Scheme program using R2 grammar
    (let ([foo 43] [bar (- 1)] [x (vector (vector foo (void)) 42 #t)])
        (if #t (+ foo bar) (vector-ref x 1))
    )
    '''
    test_data = lexer.LexPreprocess(test_data)

    lexer = lexer.SchemeLexer()
    parser = SchemeParser()
    ast = parser.parse(test_data, lexer=lexer)
    print(SchSourceCode(ast))
