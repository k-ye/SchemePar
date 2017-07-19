from base import *
from src_code_gen import *

''' Scheme specific
'''
SCH_LANG = 'scheme'
SCH_LET_NODE_T = 'let'

_SCH_LET_P_LET_BODY = 'let_body'
_SCH_PRG_P_PROGRAM = 'program'
_SCH_APPLY_P_EXPR_LIST = 'expr_list'

_NODE_TC = TypeChain(NODE_T, None)
_EXPR_TC = TypeChain(EXPR_NODE_T, _NODE_TC)


def _MakeSchNode(type, parent_tc):
    return MakeAstNode(type, parent_tc, SCH_LANG)


def _MakeSchExprNode(type):
    return _MakeSchNode(type, _EXPR_TC)


def MakeSchIntNode(x):
    node = _MakeSchExprNode(INT_NODE_T)
    SetProperty(node, INT_P_X, x)
    return node


def MakeSchVarNode(var):
    node = _MakeSchExprNode(VAR_NODE_T)
    SetProperty(node, VAR_P_VAR, var)
    return node


def MakeSchApplyNode(method, expr_list):
    node = _MakeSchExprNode(APPLY_NODE_T)
    SetProperties(node, {P_METHOD: method, _SCH_APPLY_P_EXPR_LIST: expr_list})
    return node


def GetSchApplyExprList(node):
    assert LangOf(node) == SCH_LANG and TypeOf(node) == APPLY_NODE_T
    return GetProperty(node, _SCH_APPLY_P_EXPR_LIST)


def SetSchApplyExprList(node, expr_list):
    assert LangOf(node) == SCH_LANG and TypeOf(node) == APPLY_NODE_T
    SetProperty(node, _SCH_APPLY_P_EXPR_LIST, expr_list)


def MakeSchLetNode(var_list, let_body):
    node = _MakeSchExprNode(SCH_LET_NODE_T)
    SetProperty(node, P_VAR_LIST, var_list)
    SetProperty(node, _SCH_LET_P_LET_BODY, let_body)
    return node


def GetSchLetBody(node):
    assert LangOf(node) == SCH_LANG and TypeOf(node) == SCH_LET_NODE_T
    return GetProperty(node, _SCH_LET_P_LET_BODY)


def SetSchLetBody(node, let_body):
    assert LangOf(node) == SCH_LANG and TypeOf(node) == SCH_LET_NODE_T
    SetProperty(node, _SCH_LET_P_LET_BODY, let_body)


def MakeSchProgramNode(prg_body):
    assert LangOf(prg_body) == SCH_LANG and \
        ParentOf(prg_body).type == EXPR_NODE_T
    node = _MakeSchNode(PROGRAM_NODE_T, _NODE_TC)
    SetProperty(node, _SCH_PRG_P_PROGRAM, prg_body)
    return node


def GetSchProgram(node):
    assert LangOf(node) == SCH_LANG and TypeOf(node) == PROGRAM_NODE_T
    return GetProperty(node, _SCH_PRG_P_PROGRAM)


def SetSchProgram(node, prg_body):
    assert LangOf(node) == SCH_LANG and TypeOf(node) == PROGRAM_NODE_T
    assert LangOf(prg_body) == SCH_LANG and \
        ParentOf(prg_body).type == EXPR_NODE_T
    SetProperty(node, _SCH_PRG_P_PROGRAM, prg_body)


''' Scheme Ast Node Visitor
'''


class SchAstVisitorBase(object):

    def Visit(self, node):
        self._BeginVisit()
        visit_result = self._Visit(node)
        return self._EndVisit(node, visit_result)

    def _BeginVisit(self):
        pass

    def _EndVisit(self, node, visit_result):
        return visit_result

    def _Visit(self, node):
        assert LangOf(node) == SCH_LANG
        ndtype = TypeOf(node)
        result = None
        if ndtype == PROGRAM_NODE_T:
            result = self.VisitProgram(node)
        elif ndtype == APPLY_NODE_T:
            result = self.VisitApply(node)
        elif ndtype == SCH_LET_NODE_T:
            result = self.VisitLet(node)
        elif ndtype == INT_NODE_T:
            result = self.VisitInt(node)
        elif ndtype == VAR_NODE_T:
            result = self.VisitVar(node)
        else:
            raise RuntimeError("Unknown Scheme node type={}".format(ndtype))
        return result

    def VisitProgram(self, node):
        return node

    def VisitApply(self, node):
        return node

    def VisitLet(self, node):
        return node

    def VisitInt(self, node):
        return node

    def VisitVar(self, node):
        return node


'''Build source code from a Scheme AST
'''


class _SchSourceCodeVisitor(SchAstVisitorBase):

    def __init__(self):
        super(_SchSourceCodeVisitor, self).__init__()

    def _BeginVisit(self):
        self._builder = AstSourceCodeBuilder()

    def _EndVisit(self, node, visit_result):
        return self._builder.Build()

    def VisitProgram(self, node):
        self._Visit(GetSchProgram(node))
        return node

    def VisitApply(self, node):
        return node

    def VisitLet(self, node):
        builder = self._builder

        builder.Append('( let')
        with builder.Indent():
            builder.NewLine()
            builder.Append('(')
            with builder.Indent():
                for var, var_init in GetNodeVarList(node):
                    builder.NewLine()
                    builder.Append('[')
                    self._Visit(var)
                    self._Visit(var_init)
                    builder.Append(']')
            builder.NewLine()
            builder.Append(')')
            builder.NewLine()
            let_body = GetSchLetBody(node)
            self._Visit(let_body)
        builder.NewLine()
        builder.Append(')')
        return node

    def VisitInt(self, node):
        self._builder.Append(GetIntX(node))
        return node

    def VisitVar(self, node):
        self._builder.Append(GetNodeVar(node))
        return node


def SchSourceCode(node):
    visitor = _SchSourceCodeVisitor()
    return visitor.Visit(node)