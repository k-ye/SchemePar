# Grammar

## Scheme

- version: R2
- BNF (terminal symbols are all CAPITALIZED, while non-terminal symbols are all in lowercase)

```
r2 : expr

expr
    : arg
    | '(' method maybe_expr_list ')'
    | '(' 'let' '(' let_var_bind_list ')' expr ')'
    | '(' 'if' expr expr expr ')'

arg : int | var | bool

method
    : arith_op
    | cmp_op
    | logical_op
    | rtm_fn

arith_op : '+' | '-'

cmp_op : 'eq?' | '<' | '<=' | '>' | '>='

logical_op : 'and' | 'not' | 'or'

maybe_expr_list
    : (empty)
    | expr maybe_expr_list

let_var_bind_list
    : var_bind_pair
    | var_bind_pair let_var_bind_list

var_bind_pair
    : '[' var expr ']'
    | '(' var expr ')'

```

## IR

- version: C0
- There is no lexing/parsing for IR. We generate its AST from Scheme's AST directly in Flatten pass.
- BNF

```
ir : ( PROGRAM ( maybe_var_list ) ( stmt_list ))

maybe_var_list
    : var maybe_var_list
    | empty

stmt_list 
    : stmt 
    | stmt stmt_list

stmt
    : ( ASSIGN var expr )
    | ( RETURN arg )

expr
    : arg
    | ( READ )
    | ( - arg )
    | ( + arg arg )

arg 
    : INT
    | var

var : VAR

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