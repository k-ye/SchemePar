from __future__ import print_function

import ply.lex as lex
import re

keywords = {
    'let': 'LET',
    'read': 'READ',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'if': 'IF',
}

tokens = [
    'INT',  # Natural numbers
    'BOOL',
    'VAR',
    'ADD',
    'MINUS',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'BIN_CMP',
    'LINE_COMMENT',
    'BLK_COMMENT_BEGIN',
    'BLK_COMMENT',
    'BLK_COMMENT_END',
] + list(keywords.values())

_blkc_state = 'blkc'

states = [
    (_blkc_state, 'exclusive'),
]

literals = ['+', '-', '(', ')', '[', ']']


class LexingError(Exception):
    pass


def LexPreprocess(source):
    # Important to have the following whitespace
    replace = {
        # BIN_CMP
        r'eq\?\s': '@eq ',
        r'<\s': '@lt ',
        r'<=\s': '@le ',
        r'>\s': '@gt ',
        r'>=\s': '@ge ',
        # BOOL
        # \1: 't' or 'f'
        # \2: extra captured token, needs to be put back
        r'#([tf])(\s|\]|\))': r'#\1 \2'
    }

    for pat, repl in replace.iteritems():
        source = re.sub(pat, repl, source)
    return source


def SchemeLexer():
    t_ADD = r'\+'
    t_MINUS = r'-'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_BIN_CMP = r'@((eq)|([lg][et]))'
    t_ANY_ignore = ' \t'

    # Token lexer for 'INITIAL' state
    def t_INT(t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_BOOL(t):
        r'\#[tf]\s'  # valid bools are attached with a ' '
        t.value = t.value.rstrip()
        return t

    def t_VAR(t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = keywords.get(t.value, 'VAR')
        return t

    def t_LINE_COMMENT(t):
        r';.*'
        pass

    # Token lexers for 'blkc' state
    def t_INITAL_BLK_COMMENT_BEGIN(t):
        r'\#!'
        t.lexer.begin(_blkc_state)

    def t_blkc_BLK_COMMENT_END(t):
        r'.*?!\#'
        t.lexer.begin('INITIAL')

    def t_blkc_eof(t):
        raise LexingError("EOF in block comments")

    def t_blkc_BLK_COMMENT(t):
        r'.+'
        pass

    # Token lexers for all states
    def t_ANY_newline(t):
        r'\n+'
        # Could match more than one '\n'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(t):
        raise LexingError("Unknown token={}".format(t.value))

    return lex.lex()

if __name__ == '__main__':
    test_data = '''
    ; a test scheme program using R1 grammar
    
    ; This is a line comment
    
    #! This is a block comment,
    with some nonsense characters:
    ~~ @ &^*{ ())} ?/|\
    !#

    #!0xff!!!0_o!^_^aaa!!!#
    #! #! #!!!!#

    (let  ([foo 36])
        (and #t 2)
    )
    ; 42
    '''
    test_data = LexPreprocess(test_data)
    sc_lexer = SchemeLexer()
    sc_lexer.input(test_data)
    while True:
        tok = sc_lexer.token()
        if not tok:
            break
        print(tok)
