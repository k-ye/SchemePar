from base import *
from src_code_gen import *

''' IR specific
'''
IR_LANG = 'ir'

IR_ASSIGN_NODE_T = 'assign'
IR_RETURN_NODE_T = 'return'

_IR_ASSIGN_P_EXPR = 'expr'
_IR_RETURN_P_ARG = 'arg'

_NODE_TC = TypeChain(NODE_T, None)
_STMT_TC = TypeChain(STMT_NODE_T, _NODE_TC)
_EXPR_TC = TypeChain(EXPR_NODE_T, _NODE_TC)
_ARG_TC = TypeChain(ARG_NODE_T, _EXPR_TC)


def _MakeIrNode(type, parent_tc):
    return MakeAstNode(type, parent_tc, IR_LANG)


def _MakeIrStmtNode(type):
    return _MakeIrNode(type, _STMT_TC)


def _MakeIrExprNode(type):
    return _MakeIrNode(type, _EXPR_TC)


def _MakeIrArgNode(type):
    return _MakeIrNode(type, _ARG_TC)


def MakeIrAssignNode(var, expr):
    assert LangOf(var) == IR_LANG and TypeOf(var) == VAR_NODE_T
    assert LangOf(expr) == IR_LANG
    node = _MakeIrStmtNode(IR_ASSIGN_NODE_T)
    SetProperties(node, {VAR_P_VAR: var, _IR_ASSIGN_P_EXPR: expr})
    return node


def GetIrAssignExpr(node):
    assert LangOf(node) == IR_LANG and TypeOf(node) == IR_ASSIGN_NODE_T
    return GetProperty(node, _IR_ASSIGN_P_EXPR)


def SetIrAssignExpr(node, expr):
    assert LangOf(node) == IR_LANG and TypeOf(node) == IR_ASSIGN_NODE_T
    assert LangOf(expr) == IR_LANG
    SetProperty(node, _IR_ASSIGN_P_EXPR, expr)


def MakeIrReturnNode(arg):
    assert LangOf(arg) == IR_LANG and IsIrArgNode(arg)
    node = _MakeIrStmtNode(IR_RETURN_NODE_T)
    SetProperty(node, _IR_RETURN_P_ARG, arg)
    return node


def GetIrReturnArg(node):
    assert LangOf(node) == IR_LANG and TypeOf(node) == IR_RETURN_NODE_T
    return GetProperty(node, _IR_RETURN_P_ARG)


def SetIrReturnArg(node, arg):
    assert LangOf(node) == IR_LANG and TypeOf(node) == IR_RETURN_NODE_T
    assert LangOf(arg) == IR_LANG and IsIrArgNode(arg)
    SetProperty(node, _IR_RETURN_P_ARG, arg)


def MakeIrProgramNode(var_list, stmt_list):
    node = _MakeIrNode(PROGRAM_NODE_T, _NODE_TC)
    SetProperty(node, P_VAR_LIST, var_list)
    SetProperty(node, P_STMT_LIST, stmt_list)
    return node


def IsIrArgNode(node):
    if LangOf(node) != IR_LANG:
        return False
    try:
        # parent could be None
        return ParentOf(node).type == ARG_NODE_T
    except:
        return False


def MakeIrIntNode(x):
    node = _MakeIrArgNode(INT_NODE_T)
    SetProperty(node, INT_P_X, x)
    return node


def MakeIrVarNode(var):
    node = _MakeIrArgNode(VAR_NODE_T)
    SetProperty(node, VAR_P_VAR, var)
    return node


def MakeIrApplyNode(method, arg_list):
    node = _MakeIrExprNode(APPLY_NODE_T)
    SetProperties(node, {P_METHOD: method, P_ARG_LIST: arg_list})
    return node

''' IR Ast Node Visitor
'''


class IrAstVisitorBase(object):

    def Visit(self, node):
        self._BeginVisit()
        visit_result = self._Visit(node)
        return self._EndVisit(node, visit_result)

    def _BeginVisit(self):
        pass

    def _EndVisit(self, node, visit_result):
        return visit_result

    def _Visit(self, node):
        assert LangOf(node) == IR_LANG
        ndtype = TypeOf(node)
        result = None
        if ndtype == PROGRAM_NODE_T:
            result = self.VisitProgram(node)
        elif ndtype == IR_ASSIGN_NODE_T:
            result = self.VisitAssign(node)
        elif ndtype == IR_RETURN_NODE_T:
            result = self.VisitReturn(node)
        elif ndtype == INT_NODE_T:
            result = self.VisitInt(node)
        elif ndtype == VAR_NODE_T:
            result = self.VisitVar(node)
        elif ndtype == APPLY_NODE_T:
            result = self.VisitApply(node)
        else:
            raise RuntimeError("Unknown Scheme node type={}".format(ndtype))
        return result

    def VisitProgram(self, node):
        return node

    def VisitAssign(self, node):
        return node

    def VisitReturn(self, node):
        return node

    def VisitInt(self, node):
        return node

    def VisitVar(self, node):
        return node

    def VisitApply(self, node):
        return node


class _IrSourceCodeVisitor(IrAstVisitorBase):

    def __init__(self):
        super(_IrSourceCodeVisitor, self).__init__()

    def _BeginVisit(self):
        self._builder = AstSourceCodeBuilder()

    def _EndVisit(self, node, visit_result):
        return self._builder.Build()

    def _FakeVisit(self, node, builder):
        assert builder is self._builder
        return self._Visit(node)

    def VisitProgram(self, node):
        var_list = GetNodeVarList(node)
        stmt_list = GetNodeStmtList(node)
        GenProgramSourceCode(var_list, stmt_list,
                             self._builder, self._FakeVisit)
        return node

    def VisitAssign(self, node):
        self._builder.Append('( assign')
        self._Visit(GetNodeVar(node))
        self._Visit(GetIrAssignExpr(node))
        self._builder.Append(')')
        return node

    def VisitReturn(self, node):
        self._builder.Append('( return')
        self._Visit(GetIrReturnArg(node))
        self._builder.Append(')')
        return node

    def VisitInt(self, node):
        self._builder.Append(GetIntX(node))
        return node

    def VisitVar(self, node):
        self._builder.Append(GetNodeVar(node))
        return node

    def VisitApply(self, node):
        method = GetNodeMethod(node)
        arg_list = GetNodeArgList(node)
        GenApplySourceCode(method, arg_list, self._builder, self._FakeVisit)
        return node


def IrSourceCode(node):
    visitor = _IrSourceCodeVisitor()
    return visitor.Visit(node)
