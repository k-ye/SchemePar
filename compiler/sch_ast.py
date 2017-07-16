from ast_utils import AstNodeBase


class SchNode(AstNodeBase):
    pass


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
    def type(self):
        return 'int'

    @property
    def x(self):
        return self._x

    def _source_code(self, builder):
        builder.Append(self.x)


class SchVarNode(SchExprNode):

    def __init__(self, var):
        '''
        var: A string representing the variable name 
        '''
        super(SchVarNode, self).__init__()
        self._var = var

    @property
    def type(self):
        return 'var'

    @property
    def var(self):
        return self._var

    @var.setter
    def var(self, var):
        self._var = var

    def _source_code(self, builder):
        builder.Append(self.var)


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
    def type(self):
        return 'apply'

    @property
    def method(self):
        return self._method

    @property
    def arg_list(self):
        return self._arg_list

    def set_arg_list(self, arg_list):
        self._arg_list = arg_list

    def _source_code(self, builder):
        builder.Append('({}'.format(self.method))
        for a in self._arg_list:
            a._source_code(builder)
        builder.Append(')')


class SchLetNode(SchExprNode):

    def __init__(self, var_list, body):
        '''
        var_list: A list of 2-tuple, where #1 is an SchVarNode and #2 an SchExprNode
        body: An SchExprNode
        '''
        super(SchLetNode, self).__init__()
        self._var_list = var_list
        self._body = body

    @property
    def type(self):
        return 'let'

    @property
    def var_list(self):
        return self._var_list

    def set_var_list(self, var_list):
        self._var_list = var_list

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        self._body = body

    def _source_code(self, builder):
        builder.Append('(let')

        with builder.Indent():
            builder.NewLine()
            builder.Append('(')
            with builder.Indent():
                for var, var_init in self._var_list:
                    builder.NewLine()
                    builder.Append('[')
                    var._source_code(builder)
                    var_init._source_code(builder)
                    builder.Append(']')
            builder.NewLine()
            builder.Append(')')

            builder.NewLine()
            self._body._source_code(builder)
        builder.NewLine()
        builder.Append(')')


class SchProgramNode(SchNode):
    '''
    This wrapper node is still needed at the top level. It's
    used internally at parsing stage.
    '''

    def __init__(self, expr):
        '''
        expr: An SchExprNode
        '''
        super(SchProgramNode, self).__init__()
        self._expr = expr

    @property
    def type(self):
        return 'program'

    @property
    def program(self):
        return self._expr

    @program.setter
    def program(self, expr):
        self._expr = expr

    def _source_code(self, builder):
        self._expr._source_code(builder)
