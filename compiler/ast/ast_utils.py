from contextlib import contextmanager


class AstNodeBase(object):

    @property
    def type(self):
        raise NotImplementedError('type')

    def _source_code(self, builder):
        raise NotImplementedError('source_code')

    def source_code(self):
        builder = AstSourceCodeBuilder()
        self._source_code(builder)
        return builder.Build()


class AstSourceCodeBuilder(object):

    def __init__(self):
        self.Reset()

    def Reset(self):
        self._indent_lv = 0
        self._lines = []
        self.NewLine()

    @contextmanager
    def Indent(self, sz=2):
        self._indent_lv += sz
        try:
            yield
        finally:
            self._indent_lv -= sz

    def NewLine(self):
        self._lines.append(self._MakeIndent())

    def Append(self, s, append_whitespace=True):
        ws = ' ' if append_whitespace else ''
        self._lines[-1] = '{}{}{}'.format(self._lines[-1], s, ws)

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


def GenVarDefsSourceCode(var_list, builder, formatter):
    formatter.BeginVarDefs(builder)
    for var in var_list:
        formatter.AddVar(var, builder)
    formatter.EndVarDefs(builder)


def GenStmtsSourceCode(stmt_list, builder, formatter):
    formatter.BeginStmts(builder)
    for stmt in stmt_list:
        formatter.AddStmt(stmt, builder)
    formatter.EndStmts(builder)


def GenProgramSourceCode(var_list, stmt_list, builder, formatter=None):
    formatter = formatter or DefaultProgramFormatter()

    formatter.BeginProgram(builder)
    with builder.Indent():
        GenVarDefsSourceCode(var_list, builder, formatter)
        GenStmtsSourceCode(stmt_list, builder, formatter)
    formatter.EndProgram(builder)


def GenApplySourceCode(method, operand_list, builder):
    builder.Append('(')
    builder.Append(method)
    for operand in operand_list:
        operand._source_code(builder)
    builder.Append(')')
