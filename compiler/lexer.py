from __future__ import print_function

import ply.lex as lex
import re
from ast.sch_ast import *

keywords = {
    'let': 'LET',
    'if': 'IF',
    'and': 'LOGICAL_OP',
    'or': 'LOGICAL_OP',
    'not': 'LOGICAL_OP',
    'void': 'VOID',
}
keywords.update({r: 'RTM_FN' for r in SchRtmFns()})

tokens = [
    'INT',  # Natural numbers
    'BOOL',
    'VAR',
    'ARITH_OP',
    'CMP_OP',
    'VECTOR_INIT',
    'VECTOR_REF',
    'VECTOR_SET',
    'DEFINE',
    'LAMBDA',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LINE_COMMENT',
    'BLK_COMMENT_BEGIN',
    'BLK_COMMENT',
    'BLK_COMMENT_END',
] + list(set(keywords.values()))

# 'blkc' for 'block comment'
_blkc_state = 'blkc'

states = [
    (_blkc_state, 'exclusive'),
]


class LexingError(Exception):
  pass


def LexPreprocess(source):
  # Important to have the following whitespace
  replace = {
      # BIN_CMP
      r'eq\?\s': '@eq  ',
      r'<\s': '@lt  ',
      r'<=\s': '@le  ',
      r'>\s': '@gt  ',
      r'>=\s': '@ge  ',
      # BOOL
      # \1: 't' or 'f'
      # \2: extra captured token, needs to be put back
      r'#([tf])(\s|\]|\))': r'#\1 \2',
      # vector operations
      r'vector\s': '@vector  ',
      r'vector-ref\s': '@vector-ref  ',
      r'vector-set!\s': '@vector-set  ',
      # functions and lambdas
      r'define\s': '@define  ',
      r'lambda\s': '@lambda  ',
  }

  for pat, repl in replace.iteritems():
    source = re.sub(pat, repl, source)
  return source


def SchemeLexer():
  t_ARITH_OP = r'\+|-'
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

  def t_BOOL(t):
    r'\#[tf]\s'  # valid bools are attached with a whitespace ' '
    t.value = t.value.rstrip()
    return t

  def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = keywords.get(t.value, 'VAR')
    return t

  def t_CMP_OP(t):
    r'@((eq)|([lg][et]))'
    m = {'@eq': 'eq?', '@lt': '<', '@le': '<=', '@gt': '>', '@ge': '>='}
    t.value = m[t.value]
    return t

  def t_VECTOR_INIT(t):
    r'@vector\s'  # valid vector op are attached with a whitespace ' '
    t.value = 'vector'
    return t

  def t_VECTOR_REF(t):
    r'@vector-ref\s'  # valid vector op are attached with a whitespace ' '
    t.value = 'vector-ref'
    return t

  def t_VECTOR_SET(t):
    r'@vector-set\s'  # valid vector op are attached with a whitespace ' '
    t.value = 'vector-set!'
    return t

  def t_DEFINE(t):
    r'@define\s'  # valid define is attached with a whitespace
    t.value = 'define'
    return t

  def t_LAMBDA(t):
    r'@lambda\s'  # valid lambda is attached with a whitespace
    t.value = 'lambda'
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

    ; The code might not be syntactically valid.
    (define (add foo bar) (+ foo bar))
    (let ([foo 36] (bar (vector 1 2 3)))
        (eq? (and #t 2) (vector-set! bar (void) (vector-ref bar 1))))
    )
    '''
  test_data = LexPreprocess(test_data)
  sc_lexer = SchemeLexer()
  sc_lexer.input(test_data)
  while True:
    tok = sc_lexer.token()
    if not tok:
      break
    print(tok)
