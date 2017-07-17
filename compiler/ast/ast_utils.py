from contextlib import contextmanager


class AstNodeBase(object):

    @property
    def type(self):
        raise NotImplementedError('type')

    def _source_code(self, builder):
        raise NotImplementedError('source_code')

    def source_code(self):
        builder = _SourceCodeBuilder()
        self._source_code(builder)
        return builder.Build()


class _SourceCodeBuilder(object):

    def __init__(self):
        self._indent_lv = 0
        self._lines = []
        self.NewLine()

    @contextmanager
    def Indent(self):
        self._indent_lv += 2
        try:
            yield
        finally:
            self._indent_lv -= 2

    def NewLine(self):
        self._lines.append(self._MakeIndent())

    def Append(self, s):
        self._lines[-1] = '{}{} '.format(self._lines[-1], s)

    def Build(self):
        result = '\n'.join(self._lines)
        return result

    def _MakeIndent(self):
        return ''.join([' '] * self._indent_lv)


class DefaultProgramFormatter(object):

    def __init__(self, program_hdr='program', var_hdr='variables', stmt_hdr='statements'):
        self._program_hdr = program_hdr
        self._var_hdr = var_hdr
        self._stmt_hdr = stmt_hdr

    def BeginProgram(self, builder):
        builder.Append('( {}'.format(self._program_hdr))

    def EndProgram(self, builder):
        builder.NewLine()
        builder.Append(')')

    def BeginVarDefs(self, builder):
        builder.NewLine()
        builder.Append('# {}'.format(self._var_hdr))
        builder.NewLine()
        builder.Append('(')

    def AddVar(self, var, builder):
        var._source_code(builder)

    def EndVarDefs(self, builder):
        builder.Append(')')

    def BeginStmts(self, builder):
        builder.NewLine()
        builder.Append('# {}'.format(self._stmt_hdr))

    def AddStmt(self, stmt, builder):
        builder.NewLine()
        stmt._source_code(builder)

    def EndStmts(self, builder):
        pass


def GenProgramSourceCode(var_list, stmt_list, builder, formatter=None):
    if formatter is None:
        formatter = DefaultProgramFormatter()
    formatter.BeginProgram(builder)
    with builder.Indent():
        formatter.BeginVarDefs(builder)
        for var in var_list:
            formatter.AddVar(var, builder)
        formatter.EndVarDefs(builder)

        formatter.BeginStmts(builder)
        for stmt in stmt_list:
            formatter.AddStmt(stmt, builder)
        formatter.EndStmts(builder)
    formatter.EndProgram(builder)


class DefaultApplyFormatter(object):

    def __init__(self):
        self._method_set = False

    def BeginApply(self, builder):
        builder.Append('(')

    def SetMethod(self, method, builder):
        if self._method_set:
            raise RuntimeError("Method can only be set once")
        builder.Append(method)
        self._method_set = True

    def AddOperand(self, operand, builder):
        if not self._method_set:
            raise RuntimeError("Need to set method first")
        operand._source_code(builder)

    def EndApply(self, builder):
        builder.Append(')')


def GenApplySourceCode(method, operand_list, builder, formatter=None):
    if formatter is None:
        formatter = DefaultApplyFormatter()
    formatter.BeginApply(builder)
    formatter.SetMethod(method, builder)
    for operand in operand_list:
        formatter.AddOperand(operand, builder)
    formatter.EndApply(builder)
