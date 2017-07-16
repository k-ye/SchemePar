from ast_utils import AstNodeBase

class IrNode(AstNodeBase):
    pass


class IrProgramNode(IrNode):
    def __init__(self):
        super(IrProgramNode, self).__init__()

        self._var_list = []
        self._stmt_list = []

    @property
    def type(self):
        return 'program'


class IrStmtNode(IrNode):
    pass

