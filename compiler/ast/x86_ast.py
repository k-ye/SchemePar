from ast_utils import AstNodeBase

'''
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
'''


class X86Node(AstNodeBase):
    pass


class X86ProgramNode(X86Node):

    def __init__(self, stack_sz, var_list, instr_list):
        '''
        stack_sz: an int
        var_list: a list of X86VarNode
        instr_list: a list of X86InstrNode
        '''
        super(X86ProgramNode, self).__init__()

        self._stack_sz = stack_sz
        self._var_list = var_list
        self._instr_list = instr_list

    @property
    def type(self):
        return 'program'


class X86InstrNode(X86Node):

    def __init__(self, instr, operand_list):
        super(X86InstrNode, self).__init__()
        '''
        instr: a string of the instruction name
        operand_list: a list of X86ArgNode
        '''
        self._instr = instr
        self._operand_list = operand_list

    @property
    def type(self):
        return 'instr_{}'.format(self._instr)

    @property
    def instr(self):
        return self._instr

    @property
    def operand_list(self):
        return self._operand_list


class X86ArgNode(X86Node):
    pass


class X86IntNode(X86ArgNode):

    def __init__(self, x):
        super(X86IntNode, self).__init__()
        self._x = x

    @property
    def type(self):
        return 'int'

    @property
    def x(self):
        return x


class X86RegNode(X86ArgNode):

    def __init__(self, reg):
        '''
        reg: a string of the reigster name
        '''
        super(X86RegNode, self).__init__()
        self._reg = reg

    @property
    def type(self):
        return 'register'

    @property
    def reg(self):
        return self._reg


class X86DerefNode(X86ArgNode):

    def __init__(self, reg, offs):
        '''
        reg: a string of the reigster name
        offs: an int
        '''
        super(X86DerefNode, self).__init__()
        self._reg = reg
        self._offs = offs

    @property
    def type(self):
        return 'deref'

    @property
    def reg(self):
        return self._reg

    @property
    def offset(self):
        return self._offs


class X86VarNode(X86ArgNode):

    def __init__(self, var):
        '''
        var: a string of the variable name
        '''
        super(X86VarNode, self).__init__()
        self._var = var

    @property
    def type(self):
        return 'var'

    @property
    def var(self):
        return self._var