from contextlib import contextmanager


class _SourceCodeMaker(object):

    def __init__(self):
        # indent level
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


class SchNode(object):

    def _source_code(self, maker):
        raise NotImplementedError('source_code')

    def source_code(self):
        maker = _SourceCodeMaker()
        self._source_code(maker)
        return maker.Build()


class SchExprNode(SchNode):
    pass


class SchIntNode(SchExprNode):

    def __init__(self, x):
        '''
        x: A natural integer
        '''
        super(SchIntNode, self).__init__()
        self._x = x

    @property
    def x(self):
        return self._x

    def _source_code(self, maker):
        maker.Append(self.x)


class SchVarNode(SchExprNode):

    def __init__(self, var):
        '''
        var: A string representing the variable name 
        '''
        super(SchVarNode, self).__init__()
        self._var = var

    @property
    def var(self):
        return self._var

    def _source_code(self, maker):
        maker.Append(self.var)


class SchApplyNode(SchExprNode):

    def __init__(self, method, arg_list):
        '''
        method: A string (for now, later on when we have expression that can 
                evaluate to applicable, i.e. lambda, we need to store a node)
        arg_list: A possibly empty list of SchExprNodes
        '''
        super(SchApplyNode, self).__init__()
        self._method = method
        self._arg_list = arg_list

    @property
    def method(self):
        return self._method

    def _source_code(self, maker):
        maker.Append('({}'.format(self.method))
        for a in self._arg_list:
            a._source_code(maker)
        maker.Append(')')


class SchLetNode(SchExprNode):

    def __init__(self, var_list, body):
        '''
        var_list: A list of 2-tuple, where #1 is an SchVarNode and #2 an SchExprNode
        body: An SchExprNode
        '''
        super(SchLetNode, self).__init__()
        self._var_list = var_list
        self._body = body

    def _source_code(self, maker):
        maker.Append('(let')

        with maker.Indent():
            maker.NewLine()
            maker.Append('(')
            with maker.Indent():
                for var, var_init in self._var_list:
                    maker.NewLine()
                    maker.Append('[')
                    var._source_code(maker)
                    var_init._source_code(maker)
                    maker.Append(']')
            maker.NewLine()
            maker.Append(')')

            maker.NewLine()
            self._body._source_code(maker)
        maker.NewLine()
        maker.Append(')')


class SchProgramNode(SchNode):

    def __init__(self, expr):
        '''
        expr: An SchExprNode
        '''
        super(SchProgramNode, self).__init__()
        self._expr = expr

    @property
    def program(self):
        return self._expr

    def _source_code(self, maker):
        maker.Append('(program')
        with maker.Indent():
            maker.NewLine()
            self._expr._source_code(maker)
        maker.NewLine()
        maker.Append(')')
