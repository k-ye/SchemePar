from __future__ import print_function

import ply.lex as lex

keywords = {
    'let': 'LET',
    'read': 'READ',
}

tokens = [
    'INT',  # Natural numbers
    'VAR',
    'ADD',
    'MINUS',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LINE_COMMENT',
    'BLK_COMMENT_BEGIN',
    'BLK_COMMENT',
    'BLK_COMMENT_END',
] + list(keywords.values())

_blkc_state = 'blkc'

states = [
    (_blkc_state, 'exclusive'),
]


class LexingError(Exception):
    pass


def SchemeLexer():
    t_ADD = r'\+'
    t_MINUS = r'-'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_ANY_ignore = ' \t'

    # Token lexer for 'INITIAL' state
    def t_INT(t):
        r'\d+'
        t.value = int(t.value)
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
        raise LexingError("Unknown character: {}".format(t.value[0]))

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
        (+ foo 6)
    )
    ; 42
    '''

    sc_lexer = SchemeLexer()
    sc_lexer.input(test_data)
    while True:
        tok = sc_lexer.token()
        if not tok:
            break
        print(tok)
