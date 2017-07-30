# Grammar

## Scheme

- version: R1
- BNF (terminal symbols are all CAPITALIZED, while non-terminal symbols are all in lowercase)

```
scheme : expr

expr 
    : expr_int 
    | expr_bool
    | expr_var
    | ( apply_inner )
    | ( LET ( let_var_binds ) expr )
    | ( uni_bool_op expr )
    | ( bin_bool_op expr expr )
    | ( cmp_op expr expr )
    | ( IF expr expr expr )

# converts an int to an AST node
expr_int : INT 

# converts an boolean to an AST node
expr_bool : #t | #f

uni_bool_op : NOT

bin_bool_op : AND | OR

cmp_op : "eq?" | < | > | <= | >=

# converts a string to an AST node
expr_var : VAR

apply_inner
    : READ
    | MINUS expr
    | ADD expr expr

let_var_binds : ( let_var_list )

# let_var_list contains at least 1 var_def_pair
let_var_list : var_def_pair | var_def_pair let_var_list

var_def_pair : [ expr_var expr ]

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