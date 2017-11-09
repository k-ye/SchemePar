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

# # evaluate type that is inferenced.
# _P_INFER_EVAL_TYPE = 'infer_eval_type'


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
    SetProperty(node, NODE_P_VAR, var)
    return node


def MakeSchBoolNode(b):
    node = _MakeSchExprNode(BOOL_NODE_T)
    SetProperty(node, NODE_P_BOOL, b)
    return node


def IsBinLogicalOp(op):
    return op in {'and', 'or'}


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


def IsSchArithop(method):
    return method in {'+', '-'}


def IsSchCmpOp(method):
    return method in {'eq?', '<', '<=', '>', '>='}


def IsSchLogicalOp(method):
    return method in {'and', 'not', 'or'}


def IsSchRtmFn(method):
    # check for builtin runtime function
    return method in {'read', 'read_int', 'read_bool'}


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
        ParentOf(prg_body).type == EXPR_NODE_T, ParentOf(prg_body).type
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


def MakeSchIfNode(cond, then, els):
    node = _MakeSchExprNode(IF_NODE_T)
    SetProperty(node, IF_P_COND, cond)
    SetProperty(node, IF_P_THEN, then)
    SetProperty(node, IF_P_ELSE, els)
    return node


def IsSchIfNode(node):
    return LangOf(node) == SCH_LANG and TypeOf(node) == IF_NODE_T


def MakeSchVectorInitNode(arg_list):
    node = _MakeSchExprNode(VECTOR_INIT_NODE_T)
    SetProperty(node, P_ARG_LIST, arg_list)
    return node


def IsSchVectorInitNode(node):
    return LangOf(node) == SCH_LANG and TypeOf(node) == VECTOR_INIT_NODE_T


def MakeSchVectorRefNode(vec, idx):
    node = _MakeSchExprNode(VECTOR_REF_NODE_T)
    SetProperty(node, VECTOR_P_VEC, vec)
    SetProperty(node, VECTOR_P_INDEX, idx)
    return node


def IsSchVectorRefNode(node):
    return LangOf(node) == SCH_LANG and TypeOf(node) == VECTOR_REF_NODE_T


def MakeSchVectorSetNode(vec, idx, val):
    node = _MakeSchExprNode(VECTOR_SET_NODE_T)
    SetProperty(node, VECTOR_P_VEC, vec)
    SetProperty(node, VECTOR_P_INDEX, idx)
    SetProperty(node, VECTOR_SET_P_VAL, val)
    return node


def IsSchVectorSetNode(node):
    return LangOf(node) == SCH_LANG and TypeOf(node) == VECTOR_SET_NODE_T


def SchRtmFns():
    return ['read', 'read_int', 'read_bool', ]


class SchEvalTypes(object):
    INT = 'int'
    BOOL = 'bool'
    _rtm_types = {
        'read': INT,
        'read_int': INT,
        'read_bool': BOOL,
    }

    @staticmethod
    def RtmFnType(method):
        return SchEvalTypes._rtm_types[method]


_SCH_CMP_OPS = {'eq?', '<', '<=', '>', '>='}


def IsSchCmpOp(op):
    return op in _SCH_CMP_OPS

''' Scheme Ast Node Visitor
'''


class SchAstVisitorBase(object):

    def Visit(self, node):
        '''Do NOT override
        '''
        self._BeginVisit()
        visit_result = self._Visit(node)
        return self._EndVisit(node, visit_result)

    def _BeginVisit(self):
        '''Optional to override
        '''
        pass

    def _EndVisit(self, node, visit_result):
        '''Optional to override
        '''
        return visit_result

    def _Visit(self, node):
        '''Do NOT override
        '''
        assert LangOf(node) == SCH_LANG, LangOf(node)
        ndtype = TypeOf(node)
        result = None
        if ndtype == PROGRAM_NODE_T:
            result = self.VisitProgram(node)
        elif ndtype == APPLY_NODE_T:
            result = self.VisitApply(node)
        elif ndtype == SCH_LET_NODE_T:
            result = self.VisitLet(node)
        elif ndtype == IF_NODE_T:
            result = self.VisitIf(node)
        elif ndtype == VECTOR_INIT_NODE_T:
            result = self.VisitVectorInit(node)
        elif ndtype == VECTOR_REF_NODE_T:
            result = self.VisitVectorRef(node)
        elif ndtype == VECTOR_SET_NODE_T:
            result = self.VisitVectorSet(node)
        elif ndtype == INT_NODE_T:
            result = self.VisitInt(node)
        elif ndtype == VAR_NODE_T:
            result = self.VisitVar(node)
        elif ndtype == BOOL_NODE_T:
            result = self.VisitBool(node)
        else:
            raise RuntimeError("Unknown Scheme node type={}".format(ndtype))
        return result

    def VisitProgram(self, node):
        '''Override
        '''
        return node

    def VisitApply(self, node):
        '''Override
        '''
        return node

    def VisitLet(self, node):
        '''Override
        '''
        return node

    def VisitIf(self, node):
        '''Override
        '''
        return node

    def VisitVectorInit(self, node):
        '''Override
        '''
        return node

    def VisitVectorRef(self, node):
        '''Override
        '''
        return node

    def VisitVectorSet(self, node):
        '''Override
        '''
        return node

    def VisitInt(self, node):
        '''Override
        '''
        return node

    def VisitVar(self, node):
        '''Override
        '''
        return node

    def VisitBool(self, node):
        '''Override
        '''
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
        builder = self._builder
        builder.Append('( {}'.format(GetNodeMethod(node)))
        with builder.Indent():
            for expr in GetSchApplyExprList(node):
                builder.NewLine()
                self._Visit(expr)
        builder.NewLine()
        builder.Append(')')
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
                    with builder.Indent():
                        builder.NewLine()
                        self._Visit(var_init)
                    builder.NewLine()
                    builder.Append(']')
            builder.NewLine()
            builder.Append(')')
            builder.NewLine()
            let_body = GetSchLetBody(node)
            self._Visit(let_body)
        builder.NewLine()
        builder.Append(')')
        return node

    def VisitIf(self, node):
        builder = self._builder

        builder.Append('( if')
        with builder.Indent():
            builder.NewLine()
            builder.Append('; cond')
            builder.NewLine()
            self._Visit(GetIfCond(node))

            builder.NewLine()
            builder.Append('; then-branch')
            builder.NewLine()
            self._Visit(GetIfThen(node))

            builder.NewLine()
            builder.Append('; else-branch')
            builder.NewLine()
            self._Visit(GetIfElse(node))

        builder.NewLine()
        builder.Append(')')
        return node

    def VisitVectorInit(self, node):
        builder = self._builder
        builder.Append('( vector')
        with builder.Indent():
            for expr in GetNodeArgList(node):
                builder.NewLine()
                self._Visit(expr)
        builder.NewLine()
        builder.Append(')')
        return node

    def VisitVectorRef(self, node):
        builder = self._builder
        builder.Append('( vector-ref')
        with builder.Indent():
            builder.NewLine()
            self._Visit(GetVectorNodeVec(node))
            builder.NewLine()
            self._Visit(GetVectorNodeIndex(node))
        builder.NewLine()
        builder.Append(')')
        return node

    def VisitVectorSet(self, node):
        builder = self._builder
        builder.Append('( vector-set!')
        with builder.Indent():
            builder.NewLine()
            self._Visit(GetVectorNodeVec(node))
            builder.NewLine()
            self._Visit(GetVectorNodeIndex(node))
            builder.NewLine()
            self._Visit(GetVectorSetVal(node))
        builder.NewLine()
        builder.Append(')')
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


def SchSourceCode(node):
    visitor = _SchSourceCodeVisitor()
    return visitor.Visit(node)
