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
