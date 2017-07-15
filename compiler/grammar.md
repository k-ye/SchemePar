# Scheme Grammar

- version: R1
- BNF (terminal symbols are all CAPITALIZED, while non-terminal symbols are all in lowercase)

```
scheme : (PROGRAM expr)

expr 
    : expr_int 
    | expr_var
    | ( apply_inner )
    | ( LET ( let_var_binds ) expr )

# converts an int to an AST node
expr_int : INT 

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