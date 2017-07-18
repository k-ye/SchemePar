from ast_utils import *


class InternalFormatter(object):

    def AddArg(self, t, var, builder):
        if t == 'deref':
            builder.Append('( {} {} {} )'.format(t, var[0], var[1]))
        else:
            builder.Append('( {} {} )'.format(t, var))

    def AddInstr(self, instr, operand_list, builder):
        GenApplySourceCode(instr, operand_list, builder)

    def FormatProgram(self, node, builder):
        program_fmt = DefaultProgramFormatter(stmt_hdr='instructions')
        GenProgramSourceCode(
            node.var_list, node.instr_list, builder, program_fmt)


class MacX86Formatter(object):

    def __init__(self):
        self.AddInstr = self._AddInstrDefault
        # self.AddInstr = self._AddInstrPretty

    def _Reg(self, reg):
        return '%' + reg

    def AddArg(self, t, var, builder):
        argstr = None
        if t == 'deref':
            reg, offset = var
            argstr = '{1}({0})'.format(self._Reg(reg), offset)
        elif t == 'int':
            argstr = '${}'.format(var)
        elif t == 'register':
            argstr = self._Reg(var)
        elif t == 'label':
            argstr = var
        else:
            raise RuntimeError('type={} var={}'.format(t, var))
        builder.Append(argstr, append_whitespace=False)

    def _Instr(self, instr):
        return instr + 'q'

    def _AddInstrDefault(self, instr, operand_list, builder):
        instr = '{0: <6}'.format(self._Instr(instr))
        builder.Append(instr)
        last_index = len(operand_list) - 1
        for i, op in enumerate(operand_list):
            op._source_code(builder)
            if i < last_index:
                builder.Append(',')

    def _AddInstrPretty(self, instr, operand_list, builder):
        last_index = len(operand_list) - 1
        fmtstrs, strs = ['{: <6} '], [self._Instr(instr)]
        for i, op in enumerate(operand_list):
            fs = '{: <16}'
            ops = op.source_code()
            if i < last_index:
                ops += ', '
            fmtstrs.append(fs)
            strs.append(ops)
        finalstr = ''.join(fmtstrs).format(*strs)
        builder.Append(finalstr)

    def FormatProgram(self, node, builder):
        builder.Reset()
        # beginning
        with builder.Indent(4):
            lines = [
                '.section    __TEXT,__text,regular,pure_instructions',
                '.macosx_version_min 10, 12',
                '.globl  _main',
                '.p2align    4, 0x90',
            ]
            for line in lines:
                builder.NewLine()
                builder.Append(line)
        builder.NewLine()
        builder.Append('_main:')

        # instructions
        program_fmt = DefaultProgramFormatter(stmt_hdr='instructions')
        with builder.Indent(4):
            GenStmtsSourceCode(node.instr_list, builder, program_fmt)

        # end
        builder.NewLine()
        builder.Append('.subsections_via_symbols')


class X86Node(AstNodeBase):

    def __init__(self, formatter=None):
        self.formatter = formatter

    @property
    def formatter(self):
        return self._formatter

    @formatter.setter
    def formatter(self, f):
        self._formatter = f or InternalFormatter()
        self._set_children_formatter()

    def _set_children_formatter(self):
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
    def stack_sz(self):
        return self._stack_sz

    @stack_sz.setter
    def stack_sz(self, val):
        self._stack_sz = val

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
        self.formatter.FormatProgram(self, builder)

    def _set_children_formatter(self):
        try:
            for var in self.var_list:
                var.formatter = self.formatter
            for instr in self.instr_list:
                instr.formatter = self.formatter
        except AttributeError:
            # This might be called by the base __init__, at which time neither
            # self._var_list nor self._instr_list exists.
            pass


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
        self.formatter.AddInstr(self.instr, self.operand_list, builder)

    def _set_children_formatter(self):
        try:
            for op in self.operand_list:
                op.formatter = self.formatter
        except AttributeError:
            # This might be called by the base __init__, at which time
            # self._operand_list does not exist yet.
            pass


class X86ArgNode(X86Node):

    def _arg_source_code(self, val, builder):
        self.formatter.AddArg(self.type, val, builder)


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
        self._arg_source_code(self.x, builder)
        # builder.Append('( int {} )'.format(self.x))


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
        self._arg_source_code(self.reg, builder)


class X86DerefNode(X86ArgNode):

    def __init__(self, reg, offset):
        '''
        reg: a string of the reigster name
        offset: an int
        '''
        super(X86DerefNode, self).__init__()
        self._reg = reg
        self._offset = offset

    @property
    def type(self):
        return 'deref'

    @property
    def reg(self):
        return self._reg

    @property
    def offset(self):
        return self._offset

    def _source_code(self, builder):
        # ugly but who cares :(
        self._arg_source_code((self.reg, self.offset), builder)


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
        self._arg_source_code(self.var, builder)


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
        self._arg_source_code(self.label, builder)
