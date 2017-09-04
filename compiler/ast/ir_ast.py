from base import *
from src_code_gen import *

''' IR specific
'''
IR_LANG = 'ir'

IR_ASSIGN_NODE_T = 'assign'
IR_RETURN_NODE_T = 'return'
IR_CMP_NODE_T = 'cmp'

_IR_ASSIGN_P_EXPR = 'expr'
_IR_RETURN_P_ARG = 'arg'
_IR_P_OP = 'op'
_IR_BINOP_P_LHS = 'lhs'
_IR_BINOP_P_RHS = 'rhs'

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


def MakeIrCmpNode(op, lhs, rhs):
    assert IsIrArgNode(lhs) and IsIrArgNode(rhs)
    node = _MakeIrExprNode(IR_CMP_NODE_T)
    SetProperty(node, _IR_P_OP, op)
    SetProperty(node, _IR_BINOP_P_LHS, lhs)
    SetProperty(node, _IR_BINOP_P_RHS, rhs)
    return node


def IsIrCmpNode(node):
    return LangOf(node) == IR_LANG and TypeOf(node) == IR_CMP_NODE_T


def GetIrCmpOp(node):
    assert IsIrCmpNode(node)
    return GetProperty(node, _IR_P_OP)


def SetIrCmpOp(node, op):
    assert IsIrCmpNode(node)
    SetProperty(node, _IR_P_OP, op)


def GetIrCmpLhs(node):
    assert IsIrCmpNode(node)
    return GetProperty(node, _IR_BINOP_P_LHS)


def SetIrCmpLhs(node, lhs):
    assert IsIrCmpNode(node)
    SetProperty(node, _IR_BINOP_P_LHS, lhs)


def GetIrCmpRhs(node):
    assert IsIrCmpNode(node)
    return GetProperty(node, _IR_BINOP_P_RHS)


def SetIrCmpRhs(node, rhs):
    assert IsIrCmpNode(node)
    SetProperty(node, _IR_BINOP_P_RHS, rhs)


def MakeIrIfNode(cond, then, els):
    assert IsIrCmpNode(cond)
    try:
        iter(then)
        iter(els)
    except TypeError:
        # not iterable
        raise RuntimeError('|then| or |els| not iterable')
    node = _MakeIrStmtNode(IF_NODE_T)
    SetProperty(node, IF_P_COND, cond)
    SetProperty(node, IF_P_THEN, then)
    SetProperty(node, IF_P_ELSE, els)
    return node


def IsIrIfNode(node):
    return LangOf(node) == IR_LANG and TypeOf(node) == IF_NODE_T


def MakeIrAssignNode(var, expr):
    assert LangOf(var) == IR_LANG and TypeOf(var) == VAR_NODE_T
    assert LangOf(expr) == IR_LANG
    node = _MakeIrStmtNode(IR_ASSIGN_NODE_T)
    SetProperties(node, {NODE_P_VAR: var, _IR_ASSIGN_P_EXPR: expr})
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


def IsIrProgramNode(node):
    return LangOf(node) == IR_LANG and TypeOf(node) == PROGRAM_NODE_T


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
    SetProperty(node, NODE_P_VAR, var)
    return node


def MakeIrBoolNode(b):
    node = _MakeIrArgNode(BOOL_NODE_T)
    SetProperty(node, NODE_P_BOOL, b)
    return node


def MakeIrApplyNode(method, arg_list):
    node = _MakeIrExprNode(APPLY_NODE_T)
    SetProperties(node, {P_METHOD: method, P_ARG_LIST: arg_list})
    return node


def IsIrApplyNode(node):
    return LangOf(node) == IR_LANG and TypeOf(node) == APPLY_NODE_T


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
        try:
            assert LangOf(node) == IR_LANG
        except AssertionError:
            import pdb
            pdb.set_trace()

        ndtype = TypeOf(node)
        result = None
        if ndtype == PROGRAM_NODE_T:
            result = self.VisitProgram(node)
        elif ndtype == IR_ASSIGN_NODE_T:
            result = self.VisitAssign(node)
        elif ndtype == IR_RETURN_NODE_T:
            result = self.VisitReturn(node)
        elif ndtype == IF_NODE_T:
            result = self.VisitIf(node)
        elif ndtype == IR_CMP_NODE_T:
            result = self.VisitCmp(node)
        elif ndtype == INT_NODE_T:
            result = self.VisitInt(node)
        elif ndtype == VAR_NODE_T:
            result = self.VisitVar(node)
        elif ndtype == BOOL_NODE_T:
            result = self.VisitBool(node)
        elif ndtype == APPLY_NODE_T:
            result = self.VisitApply(node)
        else:
            raise RuntimeError("Unknown Scheme node type={}".format(ndtype))
        return result

    def VisitProgram(self, node):
        return node

    def VisitApply(self, node):
        return node

    def VisitAssign(self, node):
        return node

    def VisitReturn(self, node):
        return node

    def VisitIf(self, node):
        return node

    def VisitCmp(self, node):
        return node

    def VisitInt(self, node):
        return node

    def VisitVar(self, node):
        return node

    def VisitBool(self, node):
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

    def VisitIf(self, node):
        builder = self._builder
        builder.Append('( if')
        with builder.Indent():
            builder.NewLine()
            # cond
            self._Visit(GetIfCond(node))
            # then branch
            builder.NewLine()
            builder.Append('# then')
            builder.NewLine()
            builder.Append('(')
            with builder.Indent():
                for stmt in GetIfThen(node):
                    builder.NewLine()
                    self._Visit(stmt)
            builder.NewLine()
            builder.Append(')')
            # else branch
            builder.NewLine()
            builder.Append('# else')
            builder.NewLine()
            builder.Append('(')
            with builder.Indent():
                for stmt in GetIfElse(node):
                    builder.NewLine()
                    self._Visit(stmt)
            builder.NewLine()
            builder.Append(')')
        builder.NewLine()
        builder.Append(')')
        return node

    def VisitCmp(self, node):
        self._builder.Append('( {}'.format(GetIrCmpOp(node)))
        self._Visit(GetIrCmpLhs(node))
        self._Visit(GetIrCmpRhs(node))
        self._builder.Append(')')
        return node

    def VisitInt(self, node):
        self._builder.Append(GetIntX(node))
        return node

    def VisitVar(self, node):
        self._builder.Append(GetNodeVar(node))
        return node

    def VisitBool(self, node):
        self._builder.Append(GetNodeBool(node))
        return node

    def VisitApply(self, node):
        method = GetNodeMethod(node)
        arg_list = GetNodeArgList(node)
        GenApplySourceCode(method, arg_list, self._builder, self._FakeVisit)
        return node


def IrSourceCode(node):
    visitor = _IrSourceCodeVisitor()
    return visitor.Visit(node)
