from ast_utils import *


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

    @property
    def var_list(self):
        return self._var_list

    @property
    def instr_list(self):
        return self._instr_list

    @instr_list.setter
    def instr_list(self, val):
        self._instr_list = val

    def _source_code(self, builder):
        formatter = DefaultProgramFormatter(stmt_hdr='instructions')
        GenProgramSourceCode(
            self.var_list, self.instr_list, builder, formatter)


class X86InstrNode(X86Node):

    def __init__(self, instr, *operands):
        super(X86InstrNode, self).__init__()
        '''
        instr: a string of the instruction name
        operand_list: a list of X86ArgNode
        '''
        self._instr = instr
        self._operand_list = [o for o in operands]

    @property
    def type(self):
        return 'instr_{}'.format(self._instr)

    @property
    def instr(self):
        return self._instr

    @property
    def operand_list(self):
        return self._operand_list

    @operand_list.setter
    def operand_list(self, val):
        self._operand_list = val

    @property
    def arity(self):
        return len(self._operand_list)

    def _source_code(self, builder):
        GenApplySourceCode(self.instr, self.operand_list, builder)


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
        return self._x

    def _source_code(self, builder):
        builder.Append('( int {} )'.format(self.x))


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

    def _source_code(self, builder):
        builder.Append('( reg {} )'.format(self.reg))


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

    def _source_code(self, builder):
        builder.Append('( deref {} {} )'.format(self.reg, self.offset))


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

    def _source_code(self, builder):
        builder.Append('( _var {} )'.format(self.var))


class X86LabelNode(X86ArgNode):

    def __init__(self, label):
        '''
        bael: a string of the label name
        '''
        super(X86LabelNode, self).__init__()
        self._label = label

    @property
    def type(self):
        return 'label'

    @property
    def label(self):
        return self._label

    def _source_code(self, builder):
        builder.Append('( label {} )'.format(self.label))
