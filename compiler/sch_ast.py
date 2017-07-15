class SchNode(object):
    pass


class SchExprNode(SchNode):
    pass


class SchIntNode(SchExprNode):

    def __init__(self, x):
        '''
        x: A natural integer
        '''
        super(self, SchIntNode).__init__()
        self._x = x

    @property
    def x(self):
        return self._x


class SchVarNode(SchExprNode):

    def __init__(self, var):
        '''
        var: A string representing the variable name 
        '''
        super(self, SchVarNode).__init__()
        self._var = var

    @property
    def var(self):
        return self._var


class SchApplyNode(SchExprNode):

    def __init__(self, method, arg_list):
        '''
        method: A ?-node (or string for now?)
        arg_list: A possibly empty list of SchExprNodes
        '''
        super(self, SchApplyNode).__init__()
        self._method = method
        self._arg_list = arg_list


class SchLetNode(SchExprNode):

    def __init__(self, var_list, body):
        '''
        var_list: A list of 2-tuple, where #1 is an SchVarNode and #2 an SchExprNode
        body: An SchExprNode
        '''
        super(self, SchLetNode).__init__()
        self._var_list = var_list
        self._body = body


class SchProgramNode(SchNode):

    def __init__(self, expr):
        '''
        expr: An SchExprNode
        '''
        super(self, SchProgramNode).__init__()
        self._expr = expr

    @property
    def program(self):
        return self._expr
