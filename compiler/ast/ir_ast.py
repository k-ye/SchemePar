from ast_utils import AstNodeBase


class IrNode(AstNodeBase):
    pass


class IrProgramNode(IrNode):

    def __init__(self, var_list, stmt_list):
        super(IrProgramNode, self).__init__()

        self._var_list = var_list
        self._stmt_list = stmt_list

    @property
    def type(self):
        return 'program'

    def _source_code(self, builder):
        builder.Append('( program')
        with builder.Indent():
            builder.NewLine()
            builder.Append('# variables def')
            builder.NewLine()
            builder.Append('(')
            for var in self._var_list:
                var._source_code(builder)
            builder.Append(')')
            builder.NewLine()
            builder.Append('# statements')
            for stmt in self._stmt_list:
                builder.NewLine()
                stmt._source_code(builder)
        builder.NewLine()
        builder.Append(')')


class IrStmtNode(IrNode):
    pass


class IrAssignNode(IrStmtNode):

    def __init__(self, var, expr):
        super(IrAssignNode, self).__init__()
        assert var.type == 'var'
        self._var = var
        self._expr = expr

    @property
    def type(self):
        return 'assign'

    @property
    def var(self):
        return self._var

    @property
    def expr(self):
        return self._expr

    def _source_code(self, builder):
        builder.Append('( assign')
        self.var._source_code(builder)
        self.expr._source_code(builder)
        builder.Append(')')
        

class IrReturnNode(IrStmtNode):

    def __init__(self, arg):
        '''
        arg: An IrIntNode or an IrVarNode
        '''
        super(IrReturnNode, self).__init__()
        assert IsIrArgNode(arg)
        self._arg = arg

    @property
    def type(self):
        return 'return'

    @property
    def arg(self):
        return self._arg

    def _source_code(self, builder):
        builder.Append('( return')
        self.arg._source_code(builder)
        builder.Append(')')


class IrExprNode(IrNode):
    pass


def IsIrArgNode(node):
    return isinstance(node, IrExprNode) and node.type in ['int', 'var']


class IrIntNode(IrExprNode):

    def __init__(self, x):
        '''
        x: A natural integer
        '''
        super(IrIntNode, self).__init__()
        self._x = x

    @property
    def type(self):
        return 'int'

    @property
    def x(self):
        return self._x

    def _source_code(self, builder):
        builder.Append(self.x)


class IrVarNode(IrExprNode):

    def __init__(self, var):
        '''
        var: A string representing the variable name 
        '''
        super(IrVarNode, self).__init__()
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


class IrApplyNode(IrExprNode):

    def __init__(self, method, arg_list):
        '''
        method: A string (for now, later on when we have expression that can 
                evaluate to applicable, i.e. lambda, we need to store a node)
        arg_list: A possibly empty list of (IrIntNode|IrVarNode)
        '''
        super(IrApplyNode, self).__init__()
        self._method = method
        # TODO: rename to *operand_list
        self.set_arg_list(arg_list)

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
        for a in arg_list:
            assert IsIrArgNode(a)
        self._arg_list = arg_list

    def _source_code(self, builder):
        builder.Append('({}'.format(self.method))
        for a in self._arg_list:
            a._source_code(builder)
        builder.Append(')')
