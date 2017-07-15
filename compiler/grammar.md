'''R1 Grammar
scheme : (PROGRAM expr)

expr 
    : INT 
    | VAR 
    | (READ) 
    | (- expr) 
    | (+ expr expr) 
    | (LET (let_var_list) expr)

let_var_list 
    : [VAR expr] let_var_list
    | empty

'''