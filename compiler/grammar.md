# Grammar

## Scheme

- version: R2
- BNF (terminal symbols are all CAPITALIZED, while non-terminal symbols are all in lowercase)

```

r2 : ( 'program' expr )

expr 
    : arg 
    | ( method maybe_expr_list ) 
    | ( 'let' ( var_pair_list ) expr )
    | ( 'if' expr expr expr )

arg : int | id | '#t' | '#f'

method
    : cmp_op
    | arith_op
    | logical_op
    | _builtin_fn

cmp_op : 'eq?' | '<' | '<=' | '>' | '>='

arith_op : '+' | '-'

logical_op : 'and' | 'not' | 'or'

_builtin_fn : 'read'

maybe_expr_list
    : (empty)
    | expr maybe_expr_list

var_pair_list
    : var_pair
    | var_pair var_pair_list

var_pair : '[' id expr ']'
```

## IR

- version: C1
- There is no lexing/parsing for IR. We generate its AST from Scheme's AST directly in Flatten pass.
- BNF

```
c1 : ( 'program' stmt_list )

stmt
    : ( 'assign' var expr )
    | ( 'return' arg )
    | ( 'if' ( cmp arg arg ) 
                     ( stmt_list )
                     ( stmt_list ) )

stmt_list : stmt | stmt stmt_list

expr : arg | ( 'read' ) | ( '-' arg ) | ( '+' arg arg ) | ( 'not' arg ) | ( cmp arg arg )

cmp : 'eq?' | '<' | '<=' | '>' | '>='

arg : int | var | '#t' | '#f'
```

## X86 Assembly

- version: X0
- There is no lexing/parsing for X86 Assembly. We generate its AST from IR's AST directly.
- BNF

```
x86 : ( PROGRAM INT maybe_var_list instr_list )

maybe_var_list  # only used internally
    : empty
    | _var maybe_var_list

instr_list
    : instr
    | instr instr_list

instr
    : ( ADD arg arg )
    | ( SUB arg arg )
    | ( NEG arg )
    | ( MOV arg arg )
    | ( CALL LABEL )
    | ( PUSH arg )
    | ( POP arg )
    | ( RET )

arg 
    : INT
    | REGISTER
    | deref
    | _var # only used internally

deref
    : INT ( REGISTER )
    : MINUS INT ( REGISTER )

_var : VAR

```